from news_fetcher import extract_headlines_and_catalysts
import asyncio 
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.models import Asset
from config import (ALPACA_API_KEY, ALPACA_API_SECRET, ALPACA_DATA_BASE_URL, MAX_RESULTS_PER_SCAN, MIN_AVG_VOLUME, LOW_FLOAT_MILLIONS, )
from indicators import compute_indicators, generate_trade_levels
import logging

# Fallback logger if local 'utils.logger' is not available.
logger = logging.getLogger("scanner")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Create Clients
_data_client = StockHistoricalDataClient(ALPACA_API_KEY, ALPACA_API_SECRET)
_trading_client = TradingClient(ALPACA_API_KEY, ALPACA_API_SECRET, paper=True)



async def build_universe() -> List[str]:
    """Load symbols from symbols.txt - skip Alpaca universe"""
    try:
        with open('symbols.txt', 'r') as f:
            symbols = [line.strip().upper() for line in f if line.strip()]
        print(f'✅ Loaded {len(symbols)} symbols from symbols.txt')
        return symbols
    except Exception as e:
        print(f'❌ Error loading symbols.txt: {e}')
        # Fallback symbols
        return ['AAPL', 'TSLA', 'AMD', 'NVDA', 'MSFT', 'GOOGL', 'META', 'AMZN']


def bars_to_df(bars) -> pd.DataFrame:
    """Convert alpaca bars response to a DataFrame with columns: t (ts), open, high, low, close, volume.
    Input may be the DataFrame from Client.get_stock_bars(request).df"""
    # caller passes pre-filtered df for single symbol; ensure columns exist
    df = bars.copy()
    # normalize columns if needed
    if 'close' not in df.columns:
        df["close"] = df["c"]
    return df

async def fetch_recent_bars(ticker: str, limit: int = 200) -> Optional[pd.DataFrame]:
    """Fetch recent 1-minute bars for a given ticker (includes pre/post).
    Returns pandas DataFrame indexed by timestamp ascending."""
    try:
        request = StockBarsRequest(
            symbol_or_symbols=ticker,
            timeframe=TimeFrame.Minute,
            limit=limit,
            adjustment=None
            )
        bars = _data_client.get_stock_bars(request).df
        # If multiple symbols requested, bars has multiindex; we handle single symbol path
        if (ticker,) in bars.index:
            df = bars.loc[(ticker, )]. copy()
        else:
            df = bars.copy()
        # Keep only necessary columns and ensyre chronological 
        df = df[['open', 'high', 'low', 'close', 'volume']]
        df = df.sort_index()
        df = df.rename(columns={'close': 'close'})
        return df
    except Exception as e:
        logger.error(f"Error fetching bars for {ticker}: {e}")
        return None


async def get_last_trade_price(symbol: str) -> Optional[float]:
    """ 
    Quick latest price fetch via 1 bar (limit=1). Used to filter price < $10"""
    df = await fetch_recent_bars(symbol, limit=5)
    if df is None or df.empty:
        return None
    return float(df['close'].iloc[-1])



async def scan_once(universe: List[str], posted_store, max_results: int = MAX_RESULTS_PER_SCAN) -> List[Dict]:
    """Scan the given universe for candidates that meet filters:
    - Price < $10
    - recent volume spike (current minute volume > avg * 2)
    - MA / VWAP signal: price >vwap and ma20 > ma50
    Return list of trade idea dicts."""
    results = []
    checked = 0
    for symbol in universe:
        if checked >= max_results:
            break
        checked += 1
        try:
            price = await get_last_trade_price(symbol)
            if price is None:
                continue
            if price >= 10:
                continue 
            df = await fetch_recent_bars(symbol, limit=120)
            if df is None or len(df) < 20:
                continue
            df_ind = compute_indicators(df)
            latest = df_ind.iloc[-1]
            latest_close = float(latest['close'])
            latest_vwap = float(latest['VWAP'])
            latest_ma20 = float(latest['MA20'])
            latest_ma50 = float(latest['MA50'])
            # Volume checks: compare last bar volume vs average 20 
            last_vol = float(latest['volume'])
            avg_vol = float(df_ind['volume'].rolling(window=20, min_periods=1).mean().iloc[-1])
            if avg_vol < MIN_AVG_VOLUME:
                continue
            # simple signal: price above vwap and ma20 > ma50 and volume spike 
            if latest_close > latest_vwap and latest_ma20 > latest_ma50 and last_vol > avg_vol * 1.8:
                # Optionally filter low float if you have data (skipped if not provided) 
                if posted_store.has(symbol):
                    continue  
                entry, stop, take = generate_trade_levels(latest_close, latest_vwap, latest_ma20)
                shares = 0 
                risk_per_share = max(0.0001, entry-stop)
                try: 
                    shares = int(float(1000) / risk_per_share)
                except Exception:
                    shares = 0

                headlines, has_catalyst = extract_headlines_and_catalysts(symbol, days_back=5, max_headlines=5)

                idea = {
                    "symbol": symbol,
                    "price": latest_close,
                    "vwap" : latest_vwap,
                    "ma20": latest_ma20,
                    "ma50": latest_ma50,
                    "avg_volume": int(avg_vol),
                    "last_volume": int(last_vol),
                    "entry": entry,
                    "stop": stop,
                    "take": take,
                    "shares": shares,
                    "news": headlines,              # list of dicts with datetime, headline, url, matched
                    "has_catalyst": has_catalyst,
                }
                results.append(idea)
                posted_store.add(symbol)
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            continue
    return results