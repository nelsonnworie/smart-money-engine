import sys
import os
import time
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, save_transaction
from backend.models import Wallet
from scripts.fetcher import fetch_wallet_transactions, parse_transaction
from backend.analytics import run_analytics 

def run_collection():
    db = SessionLocal()
    try:
        wallets = db.query(Wallet).all()
        print(f"\n🔄 Starting collection cycle for {len(wallets)} wallets...")

        for wallet in wallets:
            print(f"📡 Scanning: {wallet.label} [{wallet.chain}]...          ", end="\r", flush=True)
            
            try:
                raw_txs = fetch_wallet_transactions(wallet.address, wallet.chain)
                if not raw_txs:
                    continue

                new_count = 0
                for tx in raw_txs:
                    parsed = parse_transaction(tx)
                    if not parsed:
                        continue

                    parsed['wallet_address'] = wallet.address
                    parsed['chain'] = wallet.chain
                    
                    # Proper BUY / SELL detection
                    if parsed.get('to', '').lower() == wallet.address.lower():
                        parsed['action'] = 'BUY'
                    else:
                        parsed['action'] = 'SELL'
                    
                    # Save only if new
                    if save_transaction(parsed):
                        new_count += 1
                
                if new_count > 0:
                    print(f"\n✅ {wallet.label}: Logged {new_count} NEW moves.")
            
            except Exception:
                continue

            time.sleep(0.6)  # gentle rate limit

        # Run analytics after all wallets
        print("\n🧠 Running analytics...")
        run_analytics()

    except Exception as e:
        print(f"\n⚠️ Collector Error: {e}")
    finally:
        db.close()
        print("🏁 Cycle complete.\n")

# === MAIN ===
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    run_collection()                    # run once immediately
    
    print("⏰ Scheduler started (every 5 minutes)...")
    scheduler.add_job(run_collection, 'interval', minutes=5)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Stopped.")