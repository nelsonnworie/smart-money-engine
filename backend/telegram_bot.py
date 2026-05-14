import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.getenv("SMART_MONEY_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_alert(signal_data):
    score        = signal_data.get('conviction_score', 0)
    token_name   = signal_data.get('token', 'UNKNOWN')
    signal_type  = signal_data.get('signal_type', 'BUY')
    amount_usd   = signal_data.get('amount_usd', 0)
    chain        = signal_data.get('chain', 'ethereum').capitalize()
    wallet       = signal_data.get('wallet', '')

    # Format dollar amount — e.g. $1,240,000.00
    amount_str = f"${amount_usd:,.2f}"

    if score >= 90:
        header = f"<b>MEGA WHALE {signal_type}</b>"
    elif score >= 75:
        header = f"<b>SIGNIFICANT WHALE {signal_type}</b>"
    else:
        header = f"<b>WHALE {signal_type} DETECTED</b>"

    # Truncate wallet for display
    wallet_display = (
        f"{wallet[:6]}...{wallet[-4:]}" if len(wallet) > 12 else wallet
    )

    message = (
        f"{header}\n\n"
        f"Token:   <code>${token_name}</code>\n"
        f"Amount:  <b>{amount_str}</b>\n"
        f"Chain:   {chain}\n"
        f"Wallet:  <code>{wallet_display}</code>\n"
        f"Score:   {score}/100\n\n"
        f"<a href='https://etherscan.io/search?q={token_name}'>"
        f"View on Etherscan</a>"
    )

    bot = Bot(token=TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    print(f"✅ Alert sent: ${token_name} {amount_str} ({score}/100)")


if __name__ == "__main__":
    asyncio.run(send_telegram_alert({
        "token":           "ETH",
        "signal_type":     "BUY",
        "conviction_score": 85,
        "amount_usd":      320000,
        "chain":           "ethereum",
        "wallet":          "0x9845e1909dca337944a0272f1f9f7249833d2d19",
    }))