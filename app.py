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
    return inflation_loss, tax_loss, inflation_loss + tax_loss


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
        remaining_payment = monthly_payment

        for debt in debts:
            if debt["balance"] > 0 and remaining_payment > 0:
                pay = min(remaining_payment, debt["balance"])
                debt["balance"] -= pay
                remaining_payment -= pay

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

    st.divider()
    st.subheader("Time Horizon")
    years = st.slider("Projection Horizon (Years)", 5, 50, 30)

# =========================================================
# CORE PROJECTION ENGINE
# =========================================================
real_rate = (growth - inflation) * (1 - tax)
monthly_surplus = income - expenses

wealth_projection = []
current_val = assets

for year in range(years + 1):
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
st.caption("This assumes long-term disciplined investing and consistent contributions.")

redirect = st.checkbox("Redirect monthly cash from a liability to an asset")

monthly_redirect = st.number_input(
    "Monthly Amount to Redirect ($)",
    min_value=0,
    value=500,
    step=50
)

if redirect and monthly_redirect > 0:
    future_val = opportunity_cost(
        monthly_amount=monthly_redirect,
        annual_rate=growth * (1 - tax),
        years=years
    )
    st.metric(
        f"Value of Redirected Cash ({years} Years)",
        f"${future_val:,.2f}"
    )

# =========================================================
# DEBT ERADICATOR
# =========================================================
st.divider()
st.subheader("⚔️ Debt Eradicator")

method = st.radio("Payoff Strategy", ["Avalanche", "Snowball"])

st.markdown("### Enter Your Debts")

debts = []

for i in range(1, 4):
    col1, col2 = st.columns(2)
    with col1:
        balance = st.number_input(f"Debt {i} Balance ($)", min_value=0, value=0)
    with col2:
        rate = st.number_input(f"Debt {i} Interest Rate (%)", min_value=0.0, value=0.0) / 100

    if balance > 0 and rate > 0:
        debts.append({"balance": balance, "rate": rate})

monthly_payment = st.number_input(
    "Total Monthly Debt Payment ($)",
    min_value=0,
    value=1000,
    step=50
)

if debts and monthly_payment > 0:
    months_to_zero = debt_payoff(
        debts=debts,
        monthly_payment=monthly_payment,
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
    x=list(range(years + 1)),
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
