# portfolio_risk_app/utils/explain.py
"""
Explanation Module
Generates natural language explanations of risk metrics and portfolio behavior.
"""

import numpy as np
import pandas as pd
from typing import Dict, List


def explain_var(var_amount: float, 
                portfolio_value: float, 
                confidence_level: float = 0.95,
                horizon_days: int = 30) -> str:
    """
    Generate plain language explanation of Value at Risk.
    
    Parameters
    ----------
    var_amount : float
        VaR in monetary terms
    portfolio_value : float
        Current portfolio value
    confidence_level : float
        Confidence level (default 0.95)
    horizon_days : int
        Time horizon in days
    
    Returns
    -------
    str
        Natural language explanation
    """
    var_pct = (var_amount / portfolio_value) * 100
    prob_pct = (1 - confidence_level) * 100
    
    explanation = (
        f"There is a {prob_pct:.0f}% chance that your portfolio could lose more than "
        f"₹{var_amount:,.0f} ({var_pct:.1f}% of portfolio value) over the next "
        f"{horizon_days} days under typical market conditions."
    )
    
    return explanation


def assess_risk_level(var_pct: float) -> tuple:
    """
    Assess overall risk level based on VaR percentage.
    
    Parameters
    ----------
    var_pct : float
        VaR as percentage of portfolio value
    
    Returns
    -------
    tuple
        (risk_level: str, emoji: str)
    """
    if var_pct < 3:
        return "Low", "🟢"
    elif var_pct < 7:
        return "Moderate", "🟡"
    elif var_pct < 12:
        return "High", "🟠"
    else:
        return "Very High", "🔴"


def explain_simulation_outcomes(stats: Dict, 
                                portfolio_value: float) -> str:
    """
    Explain simulation results in plain language.
    
    Parameters
    ----------
    stats : Dict
        Simulation statistics dictionary
    portfolio_value : float
        Current portfolio value
    
    Returns
    -------
    str
        Natural language explanation
    """
    prob_gain = stats['prob_gain'] * 100
    prob_loss = stats['prob_loss'] * 100
    median_value = stats['median_value']
    var_amount = portfolio_value - stats['var_95']
    
    explanation = (
        f"{prob_gain:.0f}% of simulated scenarios result in gains, while "
        f"{prob_loss:.0f}% result in losses. The median outcome is ₹{median_value:,.0f}. "
        f"In the worst 5% of scenarios, losses exceed ₹{var_amount:,.0f}."
    )
    
    return explanation


def explain_risk_contribution(risk_contrib: pd.Series, 
                              top_n: int = 3) -> str:
    """
    Explain which assets contribute most to portfolio risk.
    
    Parameters
    ----------
    risk_contrib : pd.Series
        Risk contribution percentages by asset
    top_n : int
        Number of top contributors to mention
    
    Returns
    -------
    str
        Natural language explanation
    """
    sorted_contrib = risk_contrib.sort_values(ascending=False)
    top_contributors = sorted_contrib.head(top_n)
    
    explanation_parts = []
    for symbol, contrib in top_contributors.items():
        explanation_parts.append(f"{symbol} ({contrib:.1f}%)")
    
    explanation = (
        f"The largest risk contributors are: {', '.join(explanation_parts)}. "
        f"These assets drive portfolio volatility due to their weight, individual "
        f"volatility, and correlations with other holdings."
    )
    
    return explanation


def explain_correlation(corr_matrix: pd.DataFrame) -> str:
    """
    Explain correlation structure and its implications.
    
    Parameters
    ----------
    corr_matrix : pd.DataFrame
        Correlation matrix
    
    Returns
    -------
    str
        Natural language explanation
    """
    # Get upper triangle correlations (exclude diagonal)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    upper_triangle = corr_matrix.where(mask)
    
    # Calculate average correlation
    avg_corr = upper_triangle.stack().mean()
    max_corr = upper_triangle.stack().max()
    min_corr = upper_triangle.stack().min()
    
    # Find most correlated pair
    max_idx = upper_triangle.stack().idxmax()
    
    if avg_corr > 0.6:
        diversification = "limited"
        implication = "assets tend to move together, reducing diversification benefits"
    elif avg_corr > 0.3:
        diversification = "moderate"
        implication = "provides some diversification, though assets show meaningful co-movement"
    else:
        diversification = "good"
        implication = "assets move relatively independently, enhancing diversification"
    
    explanation = (
        f"Average correlation: {avg_corr:.2f} (range: {min_corr:.2f} to {max_corr:.2f}). "
        f"Your portfolio shows {diversification} diversification. Highly correlated "
        f"{implication}. The strongest correlation is between {max_idx[0]} and "
        f"{max_idx[1]} ({corr_matrix.loc[max_idx]:.2f})."
    )
    
    return explanation


