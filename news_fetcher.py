import os 
import requests 
import datetime
from typing import List, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

KEYWORDS = ["acquire", "acquisition", "merger", "buyout", "earnings", "beat", "misses", "quarter", "q1", "q2", "q3", "q4", "revenue", "guidance", "forecast", "upgrade", "downgrade", "FDA", "approval", "contract", "partnership", "deal", "listing", "bankruptcy", "delisting", "short", "scandal", "lawsuit", "launch", "contract", "supply", "demand", "growth", "loss", "profit", "dividend", "split", "insider", "buy", "sell", "CEO", "CFO", "CTO", "resign", "retire", "appoint", "appoints", "investigation", "regulation", "fine", "penalty", "settlement", "recall", "outbreak", "pandemic", "cyberattack", "hack", "data breach", "ransomware", "inflation", "interest rate", "fed", "economy", "GDP", "unemployment", "jobs report", "CPI", "PPI", "trade war", "tariff", "sanction", "embargo", "geopolitical", "conflict", "war", "crisis", "natural disaster", "earthquake", "hurricane", "flood", "wildfire", "drought", "supply chain", "logistics", "shipping", "transportation", "trial", "settlement", "verdict", "court", "lawsuit", "regulation", "compliance", "audit", "investigation", "whistleblower", "insider trading", "SEC", "FTC", "FDA", "EPA", "OSHA"]

def _finnhub_company_news(ticker: str, days_back: int = 7) -> List[Dict]:
    """ Fetch company news for 'symbol' from Finnhub for the last 'days_back' days. 
    Returns a list of news items (dicts) or empty list on failure."""
    if not FINNHUB_API_KEY:
        return []
    
    to_date =  datetime.date.today()
    from_date = to_date - datetime.timedelta(days=days_back)
    url = "https://finnhub.io/api/v1/company-news"
    params = {
        "symbol": ticker,
        "from": from_date.isoformat(),
        "to": to_date.isoformat(),
        "token": FINNHUB_API_KEY
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, list):
            return data
        return []
    except Exception: 
        return []
    
def extract_headlines_and_catalysts(symbol: str, days_back: int = 7, max_headlines: int = 5) -> Tuple[List[Dict], bool]:
    """ 
    Returns (headlines, has_catalyst) where:
    - headlines: list of dicts {"datetime":..., "headline":..., "url":...}
    - has_catalyst: True if any headline matched KEYWORDS"""

    raw = _finnhub_company_news(symbol, days_back=days_back)
    headlines = []
    has_catalyst = False
    seen_titles = set()
    for item in raw:

        title = item.get("headline") or item.get("summary") or ""
        if not title: 
            continue
        seen_titles.add(title)
        dt_unix = item.get("datetime")
        dt = None
        try:
            if dt_unix:
                dt = datetime.datetime.fromtimestamp(int(dt_unix))
        except Exception:
            dt = None
        url = item.get("url", "")
        tl = title.lower()
        matched = any(kw.lower() in tl for kw in KEYWORDS)
        if matched:
            has_catalyst = True
        headlines.append({"datetime": dt, "headline": title, "url": url, "matched": matched})
        if len(headlines) >= max_headlines:
            break
    return headlines, has_catalyst
