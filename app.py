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
# LIVE OFFICIAL DATA FETCHING (CBK 2026)
# =========================================================
@st.cache_data(ttl=3600)
def get_official_cbk_data():
    url = "https://www.centralbank.go.ke"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # Latest 2026 Average Defaults
    data = {"inflation": 0.044, "interest": 0.076, "exchange": 129.0}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            tables = pd.read_html(response.text)
            for df in tables:
                # Convert table to string for keyword searching
                content = df.to_string().upper()
                
                # 1. Official Inflation
                if "INFLATION RATE" in content:
                    row = df[df[0].str.contains("Inflation Rate", case=False, na=False)]
                    data["inflation"] = float(row[1].values[0].split('%')[0]) / 100
                
                # 2. Risk-Free Rate (Prioritizing KESONIA for 2026)
                if "KESONIA" in content or "91-DAY T-BILL" in content:
                    keyword = "KESONIA" if "KESONIA" in content else "91-Day T-Bill"
                    row = df[df[0].str.contains(keyword, case=False, na=False)]
                    data["interest"] = float(row[1].values[0].split('%')[0]) / 100
                
                # 3. Exchange Rate
                if "US DOLLAR" in content:
                    row = df[df[0].str.contains("US DOLLAR", case=False, na=False)]
                    data["exchange"] = float(row[1].values[0])
        return data
    except:
        return data

eco_data = get_official_cbk_data()

# =========================================================
# SIDEBAR & INPUTS
# =========================================================
with st.sidebar:
    st.header("Financial DNA")
    symbol = "KSh "
    
    st.subheader("Live Economic Indicators")
    inf_rate = st.number_input("Official Inflation (%)", value=eco_data['inflation']*100) / 100
    risk_free = st.number_input("KESONIA / T-Bill Rate (%)", value=eco_data['interest']*100) / 100
    ex_rate = st.number_input("USD/KES Exchange", value=eco_data['exchange'])
    
    st.divider()
    income = st.number_input("Monthly Income", value=100000)
    expenses = st.number_input("Monthly Expenses", value=60000)
    assets = st.number_input("Current Net Worth", value=1000000)
    horizon = st.slider("Horizon (Years)", 1, 40, 15)

# =========================================================
# CALCULATIONS
# =========================================================
surplus = income - expenses
# Target 10% annual growth (typical diversified aggressive portfolio)
expected_growth = 0.10 
real_return = expected_growth - inf_rate

wealth_path = []
current = assets
for y in range(horizon + 1):
    wealth_path.append({"Year": y, "Wealth": current})
    current = (current + (surplus * 12)) * (1 + real_return)

df_wealth = pd.DataFrame(wealth_path)

# =========================================================
# DASHBOARD
# =========================================================
st.title("🏛️ Wealth Architecture Suite")
st.caption("Engineered for the Kenyan Economic Landscape (2026)")

# Top Level Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Purchasing Power Risk", f"{inf_rate*100:.2f}%", delta="High" if inf_rate > 0.05 else "Stable")
m2.metric("Risk-Free Benchmark", f"{risk_free*100:.2f}%", help="Current KESONIA/T-Bill rate")
m3.metric("Annual Investable Surplus", f"{symbol}{surplus*12:,.0f}")

# Wealth Leakage Logic
st.divider()
st.subheader("🧯 Wealth Leakage Analysis")
inf_loss = assets * inf_rate
tax_drag = (assets * expected_growth) * 0.10 # Assuming 10% Withholding Tax

c1, c2 = st.columns(2)
with c1:
    st.error(f"**Inflation Leakage:** -{symbol}{inf_loss:,.2f} / year")
    st.caption("This is the 'Invisible Tax' on your idle cash.")
with c2:
    st.warning(f"**Estimated Tax Drag:** -{symbol}{tax_drag:,.2f} / year")
    st.caption("Projected withholding tax on investment gains.")

# Projection Chart
st.divider()
st.subheader("📈 Real Wealth Projection (Inflation Adjusted)")

fig = px.area(df_wealth, x="Year", y="Wealth", title="Wealth Growth Strategy")
fig.update_layout(yaxis_title=f"Net Worth ({symbol})", xaxis_title="Years from Today")
st.plotly_chart(fig, use_container_width=True)

st.success(f"Strategy: To maintain wealth, your portfolio must return at least {inf_rate*100:.2f}% annually just to break even.")
