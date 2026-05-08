import httpx
import os
from dotenv import load_dotenv

load_dotenv()

def test_wallet_fetch():
    # We will test the first address you provided (Wintermute)
    wallet_address = "0x908c4d94d34924765f1edc22a1dd098397c59dd4"
    api_key = os.getenv("COVALENT_KEY")
    
    print(f"📡 Fetching transactions for: {wallet_address}...")
    
    url = f"https://api.covalenthq.com/v1/eth-mainnet/address/{wallet_address}/transactions_v3/?key={api_key}"
    
    r = httpx.get(url)
    
    if r.status_code == 200:
        data = r.json()
        txs = data.get("data", {}).get("items", [])
        print(f"✅ SUCCESS! Found {len(txs)} recent transactions.")
        # Print the first transaction hash as proof
        if txs:
            print(f"🔗 Latest TX Hash: {txs[0].get('tx_hash')}")
    else:
        print(f"❌ FAILED: Status Code {r.status_code}")
        print(r.text)

if __name__ == "__main__":
    test_wallet_fetch()