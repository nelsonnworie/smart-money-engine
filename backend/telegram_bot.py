"""
telegram_bot.py — Alert delivery
==================================
Fix applied:
  signal_type is now ALWAYS a raw action: BUY | SELL | CLUSTER
  This file builds the display label ONCE.
  analytics.py no longer pre-builds the headline string.

  Before (broken):  analytics builds "SIGNIFICANT WHALE BUY"
                    → Telegram prepends → "SIGNIFICANT WHALE SIGNIFICANT WHALE BUY" ✗

  After (fixed):    analytics passes "BUY"
                    → Telegram builds → "SIGNIFICANT WHALE BUY" ✓
"""

import os
import asyncio
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

TOKEN   = os.getenv("SMART_MONEY_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

CHAIN_EXPLORER = {
    "ethereum": ("Etherscan",  "https://etherscan.io/search?q="),
    "arbitrum": ("Arbiscan",   "https://arbiscan.io/search?q="),
    "base":     ("Basescan",   "https://basescan.org/search?q="),
    "bsc":      ("BscScan",    "https://bscscan.com/search?q="),
    "solana":   ("Solscan",    "https://solscan.io/search?q="),
}

DASHBOARD_URL = os.getenv(
    "DASHBOARD_URL",
    "https://smartmoneyengine.vercel.app/"
)


def _build_header(signal_type: str, score: int) -> str:
    """
    Builds the display label from the raw signal_type.
    signal_type must be: BUY | SELL | CLUSTER
    score determines whale tier.

    This function is the ONLY place display labels are constructed.
    """
    action = signal_type.upper().strip()

    if score >= 90:
        tier = "🐋 MEGA WHALE"
    elif score >= 75:
        tier = "🐳 SIGNIFICANT WHALE"
    else:
        tier = "🐬 WHALE"

    if action == "CLUSTER":
        return f"<b>{tier} CLUSTER DETECTED</b>"
    elif action == "BUY":
        return f"<b>{tier} BUY DETECTED</b>"
    elif action == "SELL":
        return f"<b>{tier} SELL DETECTED</b>"
    else:
        return f"<b>{tier} SIGNAL DETECTED</b>"


async def send_telegram_alert(signal_data: dict):
    score       = signal_data.get("conviction_score", 0)
    raw_token   = signal_data.get("token", "UNKNOWN")
    signal_type = signal_data.get("signal_type", "BUY")   # raw: BUY | SELL | CLUSTER
    amount_usd  = signal_data.get("amount_usd", 0)
    chain       = (signal_data.get("chain", "ethereum") or "ethereum").lower()
    wallet      = signal_data.get("wallet", "")
    insight     = signal_data.get("insight", "")

    token_name = raw_token.lstrip("$").strip()
    amount_str = f"${amount_usd:,.2f}"

    # ── Build header ONCE from raw signal_type ──────────────────────────────
    header = _build_header(signal_type, score)

    # ── Wallet display ──────────────────────────────────────────────────────
    if isinstance(wallet, str) and wallet.startswith("0x") and len(wallet) > 12:
        wallet_display = f"{wallet[:6]}...{wallet[-4:]}"
    else:
        wallet_display = wallet[:30] if len(wallet) > 30 else wallet

    # ── Explorer link ───────────────────────────────────────────────────────
    explorer_name, explorer_base = CHAIN_EXPLORER.get(
        chain, ("Etherscan", "https://etherscan.io/search?q=")
    )
    explorer_url = f"{explorer_base}{token_name}"

    # ── Insight line ────────────────────────────────────────────────────────
    insight_line = f"\n<i>{insight}</i>\n" if insight else "\n"

    # ── Signal label for body ───────────────────────────────────────────────
    signal_label = signal_type.upper()

    message = (
        f"{header}\n\n"
        f"Token:   <code>${token_name}</code>\n"
        f"Signal:  <code>{signal_label}</code>\n"
        f"Amount:  {amount_str}\n"
        f"Chain:   {chain.capitalize()}\n"
        f"Wallet:  <code>{wallet_display}</code>\n"
        f"Score:   {score}/100\n"
        f"{insight_line}"
        f"<a href='{DASHBOARD_URL}/?token={token_name}&chain={chain}&wallet={wallet}'>📊 View Dashboard</a>  "
        f"<a href='{explorer_url}'>🔍 {explorer_name}</a>"
    )

    if not TOKEN or not CHAT_ID:
        print(f"⚠️ Telegram not configured — would have sent:\n{message}")
        return

    bot = Bot(token=TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )
    print(f"✅ Alert sent: ${token_name} {signal_label} {amount_str} (score: {score}/100)")


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