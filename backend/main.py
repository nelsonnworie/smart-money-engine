from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager
from datetime import datetime
import asyncio
import os

# Core Imports
from backend.database import SessionLocal, engine
from backend.models import Signal, Wallet, Transaction, Base
from backend.analytics import run_analytics
from scripts.collector import run_collection


# --- 1. SEEDER FUNCTION ---
def seed_wallets_if_empty():
    db = SessionLocal()
    try:
        import json
        json_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'wallets.json')
        with open(json_path, 'r') as f:
            smart_wallets = json.load(f)

        existing_count = db.query(Wallet).count()
        json_count = len(smart_wallets)

        if existing_count != json_count:
            print(f"Wallet count mismatch ({existing_count} in DB vs {json_count} in JSON). Syncing...")
            db.query(Wallet).delete()
            db.commit()
            for w_data in smart_wallets:
                db.add(Wallet(
                    address=w_data['address'],
                    label=w_data['label'],
                    chain=w_data['chain']
                ))
            db.commit()
            print(f"Synced: {json_count} wallets now in DB.")
        else:
            print(f"Wallets already synced ({existing_count} wallets).")
    except Exception as e:
        print(f"Seed Error: {e}")
    finally:
        db.close()


# --- 2. CLEANUP FUNCTION ---
async def clean_orphan_transactions():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Remove transactions from wallets no longer tracked
        cur.execute("""
            DELETE FROM transactions
            WHERE wallet_address NOT IN (
                SELECT address FROM wallets
            )
        """)
        deleted_txs = cur.rowcount

        # Remove old junk signals with NULL amount or bad tokens
        cur.execute("""
            DELETE FROM signals
            WHERE amount_usd IS NULL
               OR token IN (
                   'ETHf', 'ETHG', 'AF1', 'AFO', 'ETHFather',
                   'USDC', 'USDT', 'DAI', 'WBTC', 'WETH',
                   'USDS', 'FDUSD', 'BUSD'
               )
        """)
        deleted_signals = cur.rowcount

        conn.commit()
        cur.close()
        conn.close()
        print(f"Removed {deleted_txs} orphan transactions, {deleted_signals} junk signals")
    except Exception as e:
        print(f"Cleanup error: {e}")


# --- 3. BACKGROUND SCHEDULER ---
async def engine_scheduler():
    while True:
        try:
            print("Triggering Wallet Collection & Analytics...")
            await asyncio.to_thread(run_collection)
        except Exception as e:
            print(f"Engine Error: {e}")
        print("Cycle complete. Sleeping for 10 minutes...")
        await asyncio.sleep(600)


# --- 4. LIFESPAN ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing Database Tables...")
    Base.metadata.create_all(bind=engine)
    await asyncio.to_thread(seed_wallets_if_empty)
    await clean_orphan_transactions()
    task = asyncio.create_task(engine_scheduler())
    yield
    task.cancel()


# --- 5. APP ---
app = FastAPI(title="Smart Money API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 6. ROUTES ---
@app.get("/")
def root():
    return {"message": "Smart Money API is live.", "endpoints": ["/health", "/signals", "/wallets"]}


@app.get("/health")
def health():
    return {"status": "online", "engine": "running"}


@app.get("/signals")
def get_signals(db: Session = Depends(get_db)):
    return db.query(Signal).order_by(Signal.created_at.desc()).all()


@app.get("/wallets")
def get_wallets(db: Session = Depends(get_db)):
    return db.query(Wallet).all()


@app.get("/top-movers")
def get_top_movers(db: Session = Depends(get_db)):
    results = db.query(
        Transaction.token,
        func.count(Transaction.id).label('count')
    ).group_by(Transaction.token).order_by(
        func.count(Transaction.id).desc()
    ).limit(10).all()
    return [{"token": r[0], "count": r[1]} for r in results]


@app.get("/clusters")
def get_clusters(db: Session = Depends(get_db)):
    return db.query(Signal).filter(Signal.signal_type == 'CLUSTER').all()