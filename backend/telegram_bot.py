import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Match these exactly to your .env file names
TOKEN = os.getenv("SMART_MONEY_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

async def send_telegram_alert(signal_data):
    # This formats the message for your Telegram alert
    message = (
        f"🚨 *HIGH CONVICTION SIGNAL*\n\n"
        f"🪙 Token: ${signal_data['token']}\n"
        f"📊 Type: {signal_data['signal_type']}\n"
        f"🎯 Score: {signal_data['conviction_score']}/100"
    )
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        print("✅ Telegram alert sent!")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# This part is just for testing the file directly
if __name__ == "__main__":
    test_signal = {
        "token": "TEST",
        "signal_type": "BUY",
        "conviction_score": 99
    }
    asyncio.run(send_telegram_alert(test_signal))