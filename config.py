# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Alpaca API credentials
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", os.getenv("APCA_API_KEY_ID", "YOUR_ALPACA_API_KEY"))
ALPACA_API_SECRET = os.getenv("ALPACA_API_SECRET", os.getenv("APCA_API_SECRET_KEY", "YOUR_ALPACA_API_SECRET"))
ALPACA_DATA_BASE_URL = "https://data.alpaca.markets/v2"

# Finnhub for news
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "YOUR_FINNHUB_API_KEY")

# Discord
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "YOUR_DISCORD_BOT_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))

# Bot settings
CAPITAL_PER_TRADE = float(os.getenv("CAPITAL_PER_TRADE", "1000"))
MAX_RESULTS_PER_SCAN = int(os.getenv("MAX_RESULTS_PER_SCAN", "25"))
MIN_AVG_VOLUME = int(os.getenv("MIN_AVG_VOLUME", "100000"))
LOW_FLOAT_MILLIONS = float(os.getenv("LOW_FLOAT_MILLIONS", "20"))
SCAN_INTERVAL_SECONDS = int(os.getenv("SCAN_INTERVAL_SECONDS", "60"))

# News filter settings
NEWS_LOOKBACK_HOURS = int(os.getenv("NEWS_LOOKBACK_HOURS", "6"))
MIN_NEWS_SENTIMENT = float(os.getenv("MIN_NEWS_SENTIMENT", "0.0"))

# Market hours window (ET)
PRE_MARKET_OPEN_HOUR = 4   # 4:00 AM ET
AFTER_HOURS_CLOSE_HOUR = 20  # 8:00 PM ET

ALPACA_DATA_BASE_URL = "https://data.alpaca.markets/v2"
ALPACA_DATA_BASE_URL = "https://data.alpaca.markets/v2"

ALPACA_DATA_BASE_URL = "https://data.alpaca.markets/v2"
