import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from io import BytesIO

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="Wealth Architecture Suite", page_icon="🏛️", layout="wide")

# =========================================================
# LIVE OFFICIAL DATA FETCHING (CBK)
# =========================================================
@st.cache_data(ttl=3600)  # Refresh data every hour
def get_official_cbk_data():
    """
    Scrapes official data from the Central Bank of Kenya website.
    """
    url = "https://www.centralbank.go.ke"
    # Headers are necessary to prevent the website from blocking the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Fallback default values
    data = {"inflation": 0.045, "interest": 0.076, "exchange": 129.0}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # pd.read_html looks for <table> tags in the website HTML
            tables = pd.read_html(response.text)
            
            for df in tables:
                df_content = df.to_string()
                
                # Extract Inflation
                if "Inflation Rate" in df_content:
                    # Finds the row with Inflation and gets the next column value
                    row = df[df[0].str.contains("Inflation Rate", na=False)]
                    data["inflation"] = float(row[1].values[0].replace('%', '')) / 100
                
                # Extract 91-Day T-Bill (Risk-free interest rate)
                if "91-Day T-Bill" in df_content:
                    row = df[df[0].str.contains("91-Day T-Bill", na=False)]
                    data["interest"] = float(row[1].values[0].replace('%', '')) / 100
                
                # Extract USD Exchange Rate
                if "US DOLLAR" in df_content:
                    # Usually found in the 'Daily KES Exchange Rates' table
                    row = df[df[0].str.contains("US DOLLAR", na=False)]
                    data["exchange"] = float(row[1].values[0])
                    
        return data
    except Exception as e:
        # If the website structure changes or is down, we use safety defaults
        return data

# Load the data
eco_data = get_official_cbk_data()

# =========================================================
# UI STYLING & SIDEBAR
# =========================================================
st.markdown("""
<style>
.main { background-color: #f5f7f9; }
.stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ Wealth Architecture Suite")
st.caption("Strategic Engineering for Wealth Protection and Creation — Live CBK Data Sync")

with st.sidebar:
    st.header("Financial DNA")
    
    # Currency Settings
    CURRENCIES = {"USD ($)": "$", "KES (KSh)": "KSh ", "EUR (€)": "€", "GBP (£)": "£"}
    currency_choice = st.selectbox("Currency", list(CURRENCIES.keys()))
    symbol = CURRENCIES[currency_choice]

    st.divider()
    st.subheader("Official Economic Rates")
    # Users can see official rates and tweak them if they have better local data
    inf_rate = st.number_input("Inflation (%)", value=eco_data['inflation']*100, step=0.01) / 100
    int_rate = st.number_input("91-Day T-Bill (%)", value=eco_data['interest']*100, step=0.01) / 100
    ex_rate = st.number_input("USD/KES Exchange", value=eco_data['exchange'])
    
    st.divider()
    mode = st.radio("Objective", ["Wealth Creation", "Wealth Protection"])
    income = st.number_input(f"Monthly Income ({symbol})", value=50000)
    expenses = st.number_input(f"Monthly Expenses ({symbol})", value=30000)
    assets = st.number_input(f"Starting Assets ({symbol})", value=100000)
    years = st.slider("Time Horizon (Years)", 1, 40, 20)

# =========================================================
# CORE MATH & LOGIC
# =========================================================
def money(val): return f"{symbol}{val:,.2f}"

monthly_surplus = income - expenses
growth_rate = 0.10  # Assumed market growth (e.g., S&P 500 or NSE Index)
real_return_rate = growth_rate - inf_rate

# Calculate Projection
wealth_data = []
current_wealth = assets
for year in range(years + 1):
    wealth_data.append({"Year": year, "Wealth": current_wealth})
    current_wealth = (current_wealth + (monthly_surplus * 12)) * (1 + real_return_rate)

df_wealth = pd.DataFrame(wealth_data)

# =========================================================
# DASHBOARD LAYOUT
# =========================================================
# Metric Row
c1, c2, c3 = st.columns(3)
c1.metric("Official Inflation", f"{inf_rate*100:.2f}%", help="Pulled from CBK")
c2.metric("Official T-Bill Rate", f"{int_rate*100:.2f}%", help="91-Day benchmark")
c3.metric("Monthly Surplus", money(monthly_surplus))

# Leakage Section
st.divider()
st.subheader("🧯 Wealth Leakage (Annual)")
col1, col2 = st.columns(2)
annual_inf_loss = assets * inf_rate
opp_cost_lost = (monthly_surplus * 12) * growth_rate

with col1:
    st.write(f"**Inflation Erosion:** {money(annual_inf_loss)}")
    st.caption("The amount of purchasing power your idle cash loses every year.")
with col2:
    st.write(f"**Uninvested Opportunity Cost:** {money(opp_cost_lost)}")
    st.caption("Potential gains lost if your surplus isn't put into productive assets.")

# Visualization
st.divider()
st.subheader("📈 Wealth Trajectory (Adjusted for Inflation)")
fig = px.area(df_wealth, x="Year", y="Wealth", title="Wealth Projection")
fig.update_traces(line_color='#1f77b4')
st.plotly_chart(fig, use_container_width=True)

st.info("💡 Tip: If your 'Real Return Rate' is negative (Inflation > Growth), your line will curve downwards. Focus on assets that outpace official inflation.")
