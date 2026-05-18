import httpx
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
import time

load_dotenv()

ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY")
HELIUS_KEY    = os.getenv("HELIUS_KEY")

_eth_price_cache = {"price": 2500.0, "last_update": 0}
_price_cache     = {}

CHAIN_IDS = {"ethereum": 1, "arbitrum": 42161, "base": 8453, "bsc": 56}

STABLECOINS = ["USDC","USDT","DAI","BUSD","TUSD","FRAX","LUSD","USDP","USDS","FDUSD"]

# Tokens that are spam/airdrop dust — always drop regardless of amount
BLOCKLIST = {
    "TRUMPTROLL","XDOGE","KISHU","WOJAK","XD","AKITA","CONAN",
    "FREE","VOLT","CHUD","BAD","DTOKEN","PEIPEI","4CHAN","XEN",
    "STARL","FAERIEDRAGON","SHIB2","ELONGATE","SAFEMOON",
}

FALLBACK_PRICES = {
    "ETH": 2500.0, "WETH": 2500.0,
    "WBTC": 95000.0,
    "BNB": 600.0, "WBNB": 600.0,
    "PEPE": 0.0000142,
    "SHIB": 0.0000248,
    "DOGE": 0.38,
    "FLOKI": 0.000195,
    "LINK": 14.0,
    "UNI":  7.0,
    "AAVE": 180.0,
    "ARB":  0.45,
    "OP":   0.90,
    "MATIC": 0.55,
    "SOL":  150.0,
    "CRV":  0.35,
    "LDO":  1.20,
    "MKR":  1800.0,
    "SNX":  2.50,
    "BAL":  2.80,
    "SUSHI": 0.80,
    "COMP": 45.0,
    "YFI":  6000.0,
    "GMX":  18.0,
    "GNS":  1.80,
}
for s in STABLECOINS:
    FALLBACK_PRICES[s] = 1.0

COINGECKO_IDS = {
    "ETH": "ethereum", "WETH": "weth", "WBTC": "wrapped-bitcoin",
    "BNB": "binancecoin", "WBNB": "wbnb",
    "PEPE": "pepe", "SHIB": "shiba-inu", "DOGE": "dogecoin",
    "FLOKI": "floki", "LINK": "chainlink", "UNI": "uniswap",
    "AAVE": "aave", "ARB": "arbitrum", "OP": "optimism",
    "MATIC": "matic-network", "SOL": "solana",
    "CRV": "curve-dao-token", "LDO": "lido-dao",
    "MKR": "maker", "SNX": "synthetix-network-token",
    "GMX": "gmx", "GNS": "gains-network",
}

# Amount filters
MIN_ALERT_USD     =    50_000   # $50k floor — real smart money moves
MAX_REALISTIC_USD = 30_000_000  # $30M hard cap
# Minimum token price — SHIT, KURURU, COCORO, PNDC etc all price < 0.000001
# Real tokens (PEPE=0.0000142, LINK=$14, ETH=$2500) all above this threshold
MIN_TOKEN_PRICE   =  0.000001   # one millionth of a dollar


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


def get_price_coingecko(cg_id: str) -> float:
    try:
        r = httpx.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": cg_id, "vs_currencies": "usd"},
            timeout=8,
        )
        if r.status_code == 200:
            data = r.json()
            for val in data.values():
                price = val.get("usd", 0)
                if price and price > 0:
                    return float(price)
    except Exception:
        pass
    return 0.0


def get_token_price(symbol: str) -> float:
    token = symbol.upper().replace("$", "").strip()
    now   = time.time()

    if token in _price_cache and now - _price_cache[token][1] < 600:
        return _price_cache[token][0]

    if token in STABLECOINS:
        _price_cache[token] = (1.0, now)
        return 1.0

    if token in ("ETH", "WETH"):
        price = get_eth_price()
        _price_cache[token] = (price, now)
        return price

    if token in FALLBACK_PRICES:
        price = FALLBACK_PRICES[token]
        _price_cache[token] = (price, now)
        return price

    # Live CoinGecko lookup
    cg_id = COINGECKO_IDS.get(token, token.lower())
    price = get_price_coingecko(cg_id)
    if price > 0:
        _price_cache[token] = (price, now)
        return price

    _price_cache[token] = (0.0, now)
    return 0.0


def fetch_wallet_transactions(address: str, chain: str) -> list:
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
            r = httpx.get("https://api.etherscan.io/v2/api", params=params, timeout=30)
            if r.status_code == 200 and r.json().get("status") == "1":
                return r.json().get("result", [])

        elif chain_lower == "solana":
            url = (
                f"https://api.helius.xyz/v0/addresses/{address}/transactions"
                f"?api-key={HELIUS_KEY}&limit=50"
            )
            r = httpx.get(url, timeout=30)
            if r.status_code == 200:
                return r.json()

    except Exception:
        pass
    return []


def parse_transaction(raw_tx: dict, chain: str = "ethereum") -> dict | None:
    try:
        if isinstance(raw_tx, dict) and "signature" in raw_tx:
            return None  # Solana — different schema, skip for now

        token_symbol = raw_tx.get("tokenSymbol", "UNKNOWN")
        token = token_symbol.upper().replace("$", "").strip()

        # Drop blocklisted tokens immediately
        if token in BLOCKLIST:
            return None

        decimals = int(raw_tx.get("tokenDecimal", 18) or 18)
        if not (0 <= decimals <= 30):
            decimals = 18

        raw_val      = int(raw_tx.get("value", 0) or 0)
        token_amount = raw_val / (10 ** decimals)

        price   = get_token_price(token)
        amt_usd = token_amount * price

        if price == 0 or price < MIN_TOKEN_PRICE:
            return None
        if amt_usd < MIN_ALERT_USD or amt_usd > MAX_REALISTIC_USD:
            return None

        dt = datetime.utcnow()
        try:
            dt = datetime.fromtimestamp(
                int(raw_tx.get("timeStamp", 0)), tz=timezone.utc
            ).replace(tzinfo=None)
        except Exception:
            pass

        return {
            "tx_hash":    raw_tx.get("hash"),
            "token":      f"${token}",
            "amount_usd": round(amt_usd, 2),
            "action":     "TRANSFER",
            "timestamp":  dt,
            "from":       raw_tx.get("from", "").lower(),
            "to":         raw_tx.get("to",   "").lower(),
        }

    except Exception:
        return None


if __name__ == "__main__":
    print(f"ETH:   ${get_eth_price():.2f}")
    print(f"PEPE:  ${get_token_price('PEPE')}")
    print(f"ARB:   ${get_token_price('ARB')}")
    print(f"4CHAN: ${get_token_price('4CHAN')} (should be 0 — blocklisted)")
    print(f"MIN_ALERT_USD: ${MIN_ALERT_USD:,}")
    print(f"MAX_REALISTIC_USD: ${MAX_REALISTIC_USD:,}")