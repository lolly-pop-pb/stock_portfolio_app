# portfolio_risk_app/pages/3_Scenario_Explorer.py
"""
Page 3: Scenario Explorer
Explores short-term price uncertainty (NOT prediction).
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from utils.simulation import simulate_single_asset_paths
from utils.explain import explain_scenario_paths
from assets.styles import COLORS

st.set_page_config(page_title="Scenario Explorer", page_icon="🔮", layout="wide")

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
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #f39c12;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
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
current_prices = st.session_state.analysis['current_prices']
symbols = list(prices.columns)

# Header
st.markdown('<div class="main-title">🔮 Market Scenario Explorer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Explore short-term price uncertainty for individual stocks.</div>', unsafe_allow_html=True)

# Important disclaimer
st.markdown("""
<div class="warning-box">
<b>⚠️ Important Notice:</b> This scenario simulation illustrates a range of possible 
short-term price paths based on historical volatility. <b>It is NOT a prediction</b> 
but a representation of uncertainty. Actual prices may differ significantly.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Controls
col_control1, col_control2 = st.columns([2, 1])

with col_control1:
    selected_symbol = st.selectbox(
        "Select Asset to Explore",
        options=symbols,
        help="Choose a stock to visualize uncertainty scenarios"
    )

with col_control2:
    horizon = st.selectbox(
        "Forecast Horizon",
        options=[7, 14, 30],
        format_func=lambda x: f"{x} days",
        index=1,
        help="Time period for scenario simulation"
    )

st.markdown("---")

# Run simulation
with st.spinner(f"Simulating scenarios for {selected_symbol}..."):
    # Get price series for selected symbol
    price_series = prices[selected_symbol]
    current_price = current_prices[selected_symbol]
    
    # Simulate paths
    simulated_paths = simulate_single_asset_paths(
        price_series,
        current_price,
        horizon_days=horizon,
        n_simulations=500,
        random_seed=42
    )
    
    # Calculate statistics
    final_prices = simulated_paths[:, -1]
    pct_changes = (final_prices - current_price) / current_price * 100
    
    median_change = np.median(pct_changes)
    percentile_5 = np.percentile(pct_changes, 5)
    percentile_95 = np.percentile(pct_changes, 95)
    prob_loss = (final_prices < current_price).mean() * 100

# Display key metrics
st.markdown("### 📊 Scenario Statistics")

col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.metric(
        "Current Price",
        f"₹{current_price:.2f}"
    )

with col_stat2:
    st.metric(
        "Median Change",
        f"{median_change:+.2f}%"
    )

with col_stat3:
    st.metric(
        "90% Range",
        f"{percentile_5:.2f}% to {percentile_95:+.2f}%"
    )

with col_stat4:
    st.metric(
        "Scenarios with Loss",
        f"{prob_loss:.0f}%"
    )

st.markdown("---")

# Visualization: Price paths
st.markdown("### 📈 Simulated Price Scenarios")

fig_paths = go.Figure()

# Plot sample of paths (50 paths for clarity)
n_display = 50
sample_indices = np.random.choice(simulated_paths.shape[0], n_display, replace=False)

for idx in sample_indices:
    fig_paths.add_trace(go.Scatter(
        x=list(range(horizon + 1)),
        y=simulated_paths[idx, :],
        mode='lines',
        line=dict(color=COLORS['secondary'], width=0.5),
        opacity=0.3,
        showlegend=False,
        hoverinfo='skip'
    ))

# Add median path
median_path = np.percentile(simulated_paths, 50, axis=0)
fig_paths.add_trace(go.Scatter(
    x=list(range(horizon + 1)),
    y=median_path,
    mode='lines',
    name='Median Path',
    line=dict(color=COLORS['success'], width=3)
))

# Add current price reference
fig_paths.add_hline(
    y=current_price,
    line_dash="dash",
    line_color="red",
    annotation_text="Current Price",
    annotation_position="right"
)

# Add uncertainty bands (5th and 95th percentiles)
upper_band = np.percentile(simulated_paths, 95, axis=0)
lower_band = np.percentile(simulated_paths, 5, axis=0)

