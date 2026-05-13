import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("SMART_MONEY_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_alert(signal_data):
    """Creates a fresh Bot instance every call to avoid event loop issues."""
    score = signal_data.get('conviction_score', 0)
    token_name = signal_data.get('token', 'UNKNOWN')
    signal_type = signal_data.get('signal_type', 'BUY')
    price = signal_data.get('price', None)
    change_24h = signal_data.get('change_24h', None)
    wallets = signal_data.get('smart_wallets', None)

    if score >= 90:
        header = "⚠️ <b>MEGA WHALE MOVEMENT</b>"
    elif score >= 75:
        header = "🐋 <b>SIGNIFICANT WHALE BUY</b>"
    else:
        header = "<b>WHALE ACTIVITY DETECTED</b>"

    # Optional fields — only appear if passed in signal_data
    price_line = f"💵 <b>Price:</b> ${price}\n" if price else ""
    change_line = (
        f"📈 <b>24h Change:</b> {'+' if change_24h >= 0 else ''}{change_24h}%\n"
        if change_24h is not None else ""
    )
    wallets_line = f"👛 <b>Smart Wallets:</b> {wallets} active\n" if wallets else ""

    message = (
        f"{header}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🪙 <b>Token:</b> <code>${token_name}</code>\n"
        f"📊 <b>Signal:</b> {signal_type.upper()}\n"
        f"{price_line}"
        f"{change_line}"
        f"{wallets_line}"
        f"🎯 <b>Score:</b> {score}/100\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <a href='https://smart-money-engine.up.railway.app/details/{token_name}'>View Details on Dashboard</a>"
    )

    # Create a fresh Bot instance every time — fixes event loop closed error
    bot = Bot(token=TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    print(f"✅ Alert sent: ${token_name} ({score}/100)")


if __name__ == "__main__":
    test_signal = {
        "token": "TURBO",
        "signal_type": "BUY",
        "conviction_score": 85,
        "price": "0.00412",
        "change_24h": 14.3,
        "smart_wallets": 7,
    }
    asyncio.run(send_telegram_alert(test_signal))