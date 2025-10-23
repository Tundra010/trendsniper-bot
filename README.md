# TrendSniper (Intraday-Alerts) - Alert-only Discord bot

TrendSniper scans US equities (pre-market -> after-hours) and posts intraday alerts to a Discord channel for low-price, high-volume, low-float-like setups. Indicators: VWAP, MA20, MA50. This is an ALERT-ONLY system (no trading.)

### Features 
- Scans during 4:00 am ET to 8:00 pm ET  (pre-market to after-hours)
- Uses Alpaca Market Data API for 1-minute bars
Detects VWAP/MA20/MA50 strength + volume spikes 
- posts formatted embeds to "#intraday-alerts"
- Slash commands: "/start", "/pause", "/reset", "/status"
- Placeholders for Alpaca & Discord credentials (use ".env")

### Setups (macOS / Linux / Windows)
1. Clone or copy the project into a folder "TrendSniper". 
2. Create and activate a virtual environment: 
""" bash 
python3 -m venv .venv 
source .venv/bin/activate # macOS / Linux  
.venv\Scripts\activate # Windows (PowerShell)