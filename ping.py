# ping.py
from flask import Flask
import threading
import bot  # this imports your Discord bot file (bot.py)

app = Flask(__name__)

@app.route("/ping")
def ping():
    return "Bot is alive!", 200

def run_flask():
    app.run(host="0.0.0.0", port=5000)

threading.Thread(target=run_flask).start()

# Start your Discord bot
bot.run()
