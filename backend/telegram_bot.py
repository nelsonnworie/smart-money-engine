import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

# Configuration
TOKEN = os.getenv("SMART_MONEY_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = Bot(token=TOKEN)

async def send_telegram_alert(signal_data):
    score = signal_data.get('conviction_score', 0)
    
    # 1. Logic for Headers
    if score >= 90:
        header = "🚨🚨 <b>MEGA WHALE MOVEMENT</b> 🚨🚨"
    elif score >= 75:
        header = "🐋 <b>SIGNIFICANT WHALE BUY</b>"
    elif score >= 40:
        header = "👀 <b>WHALE ACTIVITY DETECTED</b>"
    else:
        header = "📈 <b>NEW MARKET SIGNAL</b>"

    # 2. Frontend Link (We will update the actual URL once deployed)
    # Using a placeholder URL for now
    token_name = signal_data['token']
    frontend_url = f"https://smart-money-engine.up.railway.app/details/{token_name}"

    # 3. Message Formatting
    message = (
        f"{header}\n\n"
        f"🪙 <b>Token:</b> ${token_name}\n"
        f"📊 <b>Type:</b> {signal_data['signal_type']}\n"
        f"🎯 <b>Score:</b> {score}/100\n\n"
        f"🔗 <a href='{frontend_url}'>View Details on Dashboard</a>"
    )

    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='HTML')
        print(f"✅ Telegram alert sent with link! (Score: {score})")
    except Exception as e:
        print(f"❌ Telegram error: {e}")

# THIS IS THE PART THAT TRIGGERED THE TEST
if __name__ == "__main__":
    test_signal = {
        "token": "TEST_COIN",
        "signal_type": "BUY",
        "conviction_score": 95
    }
    asyncio.run(send_telegram_alert(test_signal))