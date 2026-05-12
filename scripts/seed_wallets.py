import sys
import os
import json

# 1. Path Helper: Look one folder up for 'backend'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Imports
from backend.database import SessionLocal
from backend.models import Wallet

def seed_wallets():
    db = SessionLocal()
    # Ensure the path to the JSON file is correct relative to where you run the script
    with open("scripts/wallets.json", "r") as f:
        wallets = json.load(f)
        
    for w in wallets:
        exists = db.query(Wallet).filter(Wallet.address == w['address']).first()
        if not exists:
            new_wallet = Wallet(address=w['address'], label=w['label'], chain=w['chain'])
            db.add(new_wallet)
    
    db.commit()
    print(f"✅ Successfully seeded {len(wallets)} wallets into the DB!")
    db.close()

if __name__ == "__main__":
    seed_wallets()