def explain_volatility(volatilities: pd.Series, 
                       weights: np.ndarray,
                       symbols: List[str]) -> str:
    """
    Explain individual asset volatilities and their impact.
    
    Parameters
    ----------
    volatilities : pd.Series
        Individual asset volatilities
    weights : np.ndarray
        Portfolio weights
    symbols : List[str]
        Asset symbols
    
    Returns
    -------
    str
        Natural language explanation
    """
    # Create DataFrame for easier manipulation
    vol_df = pd.DataFrame({
        'symbol': symbols,
        'volatility': volatilities.values,
        'weight': weights * 100
    })
    
    # Sort by volatility
    vol_df = vol_df.sort_values('volatility', ascending=False)
    
    highest_vol = vol_df.iloc[0]
    lowest_vol = vol_df.iloc[-1]
    
    explanation = (
        f"Individual volatilities range from {lowest_vol['volatility']:.2%} ({lowest_vol['symbol']}) "
        f"to {highest_vol['volatility']:.2%} ({highest_vol['symbol']}). "
        f"Higher volatility increases uncertainty in portfolio outcomes. "
    )
    
    # Check if high-volatility assets have large weights
    high_vol_high_weight = vol_df[(vol_df['volatility'] > vol_df['volatility'].median()) & 
                                   (vol_df['weight'] > 20)]
    
    if not high_vol_high_weight.empty:
        explanation += (
            f"Note: {', '.join(high_vol_high_weight['symbol'].tolist())} combine "
            f"high volatility with significant portfolio weight, amplifying risk exposure."
        )
    else:
        explanation += (
            "Your portfolio weights are well-distributed relative to individual volatilities."
        )
    
    return explanation


def explain_scenario_paths(current_price: float,
                           simulated_paths: np.ndarray,
                           horizon_days: int) -> str:
    """
    Explain simulated price scenarios for a single asset.
    
    Parameters
    ----------
    current_price : float
        Current asset price
    simulated_paths : np.ndarray
        Array of simulated price paths
    horizon_days : int
        Simulation horizon
    
    Returns
    -------
    str
        Natural language explanation
    """
    # Get final prices from all paths
    final_prices = simulated_paths[:, -1]
    
    # Calculate percentage changes
    pct_changes = (final_prices - current_price) / current_price * 100
    
    # Statistics
    median_change = np.median(pct_changes)
    percentile_5 = np.percentile(pct_changes, 5)
    percentile_95 = np.percentile(pct_changes, 95)
    
    explanation = (
        f"This scenario simulation illustrates a range of possible short-term price paths "
        f"over {horizon_days} days. The median simulated change is {median_change:+.2f}%. "
        f"90% of paths fall between {percentile_5:.2f}% and {percentile_95:+.2f}%. "
        f"This is not a prediction but a representation of uncertainty based on "
        f"historical volatility."
    )
    
    return explanation


def generate_risk_summary(var_amount: float,
                         cvar_amount: float,
                         portfolio_value: float,
                         stats: Dict,
                         risk_level: str) -> str:
    """
    Generate comprehensive risk summary for executive report.
    
    Parameters
    ----------
    var_amount : float
        VaR in monetary terms
    cvar_amount : float
        CVaR in monetary terms
    portfolio_value : float
        Current portfolio value
    stats : Dict
        Simulation statistics
    risk_level : str
        Assessed risk level
    
    Returns
    -------
    str
        Comprehensive risk summary
    """
    var_pct = (var_amount / portfolio_value) * 100
    cvar_pct = (cvar_amount / portfolio_value) * 100
    prob_gain = stats['prob_gain'] * 100
    
    summary = f"""
Portfolio Risk Assessment (30-Day Horizon)

Overall Risk Level: {risk_level}

Current Portfolio Value: ₹{portfolio_value:,.0f}

Downside Risk Metrics:
• Value at Risk (95%): ₹{var_amount:,.0f} ({var_pct:.1f}%)
  → 5% chance of losing more than this amount
  
• Conditional VaR (95%): ₹{cvar_amount:,.0f} ({cvar_pct:.1f}%)
  → Expected loss if the worst 5% scenario occurs
  
• Probability of Gain: {prob_gain:.0f}%
• Median Projected Value: ₹{stats['median_value']:,.0f}

Interpretation:
Under normal market conditions over the next 30 days, there is a 5% probability 
your portfolio could lose more than ₹{var_amount:,.0f}. If losses exceed this threshold, 
the average expected loss is ₹{cvar_amount:,.0f}. These estimates are based on 
historical volatility and correlation patterns.
    """
    
    return summary.strip()
