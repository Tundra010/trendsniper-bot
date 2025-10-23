from dotenv import load_dotenv
import os

load_dotenv()

print("Alpaca key loaded:", bool(os.getenv("ALPACA_API_KEY")))
print("Discord token loaded:", bool(os.getenv("DISCORD_TOKEN")))
print("Channel ID:", os.getenv("DISCORD_CHANNEL_ID"))
