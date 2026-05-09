import httpx
import os
import time
from dotenv import load_dotenv

load_dotenv()

# API KEYS from your .env
COVALENT_KEY = os.getenv("COVALENT_KEY")
HELIUS_KEY = os.getenv("HELIUS_KEY")

def fetch_wallet_transactions(address, chain):
    """
    Fetches the latest transactions for a specific wallet and chain.
    """
    transactions = []
    
    try:
        if chain.lower() in ['ethereum', 'arbitrum', 'eth-mainnet', 'matic-mainnet']:
            # Use Covalent for EVM chains
            # Map chain name to Covalent internal name
            chain_id = "eth-mainnet" if chain.lower() == 'ethereum' else chain.lower()
            
            url = f"https://api.covalenthq.com/v1/{chain_id}/address/{address}/transactions_v3/"
            params = {"key": COVALENT_KEY}
            
            response = httpx.get(url, params=params, timeout=10.0)
            if response.status_code == 200:
                raw_data = response.json()
                transactions = raw_data.get("data", {}).get("items", [])
            else:
                print(f"❌ Covalent Error ({chain}): {response.status_code}")

        elif chain.lower() == 'solana':
            # Use Helius for Solana
            url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_KEY}"
            
            response = httpx.get(url, timeout=10.0)
            if response.status_code == 200:
                transactions = response.json()
            else:
                print(f"❌ Helius Error: {response.status_code}")
        
        return transactions

    except Exception as e:
        print(f"⚠️ Unexpected error fetching {address}: {e}")
        return []

from datetime import datetime

def parse_transaction(raw_tx):
    """
    Cleans raw Covalent data into a simple BUY/SELL event.
    """
    try:
        # 1. Get the USD Value
        # Covalent provides value_num_64 (raw) and decimals
        value_usd = raw_tx.get("value_display_fixed", 0)
        # For simplicity in testing, we can also look at the 'pretty' value
        # Note: In a production engine, we'd calculate this via token price logs
        amt_usd = float(value_usd) if value_usd else 0

        # 2. Filter: Only keep trades > $5,000 (Roadmap Requirement)
        if amt_usd < 5000:
            return None

        # 3. Determine Action (Simplified logic for Day 2)
        # If the wallet is the 'from' address, they are 'SENDING/SELLING'
        # If they are the 'to' address, they are 'RECEIVING/BUYING'
        # Note: We'll refine this for DEX swaps in Day 3
        action = "SELL" if raw_tx.get("from_address_label") else "BUY"

        # 4. Extract Token Symbol
        # Defaulting to ETH for now, we will pull ERC-20 symbols in the next step
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
    except Exception as e:
        print(f"Parsing error: {e}")
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