from typing import Tuple 
import pandas as pd
import numpy as np 

def compute_ma (series: pd.Series, window: int) -> pd.Series:
    """Compute the moving average of a pandas Series."""
    return series.rolling(window=window, min_periods=1).mean()

def compute_vwap (df: pd.DataFrame) -> pd.Series:
    """Compute the Volume Weighted Average Price (VWAP) for a DataFrame with 'price' and 'volume' columns."""
    q = df['volume']
    p = df['price']
    vwap = (p * q).cumsum() / q.cumsum()
    return vwap

def compute_indicators (df: pd.DataFrame) -> pd.DataFrame:
    """Compute various technical indicators and add them as columns to the DataFrame."""
    df = df.copy()
    df['MA20'] = compute_ma(df['price'], window=20)
    df['MA50'] = compute_ma(df['price'], window=50)
    df['VWAP'] = compute_vwap(df)
    df['Price_Change'] = df['price'].pct_change() * 100  # Percentage price change
    df['Volume_Change'] = df['volume'].pct_change() * 100  # Percentage volume change
    return df

def generate_trade_levels (latest_close: float, latest_vwap: float, latest_ma20: float, risk_percent: float=0.005, profit_multiplier: float=2.0) -> Tuple[float, float, float]:

    """Generate entry, stop-loss, and take-profit levels based on latest indicators."""
  
    base=max(latest_vwap, latest_ma20, latest_close * 0.995)
    entry=round(base * 1.000, 4) 
    stop=round(min(latest_vwap, latest_ma20, latest_close ) * (1 - risk_percent), 4)
    take=round(entry * profit_multiplier, 4)
    return entry, stop, take
