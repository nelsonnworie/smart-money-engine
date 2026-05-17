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
from scripts.collector import run_collection 

# --- 1. SEEDER FUNCTION ---
def seed_wallets_if_empty():
    db = SessionLocal()
    try:
        count = db.query(Wallet).count()
        if count == 0:
            print("🌱 Seeding wallets from wallets.json...")
            import json, os
            json_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'wallets.json')
            with open(json_path, 'r') as f:
                smart_wallets = json.load(f)
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
async def engine_scheduler():
    while True:
        try:
            print("🔄 Triggering Wallet Collection & Analytics...")
            # This calls the collector, which in turn calls analytics
            await asyncio.to_thread(run_collection)
        except Exception as e:
            print(f"❌ Engine Error: {e}")
        
        print("😴 Cycle complete. Sleeping for 10 minutes...")
        await asyncio.sleep(600) 

# --- 3. LIFESPAN MANAGEMENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Tables
    print("🚀 Initializing Database Tables...")
    Base.metadata.create_all(bind=engine)
    
    # Seed Data
    await asyncio.to_thread(seed_wallets_if_empty)
    
    # FIX: Changed 'analytics_scheduler' to 'engine_scheduler' to match definition above
    task = asyncio.create_task(engine_scheduler())
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

@app.get("/admin/clean-old-transactions")
def clean_old_transactions(db: Session = Depends(get_db)):
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=2)
    deleted = db.query(Transaction).filter(
        Transaction.timestamp < cutoff
    ).delete()
    db.commit()
    return {"deleted": deleted, "message": "Old transactions cleaned"}