# portfolio_risk_app/utils/simulation.py
"""
Monte Carlo Simulation Module
Simulates future portfolio value distributions based on historical returns.
"""

import numpy as np
import pandas as pd
from typing import Tuple


def simulate_portfolio_outcomes(prices: pd.DataFrame, 
                                weights: np.ndarray,
                                current_value: float,
                                horizon_days: int = 30,
                                n_simulations: int = 10000,
                                random_seed: int = 42) -> np.ndarray:
    """
    Simulate future portfolio values using Monte Carlo simulation.
    
    This function models portfolio uncertainty by:
    1. Calculating historical returns and covariance
    2. Simulating correlated daily returns
    3. Compounding returns over the horizon
    
    Parameters
    ----------
    prices : pd.DataFrame
        Historical prices with assets as columns
    weights : np.ndarray
        Portfolio weights (must sum to 1)
    current_value : float
        Current portfolio value
    horizon_days : int
        Simulation horizon in days (default 30)
    n_simulations : int
        Number of Monte Carlo simulations (default 10000)
    random_seed : int
        Random seed for reproducibility
    
    Returns
    -------
    np.ndarray
        Array of simulated portfolio values at horizon
    """
    np.random.seed(random_seed)
    
    # Calculate historical returns
    returns = prices.pct_change().dropna()
    
    # Get mean returns and covariance matrix
    mean_returns = returns.mean().values
    cov_matrix = returns.cov().values
    
    # Simulate correlated returns
    simulated_returns = np.random.multivariate_normal(
        mean_returns, 
        cov_matrix, 
        size=(n_simulations, horizon_days)
    )
    
    # Calculate portfolio returns for each simulation
    portfolio_returns = np.dot(simulated_returns, weights)
    
    # Compound returns over horizon to get final values
    final_values = current_value * np.prod(1 + portfolio_returns, axis=1)
    
    return final_values


def simulate_single_asset_paths(prices: pd.Series,
                                current_price: float,
                                horizon_days: int = 14,
                                n_simulations: int = 500,
                                random_seed: int = 42) -> np.ndarray:
    """
    Simulate future price paths for a single asset.
    
    Used for scenario exploration, not prediction.
    
    Parameters
    ----------
    prices : pd.Series
        Historical prices
    current_price : float
        Current price
    horizon_days : int
        Simulation horizon in days
    n_simulations : int
        Number of paths to simulate
    random_seed : int
        Random seed for reproducibility
    
    Returns
    -------
    np.ndarray
        Array of shape (n_simulations, horizon_days) containing price paths
    """
    np.random.seed(random_seed)
    
    # Calculate historical returns statistics
    returns = prices.pct_change().dropna()
    mean_return = returns.mean()
    volatility = returns.std()
    
    # Simulate daily returns
    simulated_returns = np.random.normal(
        mean_return,
        volatility,
        size=(n_simulations, horizon_days)
    )
    
    # Generate price paths by compounding returns
    price_paths = np.zeros((n_simulations, horizon_days + 1))
    price_paths[:, 0] = current_price
    
    for t in range(horizon_days):
        price_paths[:, t + 1] = price_paths[:, t] * (1 + simulated_returns[:, t])
    
    return price_paths


def calculate_simulation_statistics(simulated_values: np.ndarray, 
                                    current_value: float) -> dict:
    """
    Calculate summary statistics from simulated portfolio values.
    
    Parameters
    ----------
    simulated_values : np.ndarray
        Array of simulated portfolio values
    current_value : float
        Current portfolio value
    
    Returns
    -------
    dict
        Dictionary containing simulation statistics
    """
    # Calculate percentiles
    percentiles = {
        '5th': np.percentile(simulated_values, 5),
        '25th': np.percentile(simulated_values, 25),
        '50th': np.percentile(simulated_values, 50),
        '75th': np.percentile(simulated_values, 75),
        '95th': np.percentile(simulated_values, 95)
    }
    
    # Calculate probability of gain
    prob_gain = (simulated_values > current_value).mean()
    
    # Calculate probability of significant loss (>5%)
    prob_significant_loss = (simulated_values < current_value * 0.95).mean()
    
    # Calculate returns
    simulated_returns = (simulated_values - current_value) / current_value
    
    stats = {
        'mean_value': simulated_values.mean(),
        'median_value': percentiles['50th'],
        'std_value': simulated_values.std(),
        'percentiles': percentiles,
        'prob_gain': prob_gain,
        'prob_loss': 1 - prob_gain,
        'prob_significant_loss': prob_significant_loss,
        'mean_return': simulated_returns.mean(),
        'median_return': np.median(simulated_returns),
        'var_95': np.percentile(simulated_values, 5),
        'cvar_95': simulated_values[simulated_values <= np.percentile(simulated_values, 5)].mean()
    }
    
    return stats


def get_loss_distribution(simulated_values: np.ndarray, 
                         current_value: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract loss scenarios from simulated values.
    
    Parameters
    ----------
    simulated_values : np.ndarray
        Array of simulated portfolio values
    current_value : float
        Current portfolio value
    
    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Loss amounts and their probabilities
    """
    # Calculate losses (negative returns in monetary terms)
    losses = current_value - simulated_values
    
    # Only keep actual losses (positive loss amounts)
    loss_scenarios = losses[losses > 0]
    
    # Calculate probability of each loss magnitude
    # Bin losses and calculate probabilities
    if len(loss_scenarios) > 0:
        hist, bin_edges = np.histogram(loss_scenarios, bins=50)
        probabilities = hist / len(simulated_values)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        return bin_centers, probabilities
    else:
        return np.array([]), np.array([])
