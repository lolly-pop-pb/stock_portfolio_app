# portfolio_risk_app/utils/portfolio.py
"""
Portfolio Module
Manages portfolio composition, valuation, and allocation.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple


class Portfolio:
    """
    Represents an equity portfolio with holdings and current market values.
    """
    
    def __init__(self):
        """Initialize empty portfolio."""
        self.holdings: List[Dict] = []
    
    def add_holding(self, symbol: str, shares: float, buy_price: float):
        """
        Add a stock holding to the portfolio.
        
        Parameters
        ----------
        symbol : str
            Stock ticker symbol
        shares : float
            Number of shares
        buy_price : float
            Purchase price per share
        """
        holding = {
            'symbol': symbol,
            'shares': shares,
            'buy_price': buy_price,
            'invested_value': shares * buy_price
        }
        self.holdings.append(holding)
    
    def remove_holding(self, index: int):
        """
        Remove a holding by index.
        
        Parameters
        ----------
        index : int
            Index of holding to remove
        """
        if 0 <= index < len(self.holdings):
            self.holdings.pop(index)
    
    def get_symbols(self) -> List[str]:
        """
        Get list of stock symbols in portfolio.
        
        Returns
        -------
        List[str]
            List of ticker symbols
        """
        return [h['symbol'] for h in self.holdings]
    
    def get_invested_value(self) -> float:
        """
        Get total invested value (historical cost basis).
        
        Returns
        -------
        float
            Total invested amount
        """
        return sum(h['invested_value'] for h in self.holdings)
    
    def calculate_current_value(self, current_prices: Dict[str, float]) -> float:
        """
        Calculate current market value of portfolio.
        
        Parameters
        ----------
        current_prices : Dict[str, float]
            Dictionary mapping symbols to current prices
        
        Returns
        -------
        float
            Current portfolio value
        """
        total_value = 0.0
        for holding in self.holdings:
            symbol = holding['symbol']
            if symbol in current_prices:
                total_value += holding['shares'] * current_prices[symbol]
        
        return total_value
    
    def calculate_weights(self, current_prices: Dict[str, float]) -> np.ndarray:
        """
        Calculate portfolio weights based on current market values.
        
        Parameters
        ----------
        current_prices : Dict[str, float]
            Dictionary mapping symbols to current prices
        
        Returns
        -------
        np.ndarray
            Array of portfolio weights (sum to 1)
        """
        total_value = self.calculate_current_value(current_prices)
        
        if total_value == 0:
            return np.zeros(len(self.holdings))
        
        weights = []
        for holding in self.holdings:
            symbol = holding['symbol']
            if symbol in current_prices:
                holding_value = holding['shares'] * current_prices[symbol]
                weight = holding_value / total_value
                weights.append(weight)
            else:
                weights.append(0.0)
        
        return np.array(weights)
    
    def get_allocation_table(self, current_prices: Dict[str, float]) -> pd.DataFrame:
        """
        Generate portfolio allocation table with all details.
        
        Parameters
        ----------
        current_prices : Dict[str, float]
            Dictionary mapping symbols to current prices
        
        Returns
        -------
        pd.DataFrame
            DataFrame with portfolio allocation details
        """
        total_value = self.calculate_current_value(current_prices)
        
        data = []
        for holding in self.holdings:
            symbol = holding['symbol']
            shares = holding['shares']
            buy_price = holding['buy_price']
            invested = holding['invested_value']
            
            if symbol in current_prices:
                current_price = current_prices[symbol]
                current_value = shares * current_price
                weight = current_value / total_value if total_value > 0 else 0
                gain_loss = current_value - invested
                gain_loss_pct = (gain_loss / invested * 100) if invested > 0 else 0
                
                data.append({
                    'Symbol': symbol,
                    'Shares': shares,
                    'Buy Price': buy_price,
                    'Current Price': current_price,
                    'Invested': invested,
                    'Current Value': current_value,
                    'Weight (%)': weight * 100,
                    'Gain/Loss': gain_loss,
                    'Gain/Loss (%)': gain_loss_pct
                })
        
        return pd.DataFrame(data)
    
    def to_dict(self) -> Dict:
        """
        Convert portfolio to dictionary for serialization.
        
        Returns
        -------
        Dict
            Portfolio as dictionary
        """
        return {'holdings': self.holdings}
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Portfolio':
        """
        Create portfolio from dictionary.
        
        Parameters
        ----------
        data : Dict
            Portfolio data dictionary
        
        Returns
        -------
        Portfolio
            Reconstructed portfolio object
        """
        portfolio = cls()
        portfolio.holdings = data.get('holdings', [])
        return portfolio
    
    def is_empty(self) -> bool:
        """
        Check if portfolio is empty.
        
        Returns
        -------
        bool
            True if no holdings exist
        """
        return len(self.holdings) == 0
    
    def get_holding_count(self) -> int:
        """
        Get number of holdings in portfolio.
        
        Returns
        -------
        int
            Number of holdings
        """
        return len(self.holdings)


def calculate_risk_contribution(prices: pd.DataFrame, 
                                weights: np.ndarray) -> pd.Series:
    """
    Calculate risk contribution of each asset to portfolio variance.
    
    Risk contribution shows how much each asset contributes to total portfolio risk,
    accounting for its weight, volatility, and correlation with other assets.
    
    Parameters
    ----------
    prices : pd.DataFrame
        Historical prices with assets as columns
    weights : np.ndarray
        Portfolio weights
    
    Returns
    -------
    pd.Series
        Risk contribution for each asset (percentages summing to 100)
    """
    # Calculate returns and covariance matrix
    returns = prices.pct_change().dropna()
    cov_matrix = returns.cov().values
    
    # Portfolio variance
    portfolio_variance = np.dot(weights, np.dot(cov_matrix, weights))
    
    # Marginal contribution to risk
    marginal_contrib = np.dot(cov_matrix, weights)
    
    # Risk contribution (component risk)
    risk_contrib = weights * marginal_contrib
    
    # Convert to percentages
    risk_contrib_pct = (risk_contrib / portfolio_variance) * 100
    
    return pd.Series(risk_contrib_pct, index=prices.columns)


def calculate_correlation_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate correlation matrix of asset returns.
    
    Parameters
    ----------
    prices : pd.DataFrame
        Historical prices with assets as columns
    
    Returns
    -------
    pd.DataFrame
        Correlation matrix
    """
    returns = prices.pct_change().dropna()
    return returns.corr()


def calculate_individual_volatilities(prices: pd.DataFrame, 
                                     annualize: bool = False) -> pd.Series:
    """
    Calculate volatility for each asset.
    
    Parameters
    ----------
    prices : pd.DataFrame
        Historical prices with assets as columns
    annualize : bool
        If True, annualize volatilities
    
    Returns
    -------
    pd.Series
        Volatility for each asset
    """
    returns = prices.pct_change().dropna()
    volatilities = returns.std()
    
    if annualize:
        volatilities = volatilities * np.sqrt(252)
    
    return volatilities
