import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import time

load_dotenv()

ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY")
HELIUS_KEY    = os.getenv("HELIUS_KEY")

_eth_price_cache = {"price": 2500.0, "last_update": 0}
_price_cache = {}

CHAIN_IDS = {"ethereum": 1, "arbitrum": 42161, "base": 8453, "bsc": 56}

STABLECOINS = [
    "USDC", "USDT", "DAI", "BUSD", "TUSD",
    "FRAX", "LUSD", "USDP", "USDS", "FDUSD",
    "USDE", "PYUSD", "GUSD", "HUSD", "SUSD",
]

# Only obvious scam/exploit tokens — NOT meme coins
BLOCKLIST = [
    "TRUMPTROLL", "XDOGE", "KISHU", "XD",
    "CHUD", "BAD", "DTOKEN", "PEIPEI",
    "4CHAN", "XEN", "STARL", "FAERIEDRAGON",
    "BIDEN", "HQG", "ETHF", "ETHG",
    "AF1", "AFO", "ETHFATHER",
    # Wrapped tokens — not trading signals
    "WETH", "WBTC", "WBNB", "WMATIC", "WAVAX",
]

MAX_REALISTIC_USD = 50_000_000   # $50M cap — above this is almost certainly bad data
MIN_ALERT_USD     = 50_000       # $50k minimum — catches real whale moves

# Live prices — update these weekly or connect to a price API later
KNOWN_PRICES = {
    # Major tokens
    "ETH":    2300.0,
    "BTC":    95000.0,
    "SOL":    150.0,
    "BNB":    600.0,
    # DeFi blue chips
    "LINK":   14.0,
    "UNI":    7.0,
    "AAVE":   150.0,
    "CRV":    0.35,
    "LDO":    1.0,
    "MKR":    1500.0,
    "SNX":    1.8,
    "COMP":   50.0,
    "BAL":    2.5,
    "SUSHI":  0.8,
    # L2 / ecosystem
    "ARB":    0.45,
    "OP":     0.90,
    "MATIC":  0.35,
    "IMX":    0.90,
    "STRK":   0.35,
    # Perps / trading
    "GMX":    18.0,
    "GNS":    1.8,
    "DYDX":   0.80,
    # Yield / liquid staking
    "PENDLE": 1.50,
    "EIGEN":  1.80,
    "RPL":    8.0,
    "FXS":    2.5,
    # RWA / institutional
    "ONDO":   0.85,
    "CFG":    0.45,
    "USUAL":  0.12,
    # AI / data
    "GRT":    0.12,
    "ARKM":   1.20,
    "FET":    1.10,
    "OCEAN":  0.35,
    "SXT":    0.06,
    # Gaming / NFT
    "GALA":   0.018,
    "IMX":    0.90,
    "MAGIC":  0.35,
    # Meme (still trackable — big meme moves ARE news)
    "PEPE":   0.0000142,
    "SHIB":   0.0000248,
    "DOGE":   0.38,
    "FLOKI":  0.000195,
    "BONK":   0.000018,
    "WIF":    1.50,
    "TURBO":  0.004,
    # Other commonly traded
    "JASMY":  0.016,
    "WLFI":   0.045,
    "REQ":    0.08,
    "ATA":    0.05,
    "JTO":    2.50,
    "JUP":    0.55,
    "GALA":   0.018,
    "GRT":    0.12,
}


def get_eth_price() -> float:
    now = time.time()
    if now - _eth_price_cache["last_update"] < 300:
        return _eth_price_cache["price"]
    try:
        r = httpx.get(
            "https://api.etherscan.io/v2/api",
            params={
                "chainid": 1,
                "module":  "stats",
                "action":  "ethprice",
                "apikey":  ETHERSCAN_KEY,
            },
            timeout=8,
        )
        if r.status_code == 200:
            price = float(r.json().get("result", {}).get("ethusd", 2500))
            _eth_price_cache.update({"price": price, "last_update": now})
            # Also update KNOWN_PRICES so ETH price stays fresh
            KNOWN_PRICES["ETH"] = price
            return price
    except Exception:
        pass
    return _eth_price_cache["price"]


def get_token_price(token_symbol: str) -> float:
    token = token_symbol.upper().replace("$", "").strip()
    now   = time.time()

    if token in _price_cache and now - _price_cache[token][1] < 600:
        return _price_cache[token][0]

    if token in STABLECOINS:
        price = 1.0
    elif token in ("ETH",):
        price = get_eth_price()
    elif token in KNOWN_PRICES:
        price = KNOWN_PRICES[token]
    else:
        # Unknown token — return 0 so it gets filtered out silently
        price = 0.0

    _price_cache[token] = (price, now)
    return price


def fetch_wallet_transactions(address: str, chain: str) -> list:
    transactions = []
    try:
        chain_lower = chain.lower()

        if chain_lower in CHAIN_IDS:
            params = {
                "chainid":    CHAIN_IDS[chain_lower],
                "module":     "account",
                "action":     "tokentx",
                "address":    address,
                "startblock": 0,
                "endblock":   99_999_999,
                "page":       1,
                "offset":     100,   # fetch last 100 transactions
                "sort":       "desc",
                "apikey":     ETHERSCAN_KEY,
            }
            r = httpx.get(
                "https://api.etherscan.io/v2/api",
                params=params,
                timeout=30,
            )
            if r.status_code == 200 and r.json().get("status") == "1":
                transactions = r.json().get("result", [])

        elif chain_lower == "solana":
            url = (
                f"https://api.helius.xyz/v0/addresses/{address}"
                f"/transactions?api-key={HELIUS_KEY}&limit=100"
            )
            r = httpx.get(url, timeout=30)
            if r.status_code == 200:
                transactions = r.json()

    except Exception:
        pass

    return transactions


