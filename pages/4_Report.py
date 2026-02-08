# portfolio_risk_app/pages/3_Scenario_Explorer.py
"""
Page 4: Report Generator
Generates professional PDF risk reports.
"""

import streamlit as st
import os
from datetime import datetime
from utils.report_builder import generate_risk_report
from utils.portfolio import calculate_risk_contribution
from utils.explain import generate_risk_summary

st.set_page_config(page_title="Report Generator", page_icon="📄", layout="wide")

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
    .report-box {
        background-color: #ecf0f1;
        padding: 2rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3498db;
        margin: 2rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Check if analysis exists
if 'analysis' not in st.session_state:
    st.warning("⚠️ Please run Risk Overview analysis first.")
    if st.button("Go to Risk Overview"):
        st.switch_page("pages/1_Risk_Overview.py")
    st.stop()

# Check if portfolio exists
if 'portfolio' not in st.session_state:
    st.warning("⚠️ No portfolio found.")
    if st.button("Go to Portfolio Builder"):
        st.switch_page("home.py")
    st.stop()

# Header
st.markdown('<div class="main-title">📄 Portfolio Risk Report</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Generate a professional PDF summarizing portfolio risk, drivers, and uncertainty.</div>', unsafe_allow_html=True)

st.markdown("---")

# Get data from session state
portfolio = st.session_state.portfolio
analysis = st.session_state.analysis

portfolio_value = analysis['portfolio_value']
current_prices = analysis['current_prices']
var_amount = analysis['var_amount']
cvar_amount = analysis['cvar_amount']
risk_level = analysis['risk_level']
simulated_values = analysis['simulated_values']
sim_stats = analysis['sim_stats']
prices = analysis['prices']
weights = analysis['weights']

# Report preview
st.markdown("### 📋 Report Contents")

col_preview1, col_preview2 = st.columns(2)

with col_preview1:
    st.markdown("""
    **Section 1: Executive Summary**
    - Portfolio risk assessment overview
    - Key metrics and findings
    
    **Section 2: Portfolio Composition**
    - Current holdings and allocation
    - Asset weights and values
    
    **Section 3: Downside Risk Metrics**
    - Value at Risk (VaR) analysis
    - Conditional VaR (CVaR)
    - Risk level assessment
    """)

with col_preview2:
    st.markdown("""
    **Section 4: Risk Contributors**
    - Risk decomposition by asset
    - Contribution analysis
    
    **Section 5: Scenario Distributions**
    - Simulated outcome histogram
    - Probability distributions
    
    **Section 6: Limitations & Assumptions**
    - Methodological considerations
    - Important disclaimers
    """)

st.markdown("---")

# Report generation section
st.markdown('<div class="report-box">', unsafe_allow_html=True)
st.markdown("### 🎯 Generate Risk Report")
st.markdown("Click below to create your comprehensive portfolio risk analysis report.")

col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])

with col_gen2:
    if st.button("📥 Generate Risk Report", type="primary", use_container_width=True):
        with st.spinner("Generating professional PDF report..."):
            try:
                # Create reports directory if it doesn't exist
                reports_dir = "reports"
                os.makedirs(reports_dir, exist_ok=True)
                
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"portfolio_risk_report_{timestamp}.pdf"
                filepath = os.path.join(reports_dir, filename)
                
                # Get allocation table
                allocation_df = portfolio.get_allocation_table(current_prices)
                
                # Calculate risk contribution
                risk_contrib = calculate_risk_contribution(prices, weights)
                
                # Generate executive summary
                summary_text = generate_risk_summary(
                    var_amount,
                    cvar_amount,
                    portfolio_value,
                    sim_stats,
                    risk_level
                )
                
                # Generate report
                report_path = generate_risk_report(
                    filepath=filepath,
                    portfolio_value=portfolio_value,
                    allocation_df=allocation_df,
                    var_amount=var_amount,
                    cvar_amount=cvar_amount,
                    risk_level=risk_level,
                    risk_contrib=risk_contrib,
                    simulated_values=simulated_values,
                    summary_text=summary_text
                )
                
                st.success(f"✅ Report generated successfully!")
                
                # Provide download button
                with open(report_path, "rb") as file:
                    st.download_button(
                        label="📥 Download Report PDF",
                        data=file,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                # Display report info
                st.info(f"**Report saved to:** `{report_path}`")
                
            except Exception as e:
                st.error(f"Error generating report: {str(e)}")
                st.exception(e)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# Report features
st.markdown("### ✨ Report Features")

col_feat1, col_feat2, col_feat3 = st.columns(3)

with col_feat1:
    st.markdown("""
    **Professional Format**
    - Industry-standard layout
    - Clear visual hierarchy
    - Executive-ready design
    """)

with col_feat2:
    st.markdown("""
    **Comprehensive Analysis**
    - All key risk metrics
    - Visual representations
    - Plain-language explanations
    """)

with col_feat3:
    st.markdown("""
    **Decision-Ready**
    - Shareable with stakeholders
    - Suitable for documentation
    - Research-grade quality
    """)

st.markdown("---")

# Usage guidance
st.markdown("### 📖 How to Use This Report")

st.markdown("""
This report is designed for:
- **Personal Reference:** Keep as record of your portfolio's risk profile
- **Stakeholder Communication:** Share with financial advisors or investment committees
- **Academic Documentation:** Include in research projects or case studies
- **Decision Support:** Use insights to inform portfolio adjustments

**Important Notes:**
- Reports are timestamped for version control
- All metrics are based on historical data and Monte Carlo simulation
- This is a risk assessment tool, not investment advice
- Review the Limitations section carefully before making decisions
""")

st.markdown("---")

# Additional options
with st.expander("⚙️ Advanced Options"):
    st.markdown("""
    **Future Enhancements (Not Yet Implemented):**
    - Custom report branding
    - Multiple confidence levels
    - Longer time horizons
    - Comparison with benchmarks
    - Scenario stress testing
    
    These features may be added in future versions of the application.
    """)

# Navigation
st.markdown("---")
col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    if st.button("← Back to Scenario Explorer", use_container_width=True):
        st.switch_page("pages/3_Scenario_Explorer.py")

with col_nav2:
    if st.button("Return to Home", use_container_width=True):
        st.switch_page("home.py")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; font-size: 0.9rem; margin-top: 2rem;'>
<b>Portfolio Risk Analysis System</b><br>
Research-Grade Desktop Application for Short-Term Downside Risk Assessment<br>
<i>Reports are for informational purposes only and do not constitute investment advice.</i>
</div>
""", unsafe_allow_html=True)
