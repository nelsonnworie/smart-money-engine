import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.getenv("SMART_MONEY_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def send_telegram_alert(signal_data):
    score        = signal_data.get('conviction_score', 0)
    raw_token    = signal_data.get('token', 'UNKNOWN')
    signal_type  = signal_data.get('signal_type', 'BUY')
    amount_usd   = signal_data.get('amount_usd', 0)
    chain        = signal_data.get('chain', 'ethereum').capitalize()
    wallet       = signal_data.get('wallet', '')
    insight      = signal_data.get('insight', '')

    token_name = raw_token.lstrip('$').strip()
    amount_str = f"${amount_usd:,.2f}"

    if score >= 90:
        header = f"<b>MEGA WHALE {signal_type}</b>"
    elif score >= 75:
        header = f"<b>SIGNIFICANT WHALE {signal_type}</b>"
    else:
        header = f"<b>WHALE {signal_type} DETECTED</b>"

    if isinstance(wallet, str) and wallet.startswith("0x") and len(wallet) > 12:
        wallet_display = f"{wallet[:6]}...{wallet[-4:]}"
    else:
        wallet_display = wallet

    chain_lower = chain.lower()
    explorer_urls = {
        'ethereum': f"https://etherscan.io/search?q={token_name}",
        'arbitrum': f"https://arbiscan.io/search?q={token_name}",
        'base':     f"https://basescan.org/search?q={token_name}",
        'bsc':      f"https://bscscan.com/search?q={token_name}",
        'solana':   f"https://solscan.io/search?q={token_name}",
    }
    explorer_labels = {
        'ethereum': 'View on Etherscan',
        'arbitrum': 'View on Arbiscan',
        'base':     'View on Basescan',
        'bsc':      'View on BscScan',
        'solana':   'View on Solscan',
    }
    explorer_url   = explorer_urls.get(chain_lower, explorer_urls['ethereum'])
    explorer_label = explorer_labels.get(chain_lower, 'View on Etherscan')

    insight_line = f"\n<i>{insight}</i>\n" if insight else "\n"

    message = (
        f"{header}\n\n"
        f"Token:   <code>${token_name}</code>\n"
        f"Signal:  <code>{signal_type}</code>\n"
        f"Amount:  {amount_str}\n"
        f"Chain:   {chain}\n"
        f"Wallet:  <code>{wallet_display}</code>\n"
        f"Score:   {score}/100\n"
        f"{insight_line}"
        f"<a href='https://v0-project-seven-amber-60.vercel.app/?token={token_name}&chain={chain_lower}&wallet={wallet}'>View on Dashboard</a>\n"
        f"<a href='{explorer_url}'>{explorer_label}</a>"
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
        "token":            "ETH",
        "signal_type":      "BUY",
        "conviction_score": 85,
        "amount_usd":       3_200_000,
        "chain":            "ethereum",
        "wallet":           "0x9845e1909dca337944a0272f1f9f7249833d2d19",
        "insight":          "Wallet has been right on 7 of the last 9 major entries.",
    }))