def parse_transaction(raw_tx: dict, chain: str = "ethereum"):
    try:
        # ── Solana path ───────────────────────────────────────────────
        if isinstance(raw_tx, dict) and "signature" in raw_tx:
            timestamp_raw = raw_tx.get("timestamp", 0)
            try:
                dt = datetime.fromtimestamp(
                    int(timestamp_raw), tz=timezone.utc
                ).replace(tzinfo=None)
            except Exception:
                dt = datetime.now(timezone.utc).replace(tzinfo=None)

            # Try SPL token transfers
            for t in raw_tx.get("tokenTransfers", []):
                raw_amount   = float(t.get("tokenAmount", 0) or 0)
                token_symbol = (
                    t.get("tokenSymbol")
                    or t.get("symbol")
                    or t.get("mint", "UNKNOWN")[:8]
                )
                token = token_symbol.upper().replace("$", "").strip()

                if token in STABLECOINS:
                    amt_usd = raw_amount
                else:
                    price = get_token_price(token)
                    if price == 0:
                        continue
                    amt_usd = raw_amount * price

                if amt_usd < MIN_ALERT_USD or amt_usd > MAX_REALISTIC_USD:
                    continue

                return {
                    "tx_hash":    raw_tx.get("signature"),
                    "token":      token,
                    "amount_usd": round(amt_usd, 2),
                    "action":     "TRANSFER",
                    "timestamp":  dt,
                    "from":       t.get("fromUserAccount", ""),
                    "to":         t.get("toUserAccount", ""),
                }

            # Try native SOL transfers
            SOL_PRICE = get_token_price("SOL")
            for t in raw_tx.get("nativeTransfers", []):
                lamports   = float(t.get("amount", 0) or 0)
                sol_amount = lamports / 1_000_000_000
                amt_usd    = sol_amount * SOL_PRICE

                if amt_usd < MIN_ALERT_USD or amt_usd > MAX_REALISTIC_USD:
                    continue

                return {
                    "tx_hash":    raw_tx.get("signature"),
                    "token":      "SOL",
                    "amount_usd": round(amt_usd, 2),
                    "action":     "TRANSFER",
                    "timestamp":  dt,
                    "from":       t.get("fromUserAccount", ""),
                    "to":         t.get("toUserAccount", ""),
                }
            return None

        # ── EVM path (Etherscan) ──────────────────────────────────────
        token_symbol = raw_tx.get("tokenSymbol", "UNKNOWN")
        token        = token_symbol.upper().replace("$", "").strip()

        # Skip stablecoins and blocklisted tokens before any calculation
        if token in STABLECOINS or token in BLOCKLIST:
            return None

        decimals = int(raw_tx.get("tokenDecimal", 18) or 18)
        if decimals < 0 or decimals > 30:
            decimals = 18

        raw_val      = int(raw_tx.get("value", 0) or 0)
        token_amount = raw_val / (10 ** decimals)

        price   = get_token_price(token)
        amt_usd = token_amount * price

        # Drop unknown tokens and out-of-range amounts
        if price == 0:
            return None
        if amt_usd < MIN_ALERT_USD or amt_usd > MAX_REALISTIC_USD:
            return None

        # Timestamp
        dt = datetime.now(timezone.utc).replace(tzinfo=None)
        try:
            dt = datetime.fromtimestamp(
                int(raw_tx.get("timeStamp", 0)), tz=timezone.utc
            ).replace(tzinfo=None)
        except Exception:
            pass

        return {
            "tx_hash":    raw_tx.get("hash"),
            "token":      token,
            "amount_usd": round(amt_usd, 2),
            "action":     "TRANSFER",
            "timestamp":  dt,
            "from":       raw_tx.get("from", "").lower(),
            "to":         raw_tx.get("to",   "").lower(),
        }

    except Exception:
        return None


if __name__ == "__main__":
    print(f"ETH Price: ${get_eth_price():.2f}")

    # Test ETH wallet
    test_address = "0x9845e1909dca337944a0272f1f9f7249833d2d19"
    print(f"\nTesting EVM: {test_address}")
    raw = fetch_wallet_transactions(test_address, "ethereum")
    print(f"Raw transfers returned: {len(raw)}")
    cleaned = [p for p in (parse_transaction(t) for t in raw) if p]
    print(f"Whale moves (>$50k): {len(cleaned)}")
    for tx in cleaned[:5]:
        print(f"  {tx['action']} {tx['token']} ${tx['amount_usd']:,.2f} at {tx['timestamp']}")

    # Test Solana wallet
    sol_address = "DEXCD63uBftz5TTyRJqqgmPA1sidnYrGToKoXTwfgywo"
    print(f"\nTesting Solana: {sol_address}")
    raw_sol = fetch_wallet_transactions(sol_address, "solana")
    print(f"Raw Solana txs: {len(raw_sol)}")
    cleaned_sol = [p for p in (parse_transaction(t) for t in raw_sol) if p]
    print(f"Solana whale moves (>$50k): {len(cleaned_sol)}")
    for tx in cleaned_sol[:3]:
        print(f"  {tx['action']} {tx['token']} ${tx['amount_usd']:,.2f}")