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
    # 1. Dynamic Header based on the Conviction Score
    score = signal_data.get('conviction_score', 0)
    
    if score >= 90:
        header = "🚨🚨 *MEGA WHALE MOVEMENT* 🚨🚨"
    elif score >= 75:
        header = "🐋 *SIGNIFICANT WHALE BUY*"
    elif score >= 40:
        header = "👀 *WHALE ACTIVITY DETECTED*"
    else:
        header = "📈 *NEW MARKET SIGNAL*"

    # 2. Format the message
    message = (
        f"{header}\n\n"
        f"🪙 **Token:** ${signal_data['token']}\n"
        f"📊 **Type:** {signal_data['signal_type']}\n"
        f"🎯 **Score:** {score}/100"
    )

    try:
        # Using Markdown for bold/italics
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
        print(f"✅ Telegram alert sent! (Score: {score})")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# This part is just for testing the file directly
if __name__ == "__main__":
    test_signal = {
        "token": "TEST_COIN",
        "signal_type": "BUY",
        "conviction_score": 95
    }
    asyncio.run(send_telegram_alert(test_signal))