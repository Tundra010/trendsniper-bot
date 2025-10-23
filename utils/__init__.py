import asyncio
import datetime
import pytz

# ───────────────────────────────────────────────
# Sleep helper: aligns scanning cycle intervals
# ───────────────────────────────────────────────
async def sleep_until_next_cycle(interval_seconds: int = 60):
    """
    Sleeps until the next scan interval to keep scan timing consistent.
    """
    now = datetime.datetime.now(pytz.UTC)
    seconds_since_minute = now.second + now.microsecond / 1_000_000
    remainder = interval_seconds - (seconds_since_minute % interval_seconds)
    await asyncio.sleep(remainder)

# ───────────────────────────────────────────────
# Market window checker (pre/post-market inclusive)
# ───────────────────────────────────────────────
def is_market_window() -> bool:
    """
    Returns True if current time is within 4 AM – 8 PM Eastern (pre, reg, after hours)
    """
    now = datetime.datetime.now(pytz.timezone("US/Eastern"))
    market_open = now.replace(hour=4, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=20, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close

# ───────────────────────────────────────────────
# Logger utility
# ───────────────────────────────────────────────
def logger(msg: str):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}")

# ───────────────────────────────────────────────
# Simple memory store for tickers already posted
# ───────────────────────────────────────────────
class PostedTickerStore:
    def __init__(self):
        self._posted = set()

    def add(self, symbol: str):
        self._posted.add(symbol)

    def has(self, symbol: str) -> bool:
        return symbol in self._posted
