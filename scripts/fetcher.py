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

BLOCKLIST = [
    "TRUMPTROLL", "XDOGE", "KISHU", "WOJAK", "XD", "AKITA",
    "CONAN", "FREE", "VOLT", "CHUD", "BAD", "DTOKEN", "PEIPEI",
    "4CHAN", "XEN", "STARL", "FAERIEDRAGON", "BIDEN", "HQG",
]

MAX_REALISTIC_USD = 50_000_000
MIN_ALERT_USD     = 100_000

KNOWN_PRICES = {
    "PEPE":  0.0000142,
    "SHIB":  0.0000248,
    "DOGE":  0.38,
    "FLOKI": 0.000195,
    "LINK":  14.0,
    "UNI":   7.0,
    "AAVE":  80.0,
    "CRV":   0.35,
    "LDO":   1.0,
    "ARB":   0.45,
    "OP":    0.90,
    "GMX":   18.0,
    "JTO":   2.50,
    "JUP":   0.55,
    "PENDLE":1.50,
    "EIGEN": 1.80,
    "ONDO":  0.85,
    "GRT":   0.12,
    "ARKM":  1.20,
    "TURBO": 0.004,
    "GALA":  0.018,
    "JASMY": 0.016,
    "WLFI":  0.045,
    "REQ":   0.08,
    "ATA":   0.05,
    "SXT":   0.06,
    "USUAL": 0.12,
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
    elif token in ("WETH", "ETH"):
        price = get_eth_price()
    elif token == "WBTC":
        price = 95_000.0
    elif token in ("BNB", "WBNB"):
        price = 600.0
    elif token == "SOL":
        price = 150.0
    elif token in KNOWN_PRICES:
        price = KNOWN_PRICES[token]
    else:
        # Unknown token — return 0 so it gets filtered out
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
                "offset":     50,
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
                f"/transactions?api-key={HELIUS_KEY}&limit=50"
            )
            r = httpx.get(url, timeout=30)
            if r.status_code == 200:
                transactions = r.json()

    except Exception:
        pass

    return transactions


def parse_transaction(raw_tx: dict, chain: str = "ethereum"):
    try:
        # Skip Solana (different schema — handled separately)
        if isinstance(raw_tx, dict) and "signature" in raw_tx:
            return None

        token_symbol = raw_tx.get("tokenSymbol", "UNKNOWN")
        token        = token_symbol.upper().replace("$", "").strip()

        # Skip stablecoins and blocklisted tokens BEFORE any calculation
        if token in STABLECOINS or token in BLOCKLIST:
            return None

        decimals = int(raw_tx.get("tokenDecimal", 18) or 18)
        if decimals < 0 or decimals > 30:
            decimals = 18

        raw_val      = int(raw_tx.get("value", 0) or 0)
        token_amount = raw_val / (10 ** decimals)

        price   = get_token_price(token)
        amt_usd = token_amount * price

        # Drop unknown tokens (price == 0) and out-of-range amounts
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
            "token":      token,           # clean format e.g. "ETH" not "$ETH"
            "amount_usd": round(amt_usd, 2),
            "action":     "TRANSFER",      # collector reclassifies to BUY/SELL
            "timestamp":  dt,
            "from":       raw_tx.get("from", "").lower(),
            "to":         raw_tx.get("to",   "").lower(),
        }

    except Exception:
        return None


if __name__ == "__main__":
    print(f"ETH Price: ${get_eth_price():.2f}")

    test_address = "0x9845e1909dca337944a0272f1f9f7249833d2d19"
    print(f"\nTesting: {test_address}")
    raw = fetch_wallet_transactions(test_address, "ethereum")
    print(f"Raw transfers: {len(raw)}")

    cleaned = [p for p in (parse_transaction(t) for t in raw) if p]
    print(f"Non-stable whale moves (>$100k): {len(cleaned)}")
    for tx in cleaned[:5]:
        print(f"  {tx['action']} {tx['token']} ${tx['amount_usd']:,.2f}")