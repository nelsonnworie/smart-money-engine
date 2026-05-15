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

STABLECOINS = ["USDC", "USDT", "DAI", "BUSD", "TUSD", "FRAX", "LUSD", "USDP", "USDS", "FDUSD"]

# Known token prices (update periodically or hook to live API)
KNOWN_PRICES = {
    "PEPE":   0.0000142,
    "SHIB":   0.0000248,
    "DOGE":   0.38,
    "FLOKI":  0.000195,
    "AKITA":  0.0000003,
    "VOLT":   0.00000025,
    "XEN":    0.000000006,
    "FREE":   0.000004,
    "RIZO":   0.0000018,
    "STARL":  0.00000014,
}

# ─── MAX REALISTIC USD CAP ──────────────────────────────────────────────────
# Any single token transfer above this is almost certainly a garbage/broken
# price × huge supply situation. We reject it rather than alert on it.
MAX_REALISTIC_USD   = 50_000_000   # $50M single-tx cap
MIN_ALERT_USD       = 1_000_000    # minimum $1M to be worth tracking


def get_eth_price() -> float:
    now = time.time()
    if now - _eth_price_cache["last_update"] < 300:
        return _eth_price_cache["price"]
    try:
        r = httpx.get(
            "https://api.etherscan.io/v2/api",
            params={"chainid": 1, "module": "stats", "action": "ethprice",
                    "apikey": ETHERSCAN_KEY},
            timeout=8,
        )
        if r.status_code == 200:
            price = float(r.json().get("result", {}).get("ethusd", 2500))
            _eth_price_cache.update({"price": price, "last_update": now})
            return price
    except Exception:
        pass
    return _eth_price_cache["price"]


def get_token_price(token_symbol: str) -> float:
    token = token_symbol.upper().replace("$", "").strip()
    now = time.time()

    # Cache hit (10 min)
    if token in _price_cache and now - _price_cache[token][1] < 600:
        return _price_cache[token][0]

    if token in STABLECOINS:
        price = 1.0
    elif token in ("WETH", "ETH"):
        price = get_eth_price()
    elif token == "WBTC":
        price = 95_000.0
    elif token in ("BNB", "WBNB"):
        price = 600.0
    elif token in KNOWN_PRICES:
        price = KNOWN_PRICES[token]
    else:
        # Unknown token → return 0 so amount_usd will be 0 and gets filtered out.
        # This prevents garbage quadrillion-supply tokens from producing fake $B amounts.
        price = 0.0

    _price_cache[token] = (price, now)
    return price


def fetch_wallet_transactions(address: str, chain: str) -> list:
    transactions = []
    try:
        chain_lower = chain.lower()
        if chain_lower in CHAIN_IDS:
            params = {
                "chainid": CHAIN_IDS[chain_lower],
                "module":  "account",
                "action":  "tokentx",
                "address": address,
                "startblock": 0,
                "endblock":   99_999_999,
                "page":   1,
                "offset": 50,
                "sort":   "desc",
                "apikey": ETHERSCAN_KEY,
            }
            r = httpx.get("https://api.etherscan.io/v2/api", params=params, timeout=30)
            if r.status_code == 200 and r.json().get("status") == "1":
                transactions = r.json().get("result", [])

        elif chain_lower == "solana":
            url = (
                f"https://api.helius.xyz/v0/addresses/{address}/transactions"
                f"?api-key={HELIUS_KEY}&limit=50"
            )
            r = httpx.get(url, timeout=30)
            if r.status_code == 200:
                transactions = r.json()

    except Exception:
        pass

    return transactions


def parse_transaction(raw_tx: dict, chain: str = "ethereum") -> dict | None:
    """
    Parse a raw Etherscan ERC-20 token-transfer into our internal format.
    Returns None if the transaction should be ignored.
    """
    try:
        # Skip Solana for now (different schema)
        if isinstance(raw_tx, dict) and "signature" in raw_tx:
            return None

        token_symbol = raw_tx.get("tokenSymbol", "UNKNOWN")
        token = token_symbol.upper().replace("$", "").strip()

        decimals  = int(raw_tx.get("tokenDecimal", 18) or 18)
        raw_val   = int(raw_tx.get("value", 0) or 0)

        # Sanity guard: some tokens report 0 decimals; treat as 18 minimum
        if decimals < 0 or decimals > 30:
            decimals = 18

        token_amount = raw_val / (10 ** decimals)

        price    = get_token_price(token)
        amt_usd  = token_amount * price

        # ── CRITICAL FILTER ─────────────────────────────────────────────────
        # If price is unknown (0) or the USD value is out of realistic range,
        # silently drop this tx.  This kills the $1.5 quadrillion alerts.
        if price == 0:
            return None
        if amt_usd < MIN_ALERT_USD or amt_usd > MAX_REALISTIC_USD:
            return None
        # ────────────────────────────────────────────────────────────────────

        # Timestamp
        dt = datetime.utcnow()
        try:
            dt = datetime.fromtimestamp(
                int(raw_tx.get("timeStamp", 0)), tz=timezone.utc
            ).replace(tzinfo=None)
        except Exception:
            pass

        return {
            "tx_hash":    raw_tx.get("hash"),
            "token":      f"${token}",   # normalise to "$TOKEN" form
            "amount_usd": round(amt_usd, 2),
            "action":     "TRANSFER",    # collector will reclassify to BUY/SELL
            "timestamp":  dt,
            "from":       raw_tx.get("from", "").lower(),
            "to":         raw_tx.get("to",   "").lower(),
        }

    except Exception:
        return None


if __name__ == "__main__":
    print(f"ETH Price: ${get_eth_price():.2f}")
    print("Fetcher ready — unknown tokens return price=0 and are silently dropped.")