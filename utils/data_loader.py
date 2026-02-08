# portfolio_risk_app/utils/data_loader.py
"""
Data Loader Module
Fetches and caches historical stock prices.
"""

import yfinance as yf
import pandas as pd
from typing import List, Optional
from datetime import datetime, timedelta
import streamlit as st


@st.cache_data(ttl=3600)
def fetch_stock_data(symbol: str, 
                    period: str = "1y",
                    start_date: Optional[str] = None,
                    end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch historical stock data for a single symbol.
    
    Data is cached for 1 hour to reduce API calls.
    
    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    period : str
        Period to fetch (e.g., "1y", "2y", "5y")
    start_date : Optional[str]
        Start date in YYYY-MM-DD format (overrides period)
    end_date : Optional[str]
        End date in YYYY-MM-DD format
    
    Returns
    -------
    pd.DataFrame
        Historical price data with columns: Open, High, Low, Close, Volume
    """
    try:
        ticker = yf.Ticker(symbol)
        
        if start_date and end_date:
            data = ticker.history(start=start_date, end=end_date)
        else:
            data = ticker.history(period=period)
        
        if data.empty:
            raise ValueError(f"No data found for {symbol}")
        
        return data
    
    except Exception as e:
        raise ValueError(f"Error fetching data for {symbol}: {str(e)}")


@st.cache_data(ttl=3600)
def fetch_multiple_stocks(symbols: List[str], 
                         period: str = "1y") -> pd.DataFrame:
    """
    Fetch historical closing prices for multiple stocks.
    
    Parameters
    ----------
    symbols : List[str]
        List of stock ticker symbols
    period : str
        Period to fetch (default "1y")
    
    Returns
    -------
    pd.DataFrame
        DataFrame with symbols as columns and dates as index
    """
    prices = pd.DataFrame()
    
    for symbol in symbols:
        try:
            data = fetch_stock_data(symbol, period=period)
            prices[symbol] = data['Close']
        except Exception as e:
            st.warning(f"Could not fetch data for {symbol}: {str(e)}")
    
    # Drop rows with any missing data
    prices = prices.dropna()
    
    if prices.empty:
        raise ValueError("No valid price data found for any symbols")
    
    return prices


def get_current_prices(symbols: List[str]) -> dict:
    """
    Get current (most recent) prices for a list of symbols.
    
    Parameters
    ----------
    symbols : List[str]
        List of stock ticker symbols
    
    Returns
    -------
    dict
        Dictionary mapping symbols to current prices
    """
    current_prices = {}
    
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            # Get most recent price
            hist = ticker.history(period="1d")
            if not hist.empty:
                current_prices[symbol] = hist['Close'].iloc[-1]
            else:
                # Fallback: get from longer period
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current_prices[symbol] = hist['Close'].iloc[-1]
        except Exception as e:
            st.warning(f"Could not fetch current price for {symbol}: {str(e)}")
    
    return current_prices


def validate_symbol(symbol: str) -> bool:
    """
    Validate if a stock symbol exists and has data.
    
    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    
    Returns
    -------
    bool
        True if symbol is valid, False otherwise
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        return not hist.empty
    except:
        return False


def get_stock_info(symbol: str) -> dict:
    """
    Get basic information about a stock.
    
    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    
    Returns
    -------
    dict
        Dictionary with stock information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'currency': info.get('currency', 'USD')
        }
    except:
        return {
            'symbol': symbol,
            'name': symbol,
            'sector': 'N/A',
            'industry': 'N/A',
            'currency': 'USD'
        }


def calculate_data_quality_score(prices: pd.DataFrame) -> float:
    """
    Calculate data quality score based on completeness and length.
    
    Parameters
    ----------
    prices : pd.DataFrame
        Price data
    
    Returns
    -------
    float
        Quality score between 0 and 1
    """
    # Check for sufficient history (prefer 252 trading days = 1 year)
    length_score = min(len(prices) / 252, 1.0)
    
    # Check for completeness (no NaN values)
    completeness_score = 1.0 - (prices.isna().sum().sum() / prices.size)
    
    # Combined score
    quality_score = (length_score * 0.7) + (completeness_score * 0.3)
    
    return quality_score
