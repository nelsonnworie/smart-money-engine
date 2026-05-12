from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager
import asyncio

# Core Imports
from backend.database import SessionLocal, engine
from backend.models import Signal, Wallet, Transaction, Base
from backend.analytics import run_analytics

# --- 1. SEEDER FUNCTION (Fixes the "Missing Function" error) ---
def seed_wallets_if_empty():
    db = SessionLocal()
    try:
        count = db.query(Wallet).count()
        if count == 0:
            print("🌱 Railway Database empty. Seeding 30 smart wallets...")
            smart_wallets = [
                {"address": "0x908c4d94d34924765f1edc22a1dd098397c59dd4", "label": "Wintermute", "chain": "ethereum"},
                {"address": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045", "label": "Vitalik", "chain": "ethereum"},
                {"address": "0x0ca62954b46afee430d645da493c6c783448c4ed", "label": "DEX Alpha Trader", "chain": "ethereum"},
                {"address": "0x1e914730b4cd343ae14530f0bbf6b350d83b833d", "label": "Arb Whale", "chain": "ethereum"},
                {"address": "0x1c287f73c566b3382463a58e5e44f1336ed013c0", "label": "HNW Personal Wallet", "chain": "ethereum"},
                {"address": "0xff9b90914e248339ab0a50bf4798ef8b012eac79", "label": "Institutional Flow", "chain": "ethereum"},
                {"address": "0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B", "label": "Cumberland VC", "chain": "ethereum"},
                {"address": "0x66B0d1635209930777e38D79541aC46101968560", "label": "GMX Whale", "chain": "arbitrum"},
                {"address": "0x3fC91A3afd3030350494443651192272C6943829", "label": "Uniswap LP Power User", "chain": "ethereum"},
                {"address": "0xae2Fc9D90e90E1FDC3505c6d328A3267E6d5854b", "label": "Jaredfromsubway (MEV)", "chain": "ethereum"},
                {"address": "0x28C6c06298d514Db089934071355E5743bf21d60", "label": "Binance Cluster", "chain": "ethereum"},
                {"address": "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9", "label": "Aave Whale", "chain": "ethereum"},
                {"address": "0x4e65cdBdaC7a67137f8D52C06326E17277873D54", "label": "Curve Whale", "chain": "ethereum"},
                {"address": "0x6331a9805d21a220268a7199182a99723df7a783", "label": "Blur Farmer", "chain": "ethereum"},
                {"address": "0xf977814e90da44bfa03b6295a0616a897441acec", "label": "Binance Cold Storage", "chain": "ethereum"},
                {"address": "0x56EDDB45D8C1A062F76426C153b670390B23298F", "label": "Alpha Hunter", "chain": "ethereum"},
                {"address": "0x1111111254fb6c44bac0bed2854e76f90643097d", "label": "1inch Aggregator", "chain": "ethereum"},
                {"address": "0x000000000005a3639c0633fd00000000000b3a32", "label": "Smart Bot", "chain": "ethereum"},
                {"address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e", "label": "Exchange Whale", "chain": "ethereum"},
                {"address": "0xDC24316b9AE028F1497c275EB9192a3Ea0f67022", "label": "Lido Whale", "chain": "ethereum"},
                {"address": "0xBe0eB53F46cd730d13444a1b0EFB7C4101e14930", "label": "Stablecoin Giant", "chain": "ethereum"},
                {"address": "0x82129da993466f2C8795A4016147253457e5eA49", "label": "Pendle Whale", "chain": "ethereum"},
                {"address": "0x6A99A2D09f875eA075D1541fE65b448651859844", "label": "Ethena Staker", "chain": "ethereum"},
                {"address": "0x3907371190209689E849767C74C9D21B008d5377", "label": "Early MEV Hunter", "chain": "ethereum"},
                {"address": "0xb03b71A1A8667a42F882C7C442D731F7589d8924", "label": "Dune Top PnL", "chain": "ethereum"},
                {"address": "0x986a2f247da6675c370db79f9024f0b2f9f1b0a8", "label": "Institutional Flow 2", "chain": "ethereum"},
                {"address": "0x21a3044574923475046203110292350611023456", "label": "Smart Trader X", "chain": "ethereum"},
                {"address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", "label": "WETH Whale", "chain": "ethereum"},
                {"address": "0x00000000219ab540356cBB839Cbe05303d7705Fa", "label": "Eth2 Deposit Contract", "chain": "ethereum"},
                {"address": "0xa5939dbca3f1311acd1b2c9f17f491972ae113cb", "label": "Smart Whale 1", "chain": "ethereum"}
            ]
            for w_data in smart_wallets:
                db.add(Wallet(**w_data))
            db.commit()
            print(f"✅ Seeding complete: {len(smart_wallets)} wallets added.")
        else:
            print(f"✔️ Wallets already exist ({count}). No seeding needed.")
    except Exception as e:
        print(f"❌ Seed Error: {e}")
    finally:
        db.close()

# --- 2. BACKGROUND SCHEDULER ---
from scripts.collector import run_collection # Add this import

async def engine_scheduler():
    while True:
        try:
            print("🔄 Triggering Wallet Collection & Analytics...")
            await asyncio.to_thread(run_collection)
        except Exception as e:
            print(f"❌ Engine Error: {e}")
        await asyncio.sleep(600) # 10 minutes

# --- 3. LIFESPAN MANAGEMENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Tables
    print("🚀 Initializing Database Tables...")
    Base.metadata.create_all(bind=engine)
    
    # Seed Data
    await asyncio.to_thread(seed_wallets_if_empty)
    
    # Start Scheduler
    task = asyncio.create_task(analytics_scheduler())
    yield
    task.cancel()

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

# --- 4. ROUTES ---

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
    ).group_by(Transaction.token).order_by(func.count(Transaction.id).desc()).limit(10).all()
    return [{"token": r[0], "count": r[1]} for r in results]

@app.get("/clusters")
def get_clusters(db: Session = Depends(get_db)):
    return db.query(Signal).filter(Signal.signal_type == 'CLUSTER').all()