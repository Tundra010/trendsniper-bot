# utils.py
import datetime
import pytz
import asyncio
import logging

US_EAST = pytz.timezone("US/Eastern")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("trendsniper")

def now_et():
    """Return timezone-aware current time in US/Eastern."""
    return datetime.datetime.now(US_EAST)

def is_market_window(now=None):
    """Return True if within pre-market (4:00 ET) to after-hours (20:00 ET)."""
    if now is None:
        now = now_et()
    t = now.time()
    start = datetime.time(hour=4, minute=0)
    end = datetime.time(hour=20, minute=0)
    return start <= t <= end

async def sleep_until_next_cycle(interval_seconds):
    """Sleep until the next interval boundary so scans align to :00,:60 etc."""
    now = datetime.datetime.now()
    seconds = now.second + now.microsecond / 1_000_000
    delay = interval_seconds - (seconds % interval_seconds)
    await asyncio.sleep(delay)

# Simple in-memory persistence for posted tickers to avoid duplicate posts in same session
class PostedTickerStore:
    def __init__(self):
        self._posted = set()

    def has(self, symbol):
        return symbol in self._posted

    def add(self, symbol):
        self._posted.add(symbol)

    def clear(self):
        self._posted.clear()