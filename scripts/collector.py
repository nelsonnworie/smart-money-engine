"""
collector.py — Wallet scanning & transaction collection
=========================================================
Uses chain-specific parser classes from fetcher.py.
BUY/SELL classification is done inside each parser — not here.
Permanent deduplication happens in analytics.py via processed_transactions.
"""

import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database import SessionLocal, save_transaction
from backend.models import Wallet
from scripts.fetcher import get_parser
from backend.analytics import run_analytics


def run_collection():
    db = SessionLocal()
    try:
        wallets = db.query(Wallet).all()
        print(f"\n🔄 Starting collection cycle for {len(wallets)} wallets...")

        chain_counts: dict[str, int] = {}

        for wallet in wallets:
            chain = (wallet.chain or "ethereum").lower()
            parser = get_parser(chain)

            if not parser:
                print(f"⚠️ No parser for chain '{chain}' — skipping {wallet.label}")
                continue

            print(
                f"📡 Scanning: {wallet.label} [{chain}]...          ",
                end="\r", flush=True
            )

            try:
                parsed_txs = parser.get_transactions(wallet.address)

                if not parsed_txs:
                    continue

                new_count = 0
                for parsed in parsed_txs:
                    if not parsed:
                        continue

                    # Ensure wallet context is set (parsers set this, but safety check)
                    parsed.setdefault("wallet_address", wallet.address)
                    parsed.setdefault("chain", chain)

                    # save_transaction deduplicates by tx_hash at DB level
                    if save_transaction(parsed):
                        new_count += 1

                if new_count > 0:
                    chain_counts[chain] = chain_counts.get(chain, 0) + new_count
                    print(f"\n✅ {wallet.label} [{chain}]: {new_count} new moves logged.")

            except Exception as e:
                print(f"\n⚠️ Error scanning {wallet.label}: {e}")
                continue

            time.sleep(0.6)   # gentle rate limit — respect Etherscan/Helius limits

        # Summary
        if chain_counts:
            print(f"\n📊 Collection summary: {chain_counts}")
        else:
            print("\n📊 No new transactions found this cycle.")

        # Run analytics on collected data
        print("\n🧠 Running analytics engine...")
        run_analytics()

    except Exception as e:
        print(f"\n⚠️ Collector Error: {e}")
    finally:
        db.close()
        print("🏁 Collection cycle complete.\n")


if __name__ == "__main__":
    from apscheduler.schedulers.blocking import BlockingScheduler

    run_collection()   # run immediately on start

    scheduler = BlockingScheduler()
    print("⏰ Scheduler started (every 5 minutes)...")
    scheduler.add_job(run_collection, "interval", minutes=5)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Stopped.")