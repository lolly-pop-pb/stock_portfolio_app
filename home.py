# portfolio_risk_app/home.py
"""
Portfolio Risk Analysis Application
Home Page: Portfolio Builder
"""

import streamlit as st
import pandas as pd
import json
import os
from utils.portfolio import Portfolio
from utils.data_loader import validate_symbol, get_current_prices
from assets.styles import format_currency

# Page configuration
st.set_page_config(
    page_title="Portfolio Risk Analysis",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = Portfolio()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4788;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #34495e;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #ecf0f1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🏠 Portfolio Builder</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Build a portfolio to analyze short-term downside risk and uncertainty.</div>', unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### Add Stock")
    
    with st.form("add_stock_form", clear_on_submit=True):
        symbol = st.text_input(
            "Stock Symbol",
            placeholder="e.g., AAPL, MSFT, INFY.NS",
            help="Enter ticker symbol (use .NS suffix for NSE stocks)"
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            shares = st.number_input(
                "Number of Shares",
                min_value=0.01,
                value=10.0,
                step=1.0
            )
        
        with col_b:
            buy_price = st.number_input(
                "Buy Price per Share",
                min_value=0.01,
                value=100.0,
                step=1.0
            )
        
        submitted = st.form_submit_button("➕ Add to Portfolio", use_container_width=True)
        
        if submitted:
            if symbol:
                symbol = symbol.upper().strip()
                
                # Validate symbol
                with st.spinner(f"Validating {symbol}..."):
                    if validate_symbol(symbol):
                        st.session_state.portfolio.add_holding(symbol, shares, buy_price)
                        st.success(f"✅ Added {shares} shares of {symbol} at {format_currency(buy_price)}")
                        st.rerun()
                    else:
                        st.error(f"❌ Invalid symbol: {symbol}. Please check and try again.")
            else:
                st.warning("Please enter a stock symbol.")

with col2:
    st.markdown("### Current Portfolio")
    
    if st.session_state.portfolio.is_empty():
        st.info("📭 Your portfolio is empty. Add stocks to begin analysis.")
    else:
        # Get current prices
        symbols = st.session_state.portfolio.get_symbols()
        
        with st.spinner("Fetching current prices..."):
            current_prices = get_current_prices(symbols)
        
        # Display portfolio table
        allocation_df = st.session_state.portfolio.get_allocation_table(current_prices)
        
        # Format for display
        display_df = allocation_df[['Symbol', 'Shares', 'Buy Price', 'Current Price', 
                                    'Invested', 'Current Value', 'Weight (%)', 
                                    'Gain/Loss', 'Gain/Loss (%)']].copy()
        
        # Format currency columns
        for col in ['Buy Price', 'Current Price', 'Invested', 'Current Value', 'Gain/Loss']:
            display_df[col] = display_df[col].apply(lambda x: format_currency(x, 2))
        
        # Format percentage columns
        display_df['Weight (%)'] = display_df['Weight (%)'].apply(lambda x: f"{x:.1f}%")
        display_df['Gain/Loss (%)'] = display_df['Gain/Loss (%)'].apply(lambda x: f"{x:+.1f}%")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Portfolio summary
        st.markdown("---")
        
        total_invested = st.session_state.portfolio.get_invested_value()
        total_current = st.session_state.portfolio.calculate_current_value(current_prices)
        total_gain_loss = total_current - total_invested
        total_gain_loss_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0
        
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            st.metric("Total Invested", format_currency(total_invested))
        
        with col_s2:
            st.metric("Current Value", format_currency(total_current))
        
        with col_s3:
            st.metric(
                "Total Gain/Loss", 
                format_currency(total_gain_loss),
                delta=f"{total_gain_loss_pct:+.1f}%"
            )
        
        # Remove stock section
        st.markdown("---")
        with st.expander("🗑️ Remove Stock"):
            if len(st.session_state.portfolio.holdings) > 0:
                remove_options = [
                    f"{i}: {h['symbol']} ({h['shares']} shares)"
                    for i, h in enumerate(st.session_state.portfolio.holdings)
                ]
                
                to_remove = st.selectbox(
                    "Select stock to remove",
                    options=range(len(remove_options)),
                    format_func=lambda x: remove_options[x]
                )
                
                if st.button("Remove Selected Stock", type="secondary"):
                    st.session_state.portfolio.remove_holding(to_remove)
                    st.success("Stock removed successfully!")
                    st.rerun()

# Bottom section
st.markdown("---")

if st.session_state.portfolio.is_empty():
    st.info("💡 **Get Started:** Add at least 2 stocks to your portfolio to analyze risk.")
else:
    col_bottom1, col_bottom2 = st.columns([2, 1])
    
    with col_bottom1:
        st.markdown("""
        <div class="info-box">
        <b>Next Steps:</b><br>
        Navigate to <b>Risk Overview</b> in the sidebar to see your portfolio's downside risk analysis.
        </div>
        """, unsafe_allow_html=True)
    
    with col_bottom2:
        if st.session_state.portfolio.get_holding_count() >= 2:
            if st.button("➡️ Analyze Portfolio Risk", type="primary", use_container_width=True):
                st.switch_page("pages/1_Risk_Overview.py")
        else:
            st.info("Add at least 2 stocks to enable analysis.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; font-size: 0.9rem;'>
<b>Portfolio Risk Analysis System</b><br>
Explainable Short-Term Downside Risk for Equity Portfolios
</div>
""", unsafe_allow_html=True)
