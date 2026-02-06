import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Wealth Architecture Suite", page_icon="🏛️")

# --- CUSTOM CSS FOR WORLD-CLASS LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ Wealth Architecture Suite")
st.caption("Strategic Engineering for Wealth Protection and Creation")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Financial DNA")
    mode = st.radio("Primary Objective", ["Protect Wealth (Rich)", "Create Wealth (Poor)"])
    income = st.number_input("Monthly Income ($)", value=10000 if mode == "Protect Wealth (Rich)" else 3000)
    expenses = st.number_input("Monthly Expenses ($)", value=4000 if mode == "Protect Wealth (Rich)" else 2500)
    assets = st.number_input("Current Assets ($)", value=500000 if mode == "Protect Wealth (Rich)" else 1000)
    
    st.divider()
    st.subheader("Economic Variables")
    growth = st.slider("Expected Market Growth (%)", 0, 15, 8) / 100
    tax = st.slider("Tax Leakage (%)", 0, 50, 25) / 100
    inflation = st.slider("Inflation Rate (%)", 0, 15, 4) / 100

# --- THE CALCULATIONS (The "Logic Code") ---
real_rate = (growth - inflation) * (1 - tax)
monthly_surplus = income - expenses
wealth_projection = []
current_val = assets

for year in range(31): # 30-year projection
    wealth_projection.append(current_val)
    current_val = (current_val + (monthly_surplus * 12)) * (1 + real_rate)

# --- THE OUTPUT ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Annual Wealth 'Leakage' (Inflation/Tax)", f"${(assets * (tax + inflation)):,.2f}")
with col2:
    st.metric("30-Year Wealth Projection", f"${wealth_projection[-1]:,.2f}")

# --- THE CHART ---
fig = go.Figure()
fig.add_trace(go.Scatter(x=list(range(31)), y=wealth_projection, fill='tozeroy', line_color='#1f77b4'))
fig.update_layout(title="Wealth Accumulation Curve", xaxis_title="Years", yaxis_title="Net Worth ($)")
st.plotly_chart(fig, use_container_width=True)

st.success("This model uses First Principles math. It solves the problem of 'Financial Blindness'.")
