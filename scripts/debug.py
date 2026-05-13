import httpx, os
from dotenv import load_dotenv
load_dotenv()

key = os.getenv("COVALENT_KEY")

# Step 1: Get current ETH price from Covalent's pricing endpoint
price_url = "https://api.covalenthq.com/v1/pricing/tickers/?quote-currency=USD&key=" + key
price_r = httpx.get(price_url, timeout=30.0)
eth_price = 0
if price_r.status_code == 200:
    tickers = price_r.json().get("data", {}).get("items", [])
    for t in tickers:
        if t.get("contract_ticker_symbol") == "ETH":
            eth_price = t.get("quote_rate", 0)
            break

print(f"ETH Price from Covalent: ${eth_price}")

# Step 2: Fetch transactions
url = "https://api.covalenthq.com/v1/eth-mainnet/address/0x47ac0fb4f2d84898e4d9e7b4dab3c24507a6d503/transactions_v3/"
r = httpx.get(url, params={"key": key}, timeout=30.0)
items = r.json().get("data", {}).get("items", [])

print(f"Transactions: {len(items)}")
print()

# Step 3: Calculate USD value from gas_quote_rate (this IS reliable)
for i, tx in enumerate(items[:5]):
    gas_quote_rate = tx.get("gas_quote_rate", 0)  # This is ETH price in USD
    fees_paid_wei = tx.get("fees_paid", 0) or 0
    
    # value in wei converted to ETH then to USD
    value_wei = int(tx.get("value", 0) or 0)
    value_eth = value_wei / 1e18
    value_usd = value_eth * float(gas_quote_rate or 0)
    
    logs = tx.get("log_events", [])
    # Count logs that have real token transfers
    real_transfers = [l for l in logs if l.get("sender_contract_ticker_symbol") 
                      and l.get("decoded", {}) 
                      and l.get("decoded", {}).get("name") == "Transfer"]
    
    print(f"TX {i+1}: value_wei={value_wei} | ETH={value_eth:.4f} | USD=${value_usd:.2f} | gas_rate=${gas_quote_rate} | transfers={len(real_transfers)}")