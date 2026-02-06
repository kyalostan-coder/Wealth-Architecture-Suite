import streamlit as st
import plotly.graph_objects as go

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
# FUNCTIONS — CORE ENGINE
# =========================================================
def calculate_annual_leakage(assets, tax_rate, inflation_rate):
    inflation_loss = assets * inflation_rate
    tax_loss = assets * tax_rate
    total = inflation_loss + tax_loss
    return inflation_loss, tax_loss, total


def opportunity_cost(monthly_amount, annual_rate, years):
    months = years * 12
    monthly_rate = annual_rate / 12
    value = 0
    for _ in range(months):
        value = (value + monthly_amount) * (1 + monthly_rate)
    return value


def debt_payoff(debts, monthly_payment, method="avalanche"):
    debts = sorted(
        debts,
        key=lambda x: x["balance"] if method == "snowball" else -x["rate"]
    )
    months = 0
    while any(d["balance"] > 0 for d in debts):
        for debt in debts:
            if debt["balance"] > 0:
                pay = min(monthly_payment, debt["balance"])
                debt["balance"] -= pay
                break
        for debt in debts:
            if debt["balance"] > 0:
                debt["balance"] *= (1 + debt["rate"] / 12)
        months += 1
    return months

# =========================================================
# SIDEBAR INPUTS
# =========================================================
with st.sidebar:
    st.header("Financial DNA")
    mode = st.radio("Primary Objective", ["Protect Wealth (Rich)", "Create Wealth (Poor)"])

    income = st.number_input(
        "Monthly Income ($)",
        value=10000 if mode == "Protect Wealth (Rich)" else 3000
    )
    expenses = st.number_input(
        "Monthly Expenses ($)",
        value=4000 if mode == "Protect Wealth (Rich)" else 2500
    )
    assets = st.number_input(
        "Current Assets ($)",
        value=500000 if mode == "Protect Wealth (Rich)" else 1000
    )

    st.divider()
    st.subheader("Economic Variables")
    growth = st.slider("Expected Market Growth (%)", 0, 15, 8) / 100
    tax = st.slider("Tax Leakage (%)", 0, 50, 25) / 100
    inflation = st.slider("Inflation Rate (%)", 0, 15, 4) / 100

# =========================================================
# CORE PROJECTION ENGINE
# =========================================================
real_rate = (growth - inflation) * (1 - tax)
monthly_surplus = income - expenses

wealth_projection = []
current_val = assets

for year in range(31):
    wealth_projection.append(current_val)
    current_val = (current_val + monthly_surplus * 12) * (1 + real_rate)

# =========================================================
# LEAKAGE DETECTOR
# =========================================================
infl_loss, tax_loss, total_leak = calculate_annual_leakage(
    assets, tax, inflation
)

st.subheader("🧯 Leakage Detector")

c1, c2, c3 = st.columns(3)
c1.metric("Inflation Loss / Year", f"${infl_loss:,.2f}")
c2.metric("Tax Drag / Year", f"${tax_loss:,.2f}")
c3.metric("Total Annual Leakage", f"${total_leak:,.2f}")

# =========================================================
# OPPORTUNITY COST ENGINE
# =========================================================
st.divider()
st.subheader("🚀 Opportunity Cost Engine")

redirect = st.checkbox("Redirect $500/month from a liability to an asset")

if redirect:
    future_val = opportunity_cost(
        monthly_amount=500,
        annual_rate=growth * (1 - tax),
        years=30
    )
    st.metric(
        "Value of Redirected Cash (30 Years)",
        f"${future_val:,.2f}"
    )

# =========================================================
# DEBT ERADICATOR
# =========================================================
st.divider()
st.subheader("⚔️ Debt Eradicator")

method = st.radio("Payoff Strategy", ["Avalanche", "Snowball"])

sample_debts = [
    {"balance": 5000, "rate": 0.24},
    {"balance": 12000, "rate": 0.12},
    {"balance": 8000, "rate": 0.18},
]

months_to_zero = debt_payoff(
    debts=sample_debts,
    monthly_payment=1000,
    method=method.lower()
)

st.metric("Months to Become Debt-Free", f"{months_to_zero} months")

# =========================================================
# WEALTH CHART
# =========================================================
st.divider()
st.subheader("📈 Wealth Accumulation Curve")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=list(range(31)),
    y=wealth_projection,
    fill="tozeroy",
    line=dict(color="#1f77b4")
))
fig.update_layout(
    xaxis_title="Years",
    yaxis_title="Net Worth ($)",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

st.success("This system uses first-principles math to eliminate financial blindness.")
