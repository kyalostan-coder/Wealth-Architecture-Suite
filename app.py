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
# SIDEBAR INPUTS
# =========================================================
with st.sidebar:
    st.header("Financial DNA")

    currency_choice = st.selectbox("Currency", list(CURRENCIES.keys()))
    currency_symbol = CURRENCIES[currency_choice]

    mode = st.radio("Primary Objective", ["Protect Wealth (Rich)", "Create Wealth (Poor)"])

    income = st.number_input(
        f"Monthly Income ({currency_symbol})",
        value=10000 if mode == "Protect Wealth (Rich)" else 3000
    )
    expenses = st.number_input(
        f"Monthly Expenses ({currency_symbol})",
        value=4000 if mode == "Protect Wealth (Rich)" else 2500
    )
    assets = st.number_input(
        f"Current Assets ({currency_symbol})",
        value=500000 if mode == "Protect Wealth (Rich)" else 1000
    )

    st.divider()
    st.subheader("Economic Variables")
    growth = st.number_input("Expected Market Growth (%)", min_value=0.0, max_value=100.0, value=8.0, step=0.1) / 100
    tax = st.number_input("Tax Leakage (%)", min_value=0.0, max_value=100.0, value=25.0, step=0.1) / 100
    inflation = st.number_input("Inflation Rate (%)", min_value=0.0, max_value=100.0, value=4.0, step=0.1) / 100

    st.divider()
    st.subheader("Time Horizon")
    years = st.number_input("Projection Horizon (Years)", min_value=1, max_value=100, value=30, step=1)

    st.subheader("View Mode")
    view_mode = st.radio("Cash Flow Display", ["Monthly", "Yearly"])

# =========================================================
# CORE PROJECTION ENGINE
# =========================================================
real_rate = (growth - inflation) * (1 - tax)
monthly_surplus = income - expenses
display_surplus = monthly_surplus if view_mode == "Monthly" else monthly_surplus * 12

wealth_projection = []
current_val = assets

for _ in range(years + 1):
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
c1.metric("Inflation Loss / Year", money(infl_loss))
c2.metric("Tax Drag / Year", money(tax_loss))
c3.metric("Total Annual Leakage", money(total_leak))

# =========================================================
# CASH FLOW CLARITY
# =========================================================
st.divider()
st.subheader("💰 Cash Flow Clarity")

st.metric(
    f"Surplus ({view_mode})",
    money(display_surplus)
)

# =========================================================
# OPPORTUNITY COST ENGINE
# =========================================================
st.divider()
st.subheader("🚀 Opportunity Cost Engine")
st.caption("This assumes long-term disciplined investing and consistent contributions.")

redirect = st.checkbox(f"Redirect {view_mode.lower()} cash from a liability to an asset")

monthly_redirect = st.number_input(
    f"Monthly Amount to Redirect ({currency_symbol})",
    min_value=0,
    value=500,
    step=50
)

if redirect and monthly_redirect > 0:
    future_val = opportunity_cost(
        monthly_amount=monthly_redirect if view_mode == "Monthly" else monthly_redirect / 12,
        annual_rate=growth * (1 - tax),
        years=years
    )
    st.metric(
        f"Value of Redirected Cash ({years} Years)",
        money(future_val)
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
        balance = st.number_input(
            f"Debt {i} Balance ({currency_symbol})",
            min_value=0,
            value=0
        )
    with col2:
        rate = st.number_input(
            f"Debt {i} Interest Rate (%)",
            min_value=0.0,
            value=0.0,
            step=0.1
        ) / 100

    if balance > 0 and rate > 0:
        debts.append({"balance": balance, "rate": rate})

monthly_payment = st.number_input(
    f"Total Monthly Debt Payment ({currency_symbol})",
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
    yaxis_title=f"Net Worth ({currency_symbol})",
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

st.success("This system uses first-principles math to eliminate financial blindness.")
