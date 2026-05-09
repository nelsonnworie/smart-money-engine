import sys
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler

# This ensures Python can find the 'backend' folder from inside 'scripts'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --- IMPORTS ---
from backend.database import SessionLocal, save_transaction
from backend.models import Wallet
from scripts.fetcher import fetch_wallet_transactions, parse_transaction
from backend.analytics import run_analytics  # THIS IS THE STEP 2 IMPORT

def run_collection():
    db = SessionLocal()
    try:
        # 1. Pull the 30 wallets from your database
        wallets = db.query(Wallet).all()
        print(f"\n🔄 Starting collection cycle for {len(wallets)} wallets...")

        for wallet in wallets:
            print(f"📡 Scanning: {wallet.label} [{wallet.chain}]")
            
            # 2. Fetch raw blockchain data
            raw_txs = fetch_wallet_transactions(wallet.address, wallet.chain)
            
            new_count = 0
            for tx in raw_txs:
                # 3. Parse and filter (Keep only > $5000)
                parsed = parse_transaction(tx)
                
                if parsed:
                    parsed['wallet_address'] = wallet.address
                    parsed['chain'] = wallet.chain
                    
                    # 4. Save to the 'transactions' table
                    was_saved = save_transaction(parsed)
                    if was_saved:
                        new_count += 1
            
            if new_count > 0:
                print(f"   ✅ SUCCESS: Logged {new_count} NEW whale moves.")
            
            # Rate Limiting
            time.sleep(0.5)

        # --- STEP 2: CONNECTING TO THE SCHEDULER ---
        # Now that we have fresh data, we trigger the 'Brain' to analyze it immediately
        run_analytics()

    except Exception as e:
        print(f"⚠️ Collector Error: {e}")
    finally:
        db.close()
        print("🏁 Cycle complete. Standing by for next run...")

# --- EXECUTION BLOCK ---
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    
    # Run once immediately on start
    run_collection()
    
    # Then schedule it to run every 5 minutes
    print("⏰ Scheduler started. Will scan every 5 minutes...")
    scheduler.add_job(run_collection, 'interval', minutes=5)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Collector stopped by user.")