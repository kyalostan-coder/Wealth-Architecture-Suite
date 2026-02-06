import streamlit as st
import plotly.graph_objects as go
import plotly.express as px # Import Plotly Express
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
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "KES (KSh)": "KSh ",
    "INR (₹)": "₹",
    "NGN (₦)": "₦"
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
    if monthly_rate == 0:
        return monthly_amount * months
    return monthly_amount * ((1 + monthly_rate)**months - 1) / monthly_rate

def debt_payoff(debts, monthly_payment, method="avalanche"):
    debts = sorted(
        debts,
        key=lambda x: x["balance"] if method == "snowball" else -x["rate"]
    )
    months = 0
    while any(d["balance"] > 0 for d in debts) and months < 1000:
        remaining = monthly_payment
        for debt in debts:
            if debt["balance"] > 0 and remaining > 0:
                pay = min(remaining, debt["balance"])
                debt["balance"] -= pay
                remaining -= pay
        for debt in debts:
            if debt["balance"] > 0:
                debt["balance"] *= (1 + debt["rate"] / 12)
        months += 1
    return months

# =========================================================
# ECONOMIC DATA FETCHER (CBK)
# =========================================================
@st.cache_data
def get_cbk_data():
    url = "https://www.centralbank.go.ke"
    response = requests.get(url)
    content = BytesIO(response.content)

    try:
        # Use pandas read_excel to automatically detect and read the file
        df = pd.read_excel(content, engine="openpyxl")
    except Exception as e:
        # Fallback if automatic detection fails, returning default data
        st.error(f"Error reading CBK file: {e}")
        return {"inflation": 0.04, "interest": 0.12, "exchange": 150.0}

    latest = df.iloc[-1]
    return {
        "inflation": float(latest.get("Inflation Rate (%)", 4.0)) / 100,
        "interest": float(latest.get("91-day T-Bill Rate (%)", 12.0)) / 100,
        "exchange": float(latest.get("KES/USD", 150.0)),
    }

eco_data = get_cbk_data()

# =========================================================
# SIDEBAR INPUTS
# =========================================================
with st.sidebar:
    st.header("Financial DNA")

    currency_choice = st.selectbox("Currency", list(CURRENCIES.keys()))
    currency_symbol = CURRENCIES[currency_choice]

    mode = st.radio("Primary Objective", ["Protect Wealth (Rich)", "Create Wealth (Poor)"])

    income = st.number_input(f"Monthly Income ({currency_symbol})",
                             value=10000 if mode == "Protect Wealth (Rich)" else 3000)
    expenses = st.number_input(f"Monthly Expenses ({currency_symbol})",
                               value=4000 if mode == "Protect Wealth (Rich)" else 2500)
    assets = st.number_input(f"Current Assets ({currency_symbol})",
                             value=500000 if mode == "Protect Wealth (Rich)" else 1000)

    st.divider()
    st.subheader("Economic Variables (CBK + Manual)")
    st.metric("Inflation Rate (%)", f"{eco_data['inflation']*100:.2f}%")
    st.metric("Interest Rate (%)", f"{eco_data['interest']*100:.2f}%")
    st.metric("Exchange Rate (KES/USD)", f"{eco_data['exchange']:.2f}")

    # Manual inputs for variables CBK doesn’t publish
    growth = st.number_input("Expected Market Growth (%)", min_value=0.0, max_value=100.0, value=8.0, step=0.1) / 100
    tax = st.number_input("Tax Leakage (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1) / 100
    unemployment = st.number_input("Unemployment Rate (%)", min_value=0.0, max_value=100.0, value=6.0, step=0.1) / 100
    debt_gdp = st.number_input("Debt-to-GDP (%)", min_value=0.0, max_value=200.0, value=65.0, step=0.1) / 100

    st.divider()
    st.subheader("Time Horizon")
    years = st.number_input("Projection Horizon (Years)", min_value=1, max_value=100, value=30, step=1)

    st.subheader("View Mode")
    view_mode = st.radio("Cash Flow Display", ["Monthly", "Yearly"])

# =========================================================
# CORE PROJECTION ENGINE
# =========================================================
real_rate = (growth * (1 - tax)) - eco_data["inflation"]
monthly_surplus = income - expenses
display_surplus = monthly_surplus if view_mode == "Monthly" else monthly_surplus * 12

wealth_projection = []
current_val = assets
for _ in range(years + 1):
    wealth_projection.append(current_val)
    current_val = (current_val + monthly_surplus * 12) * (1 + real_rate)

# =========================================================
# WEALTH PROJECTION VISUALIZATION (New Section)
# =========================================================
st.divider()
st.subheader("📈 Wealth Projection")
# Create a DataFrame for Plotly
df_projection = pd.DataFrame({
    'Year': range(years + 1),
    'Wealth': wealth_projection
})
# Create an interactive Plotly line chart
fig = px.line(df_projection, x='Year', y='Wealth', title='Projected Wealth Over Time')
fig.update_traces(mode='lines+markers') # Add markers to the line
st.plotly_chart(fig, use_container_width=True)


# =========================================================
# LEAKAGE DETECTOR
# =========================================================
infl_loss, tax_loss, interest_drag, total_leak = calculate_annual_leakage(
    assets, tax, eco_data["inflation"], eco_data["interest"]
)

st.subheader("🧯 Leakage Detector")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Inflation Loss / Year", money(infl_loss))
c2.metric("Tax Drag / Year", money(tax_loss))
c3.metric("Interest Drag / Year", money(interest_drag))
c4.metric("Total Annual Leakage", money(total_leak))

# =========================================================
# CASH FLOW CLARITY
# =========================================================
st.divider()
st.subheader("💰 Cash Flow Clarity")
st.metric(f"Surplus ({view_mode})", money(display_surplus))

# =========================================================
# OPPORTUNITY COST ENGINE
# =========================================================
st.divider()
st.subheader("🚀 Opportunity Cost Engine")
redirect = st.checkbox(f"Redirect {view_mode.lower()} cash from a liability to an asset")
monthly_redirect = st.number_input(f"Monthly Amount to Redirect ({currency_symbol})", min_value=0, value=500, step=50)

if redirect and monthly_redirect > 0:
    future_val = opportunity_cost(
        monthly_amount=monthly_redirect if view_mode == "Monthly" else monthly_redirect / 12,
        annual_rate=growth * (1 - tax),
        years=years
    )
    st.metric(f"Value of Redirected Cash ({years} Years)", money(future_val))

# =========================================================
# DEBT ERADICATOR
# =========================================================
st.divider()
st.subheader("🪓 Debt Eradicator")

method = st.radio("Payoff Strategy", ["Avalanche", "Snowball"])
st.markdown("### Enter Your Debts")

debts = []
for i in range(1, 4):
    col1, col2 = st.columns(2)
    with col1:
        balance = st.number_input(f"Debt {i} Balance", value=0.0, step=100.0)
    with col2:
        rate = st.number_input(f"Debt {i} Rate (%)", value=0.0, step=0.1) / 100
    
    if balance > 0 and rate > 0:
        debts.append({"balance": balance, "rate": rate})
