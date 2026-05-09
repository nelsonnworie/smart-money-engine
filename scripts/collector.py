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
from backend.analytics import run_analytics 

def run_collection():
    db = SessionLocal()
    try:
        # 1. Pull the 30 wallets from your database
        wallets = db.query(Wallet).all()
        print(f"\n🔄 Starting collection cycle for {len(wallets)} wallets...")

        for wallet in wallets:
            # The 'end="\r"' trick keeps the terminal on a single line while scanning
            print(f"📡 Scanning: {wallet.label} [{wallet.chain}]...          ", end="\r", flush=True)
            
            try:
                # 2. Fetch raw blockchain data (hardened in fetcher.py)
                raw_txs = fetch_wallet_transactions(wallet.address, wallet.chain)
                
                if not raw_txs:
                    continue

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
                    # Move to a new line only when we actually find data
                    print(f"\n✅ {wallet.label}: Logged {new_count} NEW whale moves.")
            
            except Exception:
                # Silently skip any individual wallet errors (like specific API timeouts)
                continue

            # Rate Limiting
            time.sleep(0.5)

        # --- STEP 2: RUN ANALYTICS ---
        # Trigger the 'Brain' once all wallets are scanned
        run_analytics()

    except Exception as e:
        print(f"\n⚠️ Critical Collector Error: {e}")
    finally:
        db.close()
        print("\n🏁 Cycle complete. Standing by for next run...")

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