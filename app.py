import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Wealth Architecture Suite", page_icon="🏛️", layout="wide")

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
.main { background-color: #f5f7f9; }
.stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("🏛️ Wealth Architecture Suite")
st.caption("Strategic Engineering for Wealth Protection and Creation")

# =========================================================
# CURRENCY CONFIG
# =========================================================
CURRENCIES = {
    "USD ($)": "$", "EUR (€)": "€", "GBP (£)": "£",
    "KES (KSh)": "KSh ", "INR (₹)": "₹", "NGN (₦)": "₦"
}

# =========================================================
# FUNCTIONS — CORE ENGINE
# =========================================================
def money(value):
    return f"{currency_symbol}{value:,.2f}"

def calculate_annual_leakage(assets, tax_rate, inflation_rate, interest_rate=0.0):
    inflation_loss = assets * inflation_rate
    tax_loss = assets * tax_rate
    interest_drag = assets * interest_rate
    return inflation_loss, tax_loss, interest_drag, inflation_loss + tax_loss + interest_drag

def opportunity_cost(monthly_amount, annual_rate, years):
    months = years * 12
    monthly_rate = annual_rate / 12
    if monthly_rate == 0: return monthly_amount * months
    return monthly_amount * ((1 + monthly_rate)**months - 1) / monthly_rate

# =========================================================
# UNIVERSAL FILE LOADER (Fixes the "Not a Zip" Error)
# =========================================================
def load_economic_data(uploaded_file):
    # Default values if no file is uploaded
    defaults = {"inflation": 0.05, "interest": 0.12, "exchange": 129.0}
    
    if uploaded_file is None:
        return defaults

    try:
        fname = uploaded_file.name.lower()
        if fname.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif fname.endswith(('.xlsx', '.xls')):
            # read_excel works here because we know it's a real Excel file
            df = pd.read_excel(uploaded_file)
        elif fname.endswith(('.html', '.htm')):
            # Properly handles HTML tables (like a saved CBK page)
            tables = pd.read_html(uploaded_file)
            df = tables[0]
        elif fname.endswith('.json'):
            df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format.")
            return defaults

        # Normalize column names for flexible searching
        df.columns = [str(c).strip().lower() for c in df.columns]
        latest = df.iloc[-1]

        # Helper to find columns by keyword
        def get_val(keyword, default):
            cols = [c for c in df.columns if keyword in c]
            if cols:
                val = str(latest[cols[0]]).replace('%', '')
                return float(val) / 100 if keyword != 'kes' else float(val)
            return default

        return {
            "inflation": get_val("inflation", defaults["inflation"]),
            "interest": get_val("interest", defaults["interest"]),
            "exchange": get_val("kes", defaults["exchange"])
        }
    except Exception as e:
        st.error(f"Error parsing file: {e}")
        return defaults

# =========================================================
# SIDEBAR INPUTS
# =========================================================
with st.sidebar:
    st.header("Financial DNA")
    
    # Data Input Method
    data_source = st.radio("Economic Data Source", ["Manual/Default", "Upload File"])
    
    if data_source == "Upload File":
        uploaded_file = st.file_uploader("Upload CSV, Excel, or HTML", type=["csv", "xlsx", "xls", "html", "json"])
        eco_data = load_economic_data(uploaded_file)
    else:
        eco_data = {"inflation": 0.05, "interest": 0.12, "exchange": 129.0}

    currency_choice = st.selectbox("Currency", list(CURRENCIES.keys()))
    currency_symbol = CURRENCIES[currency_choice]

    mode = st.radio("Primary Objective", ["Protect Wealth (Rich)", "Create Wealth (Poor)"])

    income = st.number_input(f"Monthly Income ({currency_symbol})", value=10000 if mode == "Protect Wealth (Rich)" else 3000)
    expenses = st.number_input(f"Monthly Expenses ({currency_symbol})", value=4000 if mode == "Protect Wealth (Rich)" else 2500)
    assets = st.number_input(f"Current Assets ({currency_symbol})", value=500000 if mode == "Protect Wealth (Rich)" else 1000)

    st.divider()
    st.subheader("Economic Variables")
    
    # Allow manual override even if file is uploaded
    inf_rate = st.number_input("Inflation Rate (%)", value=eco_data['inflation']*100) / 100
    int_rate = st.number_input("Interest Rate (%)", value=eco_data['interest']*100) / 100
    exc_rate = st.number_input("Exchange Rate (Local/USD)", value=eco_data['exchange'])

    growth = st.number_input("Expected Market Growth (%)", value=8.0) / 100
    tax = st.number_input("Tax Leakage (%)", value=25.0) / 100
    years = st.number_input("Projection Horizon (Years)", min_value=1, max_value=100, value=20)
    view_mode = st.radio("Cash Flow Display", ["Monthly", "Yearly"])

# =========================================================
# PROJECTION LOGIC
# =========================================================
real_rate = (growth * (1 - tax)) - inf_rate
monthly_surplus = income - expenses
display_surplus = monthly_surplus if view_mode == "Monthly" else monthly_surplus * 12

wealth_projection = []
current_val = assets
for _ in range(years + 1):
    wealth_projection.append(max(0, current_val))
    current_val = (current_val + monthly_surplus * 12) * (1 + real_rate)

# =========================================================
# UI DISPLAY
# =========================================================
# 1. Leakage Detector
st.subheader("🧯 Leakage Detector")
infl_loss, tax_loss, interest_drag, total_leak = calculate_annual_leakage(assets, tax, inf_rate, int_rate)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Inflation Loss/Yr", money(infl_loss))
c2.metric("Tax Drag/Yr", money(tax_loss))
c3.metric("Interest Drag/Yr", money(interest_drag))
c4.metric("Total Annual Leakage", money(total_leak))

# 2. Wealth Chart
st.divider()
st.subheader("📈 Wealth Projection")
df_projection = pd.DataFrame({'Year': range(years + 1), 'Wealth': wealth_projection})
fig = px.line(df_projection, x='Year', y='Wealth', title=f'Wealth Forecast over {years} Years')
fig.update_traces(line_color='#2ecc71', fill='tozeroy') 
st.plotly_chart(fig, use_container_width=True)

# 3. Opportunity Cost
st.divider()
st.subheader("🚀 Opportunity Cost Engine")
col_a, col_b = st.columns(2)
with col_a:
    monthly_redirect = st.number_input(f"Monthly Amount to Redirect ({currency_symbol})", value=500)
with col_b:
    future_val = opportunity_cost(monthly_redirect, growth * (1-tax), years)
    st.metric(f"Value of Redirected Cash ({years} Years)", money(future_val))

st.success("Analysis Complete. Adjust parameters in the sidebar to stress-test your strategy.")
