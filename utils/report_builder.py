# portfolio_risk_app/utils/report_builder.py
"""
Report Builder Module
Generates professional PDF risk reports using ReportLab.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import numpy as np
from typing import Dict


class RiskReportBuilder:
    """
    Builds professional PDF risk reports.
    """
    
    def __init__(self, filepath: str):
        """
        Initialize report builder.
        
        Parameters
        ----------
        filepath : str
            Output PDF filepath
        """
        self.filepath = filepath
        self.doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Custom styles
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c5aa0'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Body with justification
        self.styles.add(ParagraphStyle(
            name='BodyJustify',
            parent=self.styles['BodyText'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        ))
    
    def add_title_page(self, portfolio_value: float, date: str):
        """Add title page."""
        self.story.append(Spacer(1, 2*inch))
        
        title = Paragraph(
            "Portfolio Risk Analysis Report",
            self.styles['CustomTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))
        
        subtitle = Paragraph(
            "Short-Term Downside Risk Assessment",
            self.styles['Heading3']
        )
        subtitle.alignment = TA_CENTER
        self.story.append(subtitle)
        self.story.append(Spacer(1, 0.5*inch))
        
        info = [
            f"<b>Portfolio Value:</b> ₹{portfolio_value:,.0f}",
            f"<b>Report Date:</b> {date}",
            f"<b>Risk Horizon:</b> 30 Days",
            f"<b>Confidence Level:</b> 95%"
        ]
        
        for item in info:
            p = Paragraph(item, self.styles['BodyText'])
            p.alignment = TA_CENTER
            self.story.append(p)
            self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(PageBreak())
    
    def add_executive_summary(self, summary_text: str):
        """Add executive summary section."""
        self.story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Split summary into paragraphs
        paragraphs = summary_text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                p = Paragraph(para.strip().replace('\n', '<br/>'), self.styles['BodyJustify'])
                self.story.append(p)
        
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_portfolio_overview(self, allocation_df: pd.DataFrame):
        """Add portfolio allocation table."""
        self.story.append(Paragraph("Portfolio Composition", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Prepare table data
        table_data = [['Symbol', 'Shares', 'Current Price', 'Value', 'Weight (%)']]
        
        for _, row in allocation_df.iterrows():
            table_data.append([
                row['Symbol'],
                f"{row['Shares']:.2f}",
                f"₹{row['Current Price']:.2f}",
                f"₹{row['Current Value']:,.0f}",
                f"{row['Weight (%)']:.1f}%"
            ])
        
        # Create table
        table = Table(table_data, colWidths=[1.2*inch, 1*inch, 1.2*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_risk_metrics(self, var_amount: float, cvar_amount: float, 
                        portfolio_value: float, risk_level: str):
        """Add risk metrics section."""
        self.story.append(Paragraph("Downside Risk Metrics", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))
        
        var_pct = (var_amount / portfolio_value) * 100
        cvar_pct = (cvar_amount / portfolio_value) * 100
        
        metrics_data = [
            ['Metric', 'Value', 'Interpretation'],
            ['Risk Level', risk_level, 'Overall portfolio risk assessment'],
            ['Value at Risk (95%)', 
             f"₹{var_amount:,.0f} ({var_pct:.1f}%)", 
             '5% chance of losing more than this'],
            ['Conditional VaR (95%)', 
             f"₹{cvar_amount:,.0f} ({cvar_pct:.1f}%)", 
             'Expected loss in worst 5% scenarios']
        ]
        
        table = Table(metrics_data, colWidths=[1.5*inch, 2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_risk_contributors(self, risk_contrib: pd.Series):
        """Add risk contribution analysis."""
        self.story.append(Paragraph("Risk Contributors", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))
        
        text = Paragraph(
            "Risk contribution measures how much each asset contributes to total portfolio "
            "variance, accounting for its weight, volatility, and correlations.",
            self.styles['BodyJustify']
        )
        self.story.append(text)
        self.story.append(Spacer(1, 0.15*inch))
        
        # Create table
        contrib_data = [['Asset', 'Risk Contribution (%)']]
        for symbol, contrib in risk_contrib.sort_values(ascending=False).items():
            contrib_data.append([symbol, f"{contrib:.1f}%"])
        
        table = Table(contrib_data, colWidths=[2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_histogram(self, simulated_values: np.ndarray, 
                     current_value: float, var_value: float):
        """Add simulation outcome histogram."""
        self.story.append(Paragraph("Simulated Outcomes Distribution", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))
        
        # Create histogram
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(simulated_values, bins=50, color='steelblue', alpha=0.7, edgecolor='black')
        ax.axvline(current_value, color='green', linestyle='--', linewidth=2, label='Current Value')
        ax.axvline(var_value, color='red', linestyle='--', linewidth=2, label='VaR (95%)')
        ax.set_xlabel('Portfolio Value (₹)', fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.set_title('Distribution of 30-Day Portfolio Outcomes', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save to buffer
        buf = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buf, format='png', dpi=150)
        buf.seek(0)
        plt.close()
        
        # Add to report
        img = Image(buf, width=5*inch, height=3.3*inch)
        self.story.append(img)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_limitations(self):
        """Add limitations and assumptions section."""
        self.story.append(Paragraph("Limitations & Assumptions", self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))
        
        limitations = [
            "<b>Historical Data:</b> Risk estimates are based on historical volatility and "
            "correlations, which may not reflect future market conditions.",
            
            "<b>Normal Market Conditions:</b> Extreme events (market crashes, black swans) "
            "may result in losses exceeding VaR estimates.",
            
            "<b>Liquidity:</b> The analysis assumes all positions can be liquidated without "
            "market impact, which may not hold during stressed conditions.",
            
            "<b>Model Risk:</b> Monte Carlo simulation assumes returns follow a normal "
            "distribution, which may underestimate tail risk.",
            
            "<b>Time Horizon:</b> Risk estimates are specific to the 30-day horizon and "
            "should not be extrapolated to longer periods.",
            
            "<b>Not Investment Advice:</b> This report is for informational purposes only "
            "and does not constitute investment advice or recommendations."
        ]
        
        for limitation in limitations:
            p = Paragraph(f"• {limitation}", self.styles['BodyJustify'])
            self.story.append(p)
            self.story.append(Spacer(1, 0.1*inch))
    
    def build(self):
        """Build and save the PDF report."""
        self.doc.build(self.story)


def generate_risk_report(filepath: str,
                        portfolio_value: float,
                        allocation_df: pd.DataFrame,
                        var_amount: float,
                        cvar_amount: float,
                        risk_level: str,
                        risk_contrib: pd.Series,
                        simulated_values: np.ndarray,
                        summary_text: str) -> str:
    """
    Generate complete risk report PDF.
    
    Parameters
    ----------
    filepath : str
        Output PDF filepath
    portfolio_value : float
        Current portfolio value
    allocation_df : pd.DataFrame
        Portfolio allocation table
    var_amount : float
        VaR in monetary terms
    cvar_amount : float
        CVaR in monetary terms
    risk_level : str
        Risk level assessment
    risk_contrib : pd.Series
        Risk contribution by asset
    simulated_values : np.ndarray
        Simulated portfolio values
    summary_text : str
        Executive summary text
    
    Returns
    -------
    str
        Path to generated report
    """
    builder = RiskReportBuilder(filepath)
    
    # Build report sections
    date_str = datetime.now().strftime("%B %d, %Y")
    builder.add_title_page(portfolio_value, date_str)
    builder.add_executive_summary(summary_text)
    builder.add_portfolio_overview(allocation_df)
    builder.add_risk_metrics(var_amount, cvar_amount, portfolio_value, risk_level)
    builder.add_risk_contributors(risk_contrib)
    
    # Calculate VaR value for histogram
    var_value = portfolio_value - var_amount
    builder.add_histogram(simulated_values, portfolio_value, var_value)
    
    builder.add_limitations()
    
    # Build PDF
    builder.build()
    
    return filepath
