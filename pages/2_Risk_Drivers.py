# portfolio_risk_app/pages/2_Risk_Drivers.py
"""
Page 2: Risk Drivers
Explains sources of portfolio risk.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.portfolio import (
    calculate_risk_contribution, 
    calculate_correlation_matrix,
    calculate_individual_volatilities
)
from utils.explain import (
    explain_risk_contribution,
    explain_correlation,
    explain_volatility
)
from assets.styles import COLORS

st.set_page_config(page_title="Risk Drivers", page_icon="🧠", layout="wide")

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
    .section-header {
        font-size: 1.5rem;
        color: #2c5aa0;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Check if analysis exists
if 'analysis' not in st.session_state:
    st.warning("⚠️ Please run Risk Overview analysis first.")
    if st.button("Go to Risk Overview"):
        st.switch_page("pages/1_Risk_Overview.py")
    st.stop()

# Get data from session state
prices = st.session_state.analysis['prices']
weights = st.session_state.analysis['weights']
symbols = list(prices.columns)

# Header
st.markdown('<div class="main-title">🧠 What Is Driving Portfolio Risk?</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Understanding the sources of your portfolio\'s downside exposure.</div>', unsafe_allow_html=True)

# Calculate risk metrics
with st.spinner("Analyzing risk drivers..."):
    risk_contrib = calculate_risk_contribution(prices, weights)
    corr_matrix = calculate_correlation_matrix(prices)
    volatilities = calculate_individual_volatilities(prices)

st.markdown("---")

# Section 1: Risk Contribution by Asset
st.markdown('<div class="section-header">1️⃣ Risk Contribution by Asset</div>', unsafe_allow_html=True)

st.info(
    "**What this means:** Stocks with higher volatility and larger portfolio weights "
    "contribute more to total risk. This shows which assets drive your downside exposure."
)

# Risk contribution bar chart
fig_contrib = go.Figure()

fig_contrib.add_trace(go.Bar(
    x=risk_contrib.values,
    y=risk_contrib.index,
    orientation='h',
    marker_color=COLORS['primary'],
    text=[f"{val:.1f}%" for val in risk_contrib.values],
    textposition='auto'
))

fig_contrib.update_layout(
    title="Risk Contribution by Asset (%)",
    xaxis_title="Risk Contribution (%)",
    yaxis_title="Asset",
    height=max(300, len(symbols) * 60),
    showlegend=False
)

st.plotly_chart(fig_contrib, use_container_width=True)

# Explanation
risk_contrib_explanation = explain_risk_contribution(risk_contrib, top_n=3)
st.markdown(f"**Analysis:** {risk_contrib_explanation}")

# Detailed table
with st.expander("📋 Detailed Risk Contribution Table"):
    contrib_df = pd.DataFrame({
        'Asset': risk_contrib.index,
        'Risk Contribution (%)': risk_contrib.values,
        'Portfolio Weight (%)': weights * 100,
        'Volatility (%)': [volatilities[symbol] * 100 for symbol in risk_contrib.index]
    })
    contrib_df = contrib_df.sort_values('Risk Contribution (%)', ascending=False)
    
    st.dataframe(
        contrib_df.style.format({
            'Risk Contribution (%)': '{:.2f}%',
            'Portfolio Weight (%)': '{:.2f}%',
            'Volatility (%)': '{:.2f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# Section 2: Correlation Structure
st.markdown('<div class="section-header">2️⃣ Correlation Structure</div>', unsafe_allow_html=True)

st.info(
    "**What this means:** Highly correlated assets tend to move together, reducing "
    "diversification benefits. Low correlation improves risk reduction through diversification."
)

# Correlation heatmap
fig_corr = go.Figure(data=go.Heatmap(
    z=corr_matrix.values,
    x=corr_matrix.columns,
    y=corr_matrix.index,
    colorscale='RdBu',
    zmid=0,
    zmin=-1,
    zmax=1,
    text=corr_matrix.values,
    texttemplate='%{text:.2f}',
    textfont={"size": 10},
    colorbar=dict(title="Correlation")
))

fig_corr.update_layout(
    title="Asset Return Correlations",
    height=max(400, len(symbols) * 50),
    xaxis_title="Asset",
    yaxis_title="Asset"
)

st.plotly_chart(fig_corr, use_container_width=True)

# Explanation
corr_explanation = explain_correlation(corr_matrix)
st.markdown(f"**Analysis:** {corr_explanation}")

st.markdown("---")

# Section 3: Volatility Profile
st.markdown('<div class="section-header">3️⃣ Volatility Profile</div>', unsafe_allow_html=True)

st.info(
    "**What this means:** Higher volatility increases uncertainty in portfolio outcomes. "
    "Individual asset volatility combines with correlations to determine total portfolio risk."
)

# Volatility bar chart with weights
vol_df = pd.DataFrame({
    'Asset': volatilities.index,
    'Volatility (%)': volatilities.values * 100,
    'Weight (%)': weights * 100
})
vol_df = vol_df.sort_values('Volatility (%)', ascending=False)

fig_vol = go.Figure()

fig_vol.add_trace(go.Bar(
    x=vol_df['Asset'],
    y=vol_df['Volatility (%)'],
    name='Volatility',
    marker_color=COLORS['danger'],
    text=[f"{val:.2f}%" for val in vol_df['Volatility (%)']],
    textposition='auto'
))

fig_vol.add_trace(go.Scatter(
    x=vol_df['Asset'],
    y=vol_df['Weight (%)'],
    name='Portfolio Weight',
    mode='lines+markers',
    marker=dict(size=10, color=COLORS['success']),
    line=dict(width=3),
    yaxis='y2'
))

fig_vol.update_layout(
    title="Asset Volatility and Portfolio Weight",
    xaxis_title="Asset",
    yaxis_title="Volatility (%)",
    yaxis2=dict(
        title="Portfolio Weight (%)",
        overlaying='y',
        side='right'
    ),
    height=400,
    legend=dict(x=0.01, y=0.99),
    hovermode='x unified'
)

st.plotly_chart(fig_vol, use_container_width=True)

# Explanation
vol_explanation = explain_volatility(volatilities, weights, symbols)
st.markdown(f"**Analysis:** {vol_explanation}")

# Volatility table
with st.expander("📋 Volatility Details"):
    vol_table = vol_df.copy()
    vol_table['Annualized Volatility (%)'] = vol_table['Volatility (%)'] * (252 ** 0.5)
    
    st.dataframe(
        vol_table.style.format({
            'Volatility (%)': '{:.2f}%',
            'Weight (%)': '{:.2f}%',
            'Annualized Volatility (%)': '{:.2f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# Key insights box
st.markdown("### 💡 Key Insights")

col_insight1, col_insight2 = st.columns(2)

with col_insight1:
    st.markdown("""
    **Risk Decomposition:**
    - Total portfolio risk emerges from individual volatilities, correlations, and weights
    - Diversification reduces risk when correlations are low
    - Concentration in high-volatility assets amplifies risk
    """)

with col_insight2:
    st.markdown("""
    **Actionable Considerations:**
    - Consider rebalancing if risk is concentrated in few assets
    - High correlation reduces diversification effectiveness
    - Volatility × Weight = Risk contribution
    """)

# Navigation
st.markdown("---")
col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    if st.button("← Back to Risk Overview", use_container_width=True):
        st.switch_page("pages/1_Risk_Overview.py")

with col_nav2:
    if st.button("Next: Scenario Explorer →", type="primary", use_container_width=True):
        st.switch_page("pages/3_Scenario_Explorer.py")