fig_paths.add_trace(go.Scatter(
    x=list(range(horizon + 1)),
    y=upper_band,
    mode='lines',
    name='95th Percentile',
    line=dict(color=COLORS['warning'], width=2, dash='dot')
))

fig_paths.add_trace(go.Scatter(
    x=list(range(horizon + 1)),
    y=lower_band,
    mode='lines',
    name='5th Percentile',
    line=dict(color=COLORS['danger'], width=2, dash='dot')
))

fig_paths.update_layout(
    title=f"{selected_symbol} - Simulated Price Paths ({horizon} Days)",
    xaxis_title="Days from Today",
    yaxis_title="Price (₹)",
    height=500,
    hovermode='x unified',
    legend=dict(x=0.01, y=0.99)
)

st.plotly_chart(fig_paths, use_container_width=True)

# Explanation
scenario_explanation = explain_scenario_paths(current_price, simulated_paths, horizon)
st.info(f"**Interpretation:** {scenario_explanation}")

st.markdown("---")

# Distribution of final prices
st.markdown("### 📊 Distribution of Final Prices")

col_dist1, col_dist2 = st.columns([2, 1])

with col_dist1:
    fig_dist = go.Figure()
    
    fig_dist.add_trace(go.Histogram(
        x=final_prices,
        nbinsx=40,
        marker_color=COLORS['primary'],
        opacity=0.7,
        name='Simulated Prices'
    ))
    
    # Add current price line
    fig_dist.add_vline(
        x=current_price,
        line_dash="dash",
        line_color="red",
        annotation_text="Current",
        annotation_position="top"
    )
    
    # Add median line
    median_price = np.median(final_prices)
    fig_dist.add_vline(
        x=median_price,
        line_dash="dash",
        line_color="green",
        annotation_text="Median",
        annotation_position="top"
    )
    
    fig_dist.update_layout(
        title=f"Distribution of {horizon}-Day Prices",
        xaxis_title="Price (₹)",
        yaxis_title="Frequency",
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

with col_dist2:
    st.markdown("**Price Percentiles:**")
    
    percentiles_df = pd.DataFrame({
        'Percentile': ['5th', '25th', '50th (Median)', '75th', '95th'],
        'Price': [
            np.percentile(final_prices, 5),
            np.percentile(final_prices, 25),
            np.percentile(final_prices, 50),
            np.percentile(final_prices, 75),
            np.percentile(final_prices, 95)
        ],
        'Change (%)': [
            (np.percentile(final_prices, 5) - current_price) / current_price * 100,
            (np.percentile(final_prices, 25) - current_price) / current_price * 100,
            (np.percentile(final_prices, 50) - current_price) / current_price * 100,
            (np.percentile(final_prices, 75) - current_price) / current_price * 100,
            (np.percentile(final_prices, 95) - current_price) / current_price * 100
        ]
    })
    
    st.dataframe(
        percentiles_df.style.format({
            'Price': '₹{:.2f}',
            'Change (%)': '{:+.2f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")

# Additional context
st.markdown("### 💡 Understanding Scenarios")

st.markdown("""
This page helps you understand the **range of possible outcomes** for individual stocks, 
not predict what will happen. Key points:

- **Not Predictions:** These are simulations based on historical volatility, not forecasts
- **Uncertainty Representation:** Shows how wide the range of outcomes could be
- **Historical Basis:** Assumes future volatility similar to past patterns
- **Limitations:** Cannot account for unexpected events, news, or structural changes

**Use this to:**
- ✅ Understand price uncertainty magnitude
- ✅ See realistic ranges of movement
- ✅ Appreciate the role of volatility

**Do NOT use this to:**
- ❌ Make specific buy/sell decisions
- ❌ Time market entries or exits
- ❌ Predict exact price targets
""")

# Navigation
st.markdown("---")
col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    if st.button("← Back to Risk Drivers", use_container_width=True):
        st.switch_page("pages/2_Risk_Drivers.py")

with col_nav2:
    if st.button("Next: Generate Report →", type="primary", use_container_width=True):
        st.switch_page("pages/4_Report.py")
