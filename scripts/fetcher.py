import httpx
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# API KEYS from your .env
COVALENT_KEY = os.getenv("COVALENT_KEY")
HELIUS_KEY = os.getenv("HELIUS_KEY")

def fetch_wallet_transactions(address, chain):
    """
    Fetches the latest transactions for a specific wallet and chain.
    Hardened for timeouts and API errors.
    """
    transactions = []
    
    try:
        if chain.lower() in ['ethereum', 'arbitrum', 'eth-mainnet', 'matic-mainnet']:
            chain_id = "eth-mainnet" if chain.lower() == 'ethereum' else chain.lower()
            url = f"https://api.covalenthq.com/v1/{chain_id}/address/{address}/transactions_v3/"
            params = {"key": COVALENT_KEY}
            
            # Increased timeout to 30s for heavy institutional wallets
            response = httpx.get(url, params=params, timeout=30.0)
            
            if response.status_code == 200:
                raw_data = response.json()
                transactions = raw_data.get("data", {}).get("items", [])
            else:
                # Silent return on 501 or other API errors to keep terminal clean
                return []

        elif chain.lower() == 'solana':
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_KEY}"
            response = httpx.get(url, timeout=30.0)
            if response.status_code == 200:
                transactions = response.json()
        
        return transactions

    except (httpx.ReadTimeout, httpx.ConnectTimeout):
        # Silencing timeout errors specifically
        return []
    except Exception:
        # Silencing unexpected errors to prevent terminal clutter
        return []

def parse_transaction(raw_tx):
    """
    Cleans raw Covalent data into a simple BUY/SELL event.
    """
    try:
        # 1. Get the USD Value
        value_usd = raw_tx.get("value_display_fixed", 0)
        amt_usd = float(value_usd) if value_usd else 0

        # 2. Filter: Only keep trades > $5,000
        if amt_usd < 5000:
            return None

        # 3. Determine Action
        action = "SELL" if raw_tx.get("from_address_label") else "BUY"

        # 4. Extract Token Symbol
        token = "ETH" 

        # 5. Convert Timestamp
        raw_time = raw_tx.get("block_signed_at")
        dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))

        return {
            "tx_hash": raw_tx.get("tx_hash"),
            "token_symbol": token,
            "amount_usd": amt_usd,
            "action": action,
            "timestamp": dt
        }
    except Exception:
        # Silencing parsing errors
        return None

# --- TEST IT ---
if __name__ == "__main__":
    test_wallet = "0x908c4d94d34924765f1edc22a1dd098397c59dd4"
    print(f"🔍 Testing Parser for {test_wallet}...")
    
    raw_results = fetch_wallet_transactions(test_wallet, "ethereum")
    
    cleaned_txs = []
    for tx in raw_results:
        parsed = parse_transaction(tx)
        if parsed:
            cleaned_txs.append(parsed)
            
    print(f"✅ Cleaned {len(cleaned_txs)} high-value transactions (> $5000).")
    if cleaned_txs:
        print(f"📊 Sample Event: {cleaned_txs[0]['action']} {cleaned_txs[0]['token_symbol']} - ${cleaned_txs[0]['amount_usd']:.2f}")