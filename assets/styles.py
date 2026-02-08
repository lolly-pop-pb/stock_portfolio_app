"""
Styles and Formatting
Color schemes and constants for consistent UI appearance.
"""

# Color scheme
COLORS = {
    'primary': '#1f4788',
    'secondary': '#2c5aa0',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    'light': '#ecf0f1',
    'dark': '#34495e',
    'background': '#ffffff',
    'text': '#2c3e50'
}

# Risk level colors
RISK_COLORS = {
    'Low': '#27ae60',
    'Moderate': '#f39c12',
    'High': '#e67e22',
    'Very High': '#e74c3c'
}

# Risk level emojis
RISK_EMOJIS = {
    'Low': '🟢',
    'Moderate': '🟡',
    'High': '🟠',
    'Very High': '🔴'
}

# Chart styling
CHART_CONFIG = {
    'color_palette': ['#1f4788', '#2c5aa0', '#3498db', '#5dade2', '#85c1e2'],
    'font_size': 12,
    'title_size': 16,
    'line_width': 2
}

# Currency formatting
CURRENCY_SYMBOL = '₹'

def format_currency(value: float, decimals: int = 0) -> str:
    """
    Format value as currency.
    
    Parameters
    ----------
    value : float
        Numeric value
    decimals : int
        Number of decimal places
    
    Returns
    -------
    str
        Formatted currency string
    """
    return f"{CURRENCY_SYMBOL}{value:,.{decimals}f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage.
    
    Parameters
    ----------
    value : float
        Numeric value (as decimal, e.g., 0.05 for 5%)
    decimals : int
        Number of decimal places
    
    Returns
    -------
    str
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"

def get_risk_color(risk_level: str) -> str:
    """
    Get color for risk level.
    
    Parameters
    ----------
    risk_level : str
        Risk level string
    
    Returns
    -------
    str
        Hex color code
    """
    return RISK_COLORS.get(risk_level, COLORS['info'])

def get_risk_emoji(risk_level: str) -> str:
    """
    Get emoji for risk level.
    
    Parameters
    ----------
    risk_level : str
        Risk level string
    
    Returns
    -------
    str
        Emoji string
    """
    return RISK_EMOJIS.get(risk_level, '⚪')
