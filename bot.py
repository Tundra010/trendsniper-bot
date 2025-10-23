# bot.py
# bot.py
import asyncio
from typing import List
import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
# removed erroneous top-level await; ensure SCAN_INTERVAL_SECONDS is used inside async functions
from config import DISCORD_TOKEN, DISCORD_CHANNEL_ID, SCAN_INTERVAL_SECONDS
# Local lightweight replacements for missing utils module:
import time
import datetime
from utils import is_market_window, PostedTickerStore, sleep_until_next_cycle
import logging
from scanner import build_universe, scan_once

# Setup logging
logger = logging.getLogger("trendsniper")

logging.basicConfig( level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", )

class PostedTickerStore:
    """In-memory set to track tickers posted during the bot session."""
    def __init__(self):
        self._posted = set()

    def add(self, ticker: str):
        self._posted.add(ticker)

    def contains(self, ticker: str) -> bool:
        return ticker in self._posted

    def clear(self):
        self._posted.clear()

    def to_list(self) -> List[str]:
        return list(self._posted)

def is_market_window() -> bool:
    """Approximate US market hours (Mon-Fri 09:30-16:00 ET) using UTC times (13:30-20:00 UTC).
    This is a conservative approximation that ignores DST nuances but works for short-term testing.
    """
    now = datetime.datetime.utcnow()
    # Weekdays only
    if now.weekday() >= 5:
        return False
    open_utc = now.replace(hour=13, minute=30, second=0, microsecond=0)
    close_utc = now.replace(hour=20, minute=0, second=0, microsecond=0)
    return open_utc <= now <= close_utc

async def sleep_until_next_cycle(interval_seconds: int):
    """Sleep until the next multiple of interval_seconds from the epoch (align scan cycles)."""
    now = time.time()
    next_cycle = ((now // interval_seconds) + 1) * interval_seconds
    delay = max(0.0, next_cycle - now)
    await asyncio.sleep(delay)
import logging
from scanner import build_universe, scan_once
from indicators import compute_indicators
from news_fetcher import extract_headlines_and_catalysts

logging.basicConfig(level=logging.INFO, format="%(asctime)s-%(levelname)s-%(message)s")
logger = logging.getLogger("TrendsniperBot")

intents = discord.Intents.default() 
intents.message_content = True # fine for development; tighten in production
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# state flags
_scanning_enabled = True
_posted_store = PostedTickerStore()
_universe = []
_scan_task = None


@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    # Sync app commands
    try:
        await tree.sync()
        logger.info("App commands synced successfully.")
    except Exception as e:
        logger.warning(f"Error syncing app commands: {e}")
    # Build universe in background
    global _universe, _scan_task
    _universe = await build_universe()
    logger.info(f'Universe loaded: {len(_universe)} symbols.')
    # Start scanning loop
    if _scan_task is None:
        _scan_task = bot.loop.create_task(scanning_loop())
    # send ready message 
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    if channel: 
        try: 
            await channel.send("TrendSniper Bot is now online and ready to scan for opportunities!")
        except Exception as e:
            logger.debug(f"Failed to send ready message: {e}")


async def scanning_loop():
    """Main loop that runs scans every SCAN_INTERVAL_SECONDS during market hours."""
    await bot.wait_until_ready()
    channel = None
    if DISCORD_CHANNEL_ID:
        channel = bot.get_channel(DISCORD_CHANNEL_ID)
    global _scanning_enabled
    while not bot.is_closed():
        try:
            if _scanning_enabled and is_market_window():
                logger.info("Starting scan cycle...")
                # Sleep until aligned cycle
                await sleep_until_next_cycle(SCAN_INTERVAL_SECONDS)
                # perform one scan
                results = await scan_once(_universe, _posted_store)
                if results:
                    for idea in results:
                        # post pretty embed
                        embed = discord.Embed(
                            title=f"TrendSniper Alert - {idea['ticker']}",
                            description=f"Price: ${idea['price']:.4f}",
                            color=discord.Color.green()
                        )
                        embed.add_field(name="Entry", value=f"${idea['entry']}", inline=True)
                        embed.add_field(name="Stop", value=f"${idea['stop']}", inline=True)
                        embed.add_field(name="Take", value=f"${idea['take']}", inline=True)
                        embed.add_field(name="Shares", value=f"{idea['shares']}", inline=True)
                        embed.add_field(name="VWAP", value=f"${idea['vwap']:.4f}", inline=True)
                        embed.add_field(name="MA20 / MA50", value=f"${idea['ma20']:.4f} / {idea['ma50']:.4f}", inline=True)
                        embed.add_field(name="Volume (last/avg)", value=f"{idea['last_volume']} / {idea['avg_volume']}", inline=True)
                        embed.set_footer(text="Filters: Price < $10 . Low-float . High Volume")

                        # news / catalyst 
                        news_list = idea.get("news", [])
                        if idea.get("has_catalyst"):
                            embed.add_field(name="Catalyst", value="Yes - relevant news found", inline=False)
                        elif news_list:
                            embed.add_field(name="News", value=f"{len(news_list)} recent healines", inline=False)

                        if news_list:
                            lines = []
                            for n in news_list[:3]:
                                title = n.get("headline", "")
                                url = n.get("url", "")

                                if url: 
                                    line = f"[{title}]({url})"
                                else:
                                    line = title
                                lines.append(line)
                            embed.add_field(name="Headlines", value="\n".join(lines), inline=False)
                        if channel:
                            try:
                                await channel.send(embed=embed)
                            except Exception as e:
                                logger.warning(f"Failed to send message: {e}")
                else:
                    logger.debug("No signals this cycle.")
            else:
                # not scanning; ensure sleep but keep alive
                logger.debug("Scanning paused or market closed.")
                await asyncio.sleep(10)
        except Exception as e:
            logger.exception(f"Error in scanning loop: {e}")
            await asyncio.sleep(5)

         
@tree.command(name="start", description="Start scanning for trade ideas.")
async def start(interaction: discord.Interaction):
    global _scanning_enabled
    _scanning_enabled = True
    _posted_store.clear()  # Clear posted tickers to allow reposting
    await interaction.response.send_message("Scanning started.", ephemeral=True)

@tree.command(name="pause", description="Stop scanning for trade ideas.")
async def pause(interaction: discord.Interaction):
    global _scanning_enabled
    _scanning_enabled = False
    await interaction.response.send_message("Scanning paused.", ephemeral=True)

@tree.command(name="reset", description="Reset posted tickers a and refresh universe.")
async def reset(interaction: discord.Interaction):
    global _posted_store, _universe
    _posted_store.clear()
    _universe = await build_universe()
    await interaction.response.send_message(f"Posted tickers cleared and universe refreshed symbols).", ephemeral=True)

@tree.command(name="status", description="Get current scanning status.")
async def status(interaction: discord.Interaction):
    import datetime
    nm ="ON" if _scanning_enabled else "OFF"
    env = "Market Window" if is_market_window() else "Outside Market Hours"
    posted_count= len(_universe)
    uni_len =len(_universe)
    txt = f"Scanning: **{nm}**\nwindow: **{env}**\nPosted Tickers: (session): **{posted_count}**\nUniverse size: **{uni_len}**\nTime: {datetime.datetime.now().isoformat()}"
    await interaction.response.send_message(txt, ephemeral=True)


if __name__ == "__main__":
        bot.run(DISCORD_TOKEN)