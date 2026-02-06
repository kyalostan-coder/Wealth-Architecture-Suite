import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# =========================================================
# 1. PAGE SETUP
# =========================================================
st.set_page_config(page_title="Wealth Reality Suite", layout="wide")

# Professional Dashboard Styling
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 24px; color: #2ecc71; }
    .main { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. SIDEBAR - REALISTIC INPUTS
# =========================================================
with st.sidebar:
    st.title("🛠️ Project Parameters")
    
    st.subheader("Monthly Cash Flow")
    monthly_savings = st.number_input("Monthly Savings (KSh)", value=20000, step=1000)
    initial_capital = st.number_input("Starting Balance (KSh)", value=0)
    
    st.subheader("Market Expectations")
    # Realistically, MMFs in Kenya range from 12-16%
    annual_yield = st.slider("Annual Yield (%)", 0.0, 20.0, 15.0) / 100
    inflation = st.slider("Inflation Rate (%)", 0.0, 10.0, 5.0) / 100
    
    years = st.number_input("Timeline (Years)", min_value=1, value=5)

# =========================================================
# 3. THE "REALITY CHECK" ENGINE
# =========================================================
# Using the Future Value of an Annuity Formula
# FV = PMT * (((1 + r/n)^(nt) - 1) / (r/n))
def calculate_growth(pmt, r, t, pv):
    months = t * 12
    monthly_rate = r / 12
    if monthly_rate == 0:
        return [pv + (pmt * m) for m in range(months + 1)]
    
    balances = []
    for m in range(months + 1):
        # Compound the initial balance + the monthly contributions
        val = pv * (1 + monthly_rate)**m + pmt * (((1 + monthly_rate)**m - 1) / monthly_rate)
        balances.append(val)
    return balances

# Calculations
raw_balances = calculate_growth(monthly_savings, annual_yield, years, initial_capital)
total_deposited = initial_capital + (monthly_savings * years * 12)
final_wealth = raw_balances[-1]
interest_earned = final_wealth - total_deposited

# =========================================================
# 4. DASHBOARD LAYOUT
# =========================================================
st.title("🏛️ Wealth Architecture Suite")
st.info(f"Goal: See how long it actually takes to hit KSh 1,000,000 with KSh {monthly_savings:,.0f}/month.")

# KPI Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Final Balance", f"KSh {final_wealth:,.0f}")
c2.metric("Total Deposits", f"KSh {total_deposited:,.0f}")
c3.metric("Interest Gained", f"KSh {interest_earned:,.0f}")
c4.metric("Real Yield (Adj.)", f"{(annual_yield - inflation)*100:.1f}%")

# Realistic Analysis
st.divider()
col_left, col_right = st.columns([2, 1])

with col_left:
    # Charting the path
    df = pd.DataFrame({
        "Month": range(len(raw_balances)),
        "Wealth": raw_balances,
        "Deposits": [initial_capital + (monthly_savings * m) for m in range(len(raw_balances))]
    })
    
    fig = px.area(df, x="Month", y=["Wealth", "Deposits"], 
                  title="Wealth vs. Pure Savings",
                  labels={"value": "Amount (KSh)", "variable": "Type"},
                  color_discrete_sequence=['#2ecc71', '#bdc3c7'])
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("The 1 Million Milestone")
    # Finding when we hit 1M
    months_to_1m = next((i for i, v in enumerate(raw_balances) if v >= 1000000), None)
    
    if months_to_1m:
        st.success(f"✔️ You hit 1 Million in **{months_to_1m} months**")
        st.write(f"That's approximately **{months_to_1m/12:.1f} years**.")
    else:
        st.error("❌ You won't hit 1 Million in this timeframe.")
        st.write("Try increasing the years or your monthly savings.")

st.warning("⚠️ **Reality Check:** To hit 1M in exactly 12 months with 0 starting balance, you would need to save roughly **KSh 78,000 per month** at 15% interest.")
