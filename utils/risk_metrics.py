# portfolio_risk_app/utils/risk_metrics.py
"""
Risk Metrics Module
Computes Value at Risk (VaR), Conditional VaR (CVaR), and portfolio returns.
"""

import numpy as np
import pandas as pd


def calculate_portfolio_returns(prices: pd.DataFrame, weights: np.ndarray) -> pd.Series:
    """
    Calculate portfolio returns from individual asset prices and weights.
    
    Parameters
    ----------
    prices : pd.DataFrame
        Historical prices with assets as columns
    weights : np.ndarray
        Portfolio weights (must sum to 1)
    
    Returns
    -------
    pd.Series
        Daily portfolio returns
    """
    # Calculate individual asset returns
    returns = prices.pct_change().dropna()
    
    # Calculate weighted portfolio returns
    portfolio_returns = (returns * weights).sum(axis=1)
    
    return portfolio_returns


def calculate_var(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Value at Risk (VaR) at specified confidence level.
    
    VaR represents the maximum loss not exceeded with a given confidence level.
    
    Parameters
    ----------
    returns : pd.Series
        Portfolio returns
    confidence_level : float
        Confidence level (default 0.95 for 95% VaR)
    
    Returns
    -------
    float
        VaR as a negative return (loss)
    """
    var = np.percentile(returns, (1 - confidence_level) * 100)
    return var


def calculate_cvar(returns: pd.Series, confidence_level: float = 0.95) -> float:
    """
    Calculate Conditional Value at Risk (CVaR), also known as Expected Shortfall.
    
    CVaR is the expected loss given that the loss exceeds VaR.
    It measures tail risk beyond the VaR threshold.
    
    Parameters
    ----------
    returns : pd.Series
        Portfolio returns
    confidence_level : float
        Confidence level (default 0.95)
    
    Returns
    -------
    float
        CVaR as a negative return (expected tail loss)
    """
    var = calculate_var(returns, confidence_level)
    
    # CVaR is the mean of returns below VaR
    cvar = returns[returns <= var].mean()
    
    return cvar


def calculate_volatility(returns: pd.Series, annualize: bool = False) -> float:
    """
    Calculate volatility (standard deviation of returns).
    
    Parameters
    ----------
    returns : pd.Series
        Returns series
    annualize : bool
        If True, annualize the volatility (default False)
    
    Returns
    -------
    float
        Volatility
    """
    vol = returns.std()
    
    if annualize:
        # Annualize assuming 252 trading days
        vol = vol * np.sqrt(252)
    
    return vol


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    Calculate maximum drawdown from peak.
    
    Parameters
    ----------
    returns : pd.Series
        Returns series
    
    Returns
    -------
    float
        Maximum drawdown as a negative percentage
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    
    return drawdown.min()


def portfolio_value_at_risk(current_value: float, returns: pd.Series, 
                           confidence_level: float = 0.95) -> float:
    """
    Calculate portfolio Value at Risk in monetary terms.
    
    Parameters
    ----------
    current_value : float
        Current portfolio value
    returns : pd.Series
        Portfolio returns
    confidence_level : float
        Confidence level (default 0.95)
    
    Returns
    -------
    float
        VaR in monetary units (positive number representing potential loss)
    """
    var_return = calculate_var(returns, confidence_level)
    var_monetary = abs(var_return * current_value)
    
    return var_monetary


def portfolio_cvar(current_value: float, returns: pd.Series, 
                  confidence_level: float = 0.95) -> float:
    """
    Calculate portfolio Conditional VaR in monetary terms.
    
    Parameters
    ----------
    current_value : float
        Current portfolio value
    returns : pd.Series
        Portfolio returns
    confidence_level : float
        Confidence level (default 0.95)
    
    Returns
    -------
    float
        CVaR in monetary units (positive number representing expected tail loss)
    """
    cvar_return = calculate_cvar(returns, confidence_level)
    cvar_monetary = abs(cvar_return * current_value)
    
    return cvar_monetary
