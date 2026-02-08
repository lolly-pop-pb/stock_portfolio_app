# portfolio_risk_app/pages/1_Risk_Overview.py
"""
Page 1: Risk Overview
Quantifies short-term portfolio downside risk.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from utils.portfolio import Portfolio
from utils.data_loader import fetch_multiple_stocks, get_current_prices
from utils.risk_metrics import calculate_portfolio_returns, portfolio_value_at_risk, portfolio_cvar
from utils.simulation import simulate_portfolio_outcomes, calculate_simulation_statistics
from utils.explain import explain_var, assess_risk_level, explain_simulation_outcomes
from assets.styles import format_currency, get_risk_color, get_risk_emoji

st.set_page_config(page_title="Risk Overview", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        color: #1f4788;
        font-weight: bold;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #34495e;
        margin-bottom: 2rem;
    }
    .metric-box {
        background-color: #ecf0f1;
        padding: 1.5rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .risk-high {
        background-color: #fadbd8;
        border-left: 4px solid #e74c3c;
    }
    .risk-moderate {
        background-color: #fcf3cf;
        border-left: 4px solid #f39c12;
    }
    .risk-low {
        background-color: #d5f4e6;
        border-left: 4px solid #27ae60;
    }
</style>
""", unsafe_allow_html=True)

# Check if portfolio exists
if 'portfolio' not in st.session_state or st.session_state.portfolio.is_empty():
    st.warning("⚠️ No portfolio found. Please build a portfolio first.")
    if st.button("Go to Portfolio Builder"):
        st.switch_page("home.py")
    st.stop()

portfolio = st.session_state.portfolio

# Header
st.markdown('<div class="main-title">📊 Portfolio Risk Overview (30-Day Outlook)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">How much your portfolio could lose in the next month — and why.</div>', unsafe_allow_html=True)

# Fetch data
symbols = portfolio.get_symbols()

with st.spinner("Fetching market data and calculating risk..."):
    try:
        # Get historical prices
        prices = fetch_multiple_stocks(symbols, period="1y")
        
        # Get current prices
        current_prices = get_current_prices(symbols)
        
        # Calculate portfolio metrics
        portfolio_value = portfolio.calculate_current_value(current_prices)
        weights = portfolio.calculate_weights(current_prices)
        
        # Calculate historical portfolio returns
        portfolio_returns = calculate_portfolio_returns(prices, weights)
        
        # Calculate VaR and CVaR
        var_amount = portfolio_value_at_risk(portfolio_value, portfolio_returns, confidence_level=0.95)
        cvar_amount = portfolio_cvar(portfolio_value, portfolio_returns, confidence_level=0.95)
        
        # Run Monte Carlo simulation
        simulated_values = simulate_portfolio_outcomes(
            prices, weights, portfolio_value, 
            horizon_days=30, n_simulations=10000
        )
        
        # Calculate simulation statistics
        sim_stats = calculate_simulation_statistics(simulated_values, portfolio_value)
        
        # Assess risk level
        var_pct = (var_amount / portfolio_value) * 100
        risk_level, risk_emoji = assess_risk_level(var_pct)
        
    except Exception as e:
        st.error(f"Error analyzing portfolio: {str(e)}")
        st.stop()

# Store in session state for other pages
st.session_state.analysis = {
    'prices': prices,
    'current_prices': current_prices,
    'portfolio_value': portfolio_value,
    'weights': weights,
    'var_amount': var_amount,
    'cvar_amount': cvar_amount,
    'simulated_values': simulated_values,
    'sim_stats': sim_stats,
    'risk_level': risk_level,
    'portfolio_returns': portfolio_returns
}

# Display metrics
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("### 💼 Portfolio Value")
    st.markdown(f"<h2 style='color: #1f4788;'>{format_currency(portfolio_value)}</h2>", unsafe_allow_html=True)

with col2:
    risk_color = get_risk_color(risk_level)
    risk_class = f"risk-{risk_level.lower().replace(' ', '-')}"
    st.markdown("### ⚠️ 30-Day Risk Level")
    st.markdown(f"<h2 style='color: {risk_color};'>{risk_emoji} {risk_level}</h2>", unsafe_allow_html=True)

with col3:
    st.markdown("### 🔻 Potential Downside (5%)")
    st.markdown(f"<h2 style='color: #e74c3c;'>{format_currency(var_amount)}</h2>", unsafe_allow_html=True)

st.markdown("---")

# Explanation text
explanation = explain_var(var_amount, portfolio_value, confidence_level=0.95, horizon_days=30)
st.info(f"**Interpretation:** {explanation}")

st.markdown("---")

# Visualization: Histogram of outcomes
st.markdown("### 📈 Possible 30-Day Outcomes")

fig = go.Figure()

# Histogram
fig.add_trace(go.Histogram(
    x=simulated_values,
    nbinsx=50,
    name='Simulated Values',
    marker_color='steelblue',
    opacity=0.7
))

# Add current value line
fig.add_vline(
    x=portfolio_value, 
    line_dash="dash", 
    line_color="green",
    annotation_text="Current Value",
    annotation_position="top"
)

# Add VaR line
var_value = portfolio_value - var_amount
fig.add_vline(
    x=var_value,
    line_dash="dash",
    line_color="red",
    annotation_text="VaR (95%)",
    annotation_position="top"
)

fig.update_layout(
    title="Distribution of Simulated Portfolio Values",
    xaxis_title="Portfolio Value (₹)",
    yaxis_title="Frequency",
    showlegend=False,
    height=400,
    hovermode='x'
)

st.plotly_chart(fig, use_container_width=True)

# Simulation summary
st.markdown("### 📊 Simulation Summary")

col_sim1, col_sim2, col_sim3, col_sim4 = st.columns(4)

with col_sim1:
    st.metric(
        "Scenarios with Gains",
        f"{sim_stats['prob_gain']*100:.0f}%"
    )

with col_sim2:
    st.metric(
        "Scenarios with Losses",
        f"{sim_stats['prob_loss']*100:.0f}%"
    )

with col_sim3:
    st.metric(
        "Median Outcome",
        format_currency(sim_stats['median_value'])
    )

with col_sim4:
    st.metric(
        "Expected Return",
        f"{sim_stats['mean_return']*100:+.2f}%"
    )

# Additional explanation
sim_explanation = explain_simulation_outcomes(sim_stats, portfolio_value)
st.info(f"**Analysis:** {sim_explanation}")

# Bottom navigation
st.markdown("---")
col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    if st.button("← Back to Portfolio", use_container_width=True):
        st.switch_page("home.py")

with col_nav2:
    if st.button("Next: Risk Drivers →", type="primary", use_container_width=True):
        st.switch_page("pages/2_Risk_Drivers.py")
