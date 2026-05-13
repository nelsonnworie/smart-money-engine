import httpx
import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import timezone

load_dotenv()

ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY")
HELIUS_KEY = os.getenv("HELIUS_KEY")

# Current ETH price cache
_eth_price_cache = {"price": 2500.0, "fetched_at": None}

def get_eth_price():
    """Get current ETH price in USD from Etherscan."""
    try:
        url = "https://api.etherscan.io/v2/api"
        params = {
            "chainid": 1,
            "module": "stats",
            "action": "ethprice",
            "apikey": ETHERSCAN_KEY
        }
        r = httpx.get(url, params=params, timeout=10.0)
        if r.status_code == 200:
            result = r.json().get("result", {})
            price = float(result.get("ethusd", 2500))
            _eth_price_cache["price"] = price
            return price
    except Exception:
        pass
    return _eth_price_cache["price"]


def fetch_wallet_transactions(address, chain):
    """
    Fetch ERC-20 token transfers for a wallet using Etherscan.
    Returns parsed transactions directly — no separate parse step needed.
    """
    transactions = []

    try:
        if chain.lower() in ["ethereum", "arbitrum"]:
            base_url = "https://api.etherscan.io/v2/api"

            # Fetch ERC-20 token transfers — these have real USD values
            params = {
                "chainid": 1 if chain.lower() == "ethereum" else 42161,
                "module": "account",
                "action": "tokentx",
                "address": address,
                "startblock": 0,
                "endblock": 99999999,
                "page": 1,
                "offset": 50,
                "sort": "desc",
                "apikey": ETHERSCAN_KEY
}
            r = httpx.get(base_url, params=params, timeout=30.0)

            if r.status_code == 200:
                result = r.json()
                if result.get("status") == "1":
                    transactions = result.get("result", [])

        elif chain.lower() == "solana":
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_KEY}"
            r = httpx.get(url, timeout=30.0)
            if r.status_code == 200:
                transactions = r.json()

    except Exception:
        pass

    return transactions


def parse_transaction(raw_tx):
    """
    Parse an Etherscan ERC-20 token transfer into our standard format.
    """
    try:
        # Get token info
        token = raw_tx.get("tokenSymbol", "UNKNOWN")
        decimals = int(raw_tx.get("tokenDecimal", 18) or 18)

        # Calculate token amount
        raw_value = int(raw_tx.get("value", 0) or 0)
        token_amount = raw_value / (10 ** decimals)

        # Get USD value — Etherscan doesn't give USD directly
        # We use a reasonable estimate: for stablecoins price=1, for others use ETH price ratio
        # For now we filter by token amount as a proxy
        # Stablecoins: USDC, USDT, DAI, BUSD — 1:1 with USD
        stablecoins = ["USDC", "USDT", "DAI", "BUSD", "TUSD", "FRAX", "LUSD", "USDP"]

        if token in stablecoins:
            amt_usd = token_amount  # 1:1 with USD
        elif token == "WETH" or token == "ETH":
            eth_price = get_eth_price()
            amt_usd = token_amount * eth_price
        elif token == "WBTC":
            amt_usd = token_amount * 95000  # approximate BTC price
        else:
            # For unknown tokens, use a minimum threshold based on amount
            # If someone transfers 1M+ tokens it's likely significant
            amt_usd = token_amount * 0.01  # conservative estimate

        # Filter: only keep transfers >= $5,000
        if amt_usd < 50000:
            return None

        # Determine direction
        wallet_address = raw_tx.get("to", "").lower()
        from_address = raw_tx.get("from", "").lower()
        # Will be set by collector
        action = "BUY"

        # Parse timestamp
        timestamp_raw = raw_tx.get("timeStamp", "")
        try:
            dt = datetime.fromtimestamp(int(timestamp_raw), tz=timezone.utc).replace(tzinfo=None)
        except Exception:
            dt = datetime.utcnow()

        return {
            "tx_hash":    raw_tx.get("hash"),
            "token":      token,
            "amount_usd": round(amt_usd, 2),
            "action":     action,
            "timestamp":  dt,
            "from":       from_address,
            "to":         wallet_address,
        }

    except Exception:
        return None


# --- TEST ---
if __name__ == "__main__":
    # Test with a known active whale
    test_address = "0x47ac0fb4f2d84898e4d9e7b4dab3c24507a6d503"
    print(f"Testing Etherscan fetcher for {test_address}...")
    print(f"ETH Price: ${get_eth_price():.2f}")

    raw = fetch_wallet_transactions(test_address, "ethereum")
    print(f"Raw transfers returned: {len(raw)}")

    cleaned = []
    for tx in raw:
        parsed = parse_transaction(tx)
        if parsed:
            cleaned.append(parsed)

    print(f"High-value transfers (>$5k): {len(cleaned)}")
    for tx in cleaned[:5]:
        print(f"  {tx['action']} {tx['token']} ${tx['amount_usd']:,.2f} at {tx['timestamp']}")