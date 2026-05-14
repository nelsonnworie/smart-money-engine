import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY")
HELIUS_KEY    = os.getenv("HELIUS_KEY")

_eth_price_cache = {"price": 2500.0}

CHAIN_IDS = {
    "ethereum": 1,
    "arbitrum": 42161,
    "base":     8453,
    "bsc":      56,
}

STABLECOINS = [
    "USDC", "USDT", "DAI", "BUSD", "TUSD",
    "FRAX", "LUSD", "USDP", "USDS", "FDUSD",
]

SOL_PRICE = 150  # approximate SOL price in USD


def get_eth_price():
    try:
        r = httpx.get(
            "https://api.etherscan.io/v2/api",
            params={
                "chainid": 1,
                "module":  "stats",
                "action":  "ethprice",
                "apikey":  ETHERSCAN_KEY,
            },
            timeout=10.0,
        )
        if r.status_code == 200:
            price = float(r.json().get("result", {}).get("ethusd", 2500))
            _eth_price_cache["price"] = price
            return price
    except Exception:
        pass
    return _eth_price_cache["price"]


def fetch_wallet_transactions(address, chain):
    transactions = []
    try:
        chain_lower = chain.lower()

        # ── EVM chains (Ethereum, Arbitrum, Base, BSC) ───────────────
        if chain_lower in CHAIN_IDS:
            params = {
                "chainid":    CHAIN_IDS[chain_lower],
                "module":     "account",
                "action":     "tokentx",
                "address":    address,
                "startblock": 0,
                "endblock":   99999999,
                "page":       1,
                "offset":     50,
                "sort":       "desc",
                "apikey":     ETHERSCAN_KEY,
            }
            r = httpx.get(
                "https://api.etherscan.io/v2/api",
                params=params,
                timeout=30.0,
            )
            if r.status_code == 200:
                result = r.json()
                if result.get("status") == "1":
                    transactions = result.get("result", [])

        # ── Solana (Helius) ───────────────────────────────────────────
        elif chain_lower == "solana":
            url = (
                f"https://api.helius.xyz/v0/addresses/{address}"
                f"/transactions?api-key={HELIUS_KEY}&limit=50"
            )
            r = httpx.get(url, timeout=30.0)
            if r.status_code == 200:
                transactions = r.json()

    except Exception:
        pass

    return transactions


def parse_transaction(raw_tx, chain="ethereum"):
    try:

        # ── SOLANA PATH ───────────────────────────────────────────────
        # Helius transactions always contain "signature" — EVM never does
        if isinstance(raw_tx, dict) and "signature" in raw_tx:

            timestamp_raw = raw_tx.get("timestamp", 0)
            try:
                dt = datetime.fromtimestamp(
                    int(timestamp_raw), tz=timezone.utc
                ).replace(tzinfo=None)
            except Exception:
                dt = datetime.utcnow()

            # 1. Try SPL token transfers first (USDC, JTO, JUP, etc.)
            for t in raw_tx.get("tokenTransfers", []):
                raw_amount   = float(t.get("tokenAmount", 0) or 0)
                token_symbol = (
                    t.get("tokenSymbol")
                    or t.get("symbol")
                    or t.get("mint", "UNKNOWN")[:8]
                )

                # Stablecoins: amount == USD directly
                if token_symbol in STABLECOINS:
                    amt_usd = raw_amount
                else:
                    # Unknown SPL — conservative $0.01 estimate
                    amt_usd = raw_amount * 0.01

                if amt_usd < 1000000:
                    continue

                return {
                    "tx_hash":    raw_tx.get("signature"),
                    "token":      token_symbol,
                    "amount_usd": round(amt_usd, 2),
                    "action":     "BUY",
                    "timestamp":  dt,
                    "from":       t.get("fromUserAccount", ""),
                    "to":         t.get("toUserAccount",   ""),
                }

            # 2. Fall back to native SOL transfers
            for t in raw_tx.get("nativeTransfers", []):
                lamports   = float(t.get("amount", 0) or 0)
                sol_amount = lamports / 1_000_000_000  # lamports → SOL
                amt_usd    = sol_amount * SOL_PRICE

                if amt_usd < 1000000:
                    continue

                return {
                    "tx_hash":    raw_tx.get("signature"),
                    "token":      "SOL",
                    "amount_usd": round(amt_usd, 2),
                    "action":     "BUY",
                    "timestamp":  dt,
                    "from":       t.get("fromUserAccount", ""),
                    "to":         t.get("toUserAccount",   ""),
                }

            # Nothing above $100k in this Solana transaction
            return None

        # ── EVM PATH (Etherscan token transfers) ──────────────────────
        token        = raw_tx.get("tokenSymbol", "UNKNOWN")
        decimals     = int(raw_tx.get("tokenDecimal", 18) or 18)
        raw_val      = int(raw_tx.get("value", 0) or 0)
        token_amount = raw_val / (10 ** decimals)

        if token in STABLECOINS:
            amt_usd = token_amount
        elif token in ("WETH", "ETH"):
            amt_usd = token_amount * get_eth_price()
        elif token == "WBTC":
            amt_usd = token_amount * 95000
        elif token in ("BNB", "WBNB"):
            amt_usd = token_amount * 600
        else:
            amt_usd = token_amount * 0.01

        if amt_usd < 1000000:
            return None

        timestamp_raw = raw_tx.get("timeStamp", "")
        try:
            dt = datetime.fromtimestamp(
                int(timestamp_raw), tz=timezone.utc
            ).replace(tzinfo=None)
        except Exception:
            dt = datetime.utcnow()

        return {
            "tx_hash":    raw_tx.get("hash"),
            "token":      token,
            "amount_usd": round(amt_usd, 2),
            "action":     "BUY",
            "timestamp":  dt,
            "from":       raw_tx.get("from", "").lower(),
            "to":         raw_tx.get("to",   "").lower(),
        }

    except Exception:
        return None


# ── TEST ──────────────────────────────────────────────────────────────
if __name__ == "__main__":

    print(f"ETH Price: ${get_eth_price():.2f}")

    # Test EVM wallet
    evm_address = "0x47ac0fb4f2d84898e4d9e7b4dab3c24507a6d503"
    print(f"\nTesting EVM wallet: {evm_address}")
    raw_evm = fetch_wallet_transactions(evm_address, "ethereum")
    print(f"Raw EVM transfers: {len(raw_evm)}")
    cleaned_evm = [p for p in (parse_transaction(t) for t in raw_evm) if p]
    print(f"High-value EVM (>$1m): {len(cleaned_evm)}")
    for tx in cleaned_evm[:3]:
        print(f"  {tx['action']} {tx['token']} ${tx['amount_usd']:,.2f} at {tx['timestamp']}")

    # Test Solana wallet
    sol_address = "DEXCD63uBftz5TTyRJqqgmPA1sidnYrGToKoXTwfgywo"
    print(f"\nTesting Solana wallet: {sol_address}")
    raw_sol = fetch_wallet_transactions(sol_address, "solana")
    print(f"Raw Solana transactions: {len(raw_sol)}")
    cleaned_sol = [p for p in (parse_transaction(t) for t in raw_sol) if p]
    print(f"High-value Solana (>$1m): {len(cleaned_sol)}")
    for tx in cleaned_sol[:3]:
        print(f"  {tx['action']} {tx['token']} ${tx['amount_usd']:,.2f} at {tx['timestamp']}")