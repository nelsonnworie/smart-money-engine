from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager
import asyncio

# Imports remain the same
from backend.database import SessionLocal, engine
from backend.models import Signal, Wallet, Transaction, Base
from backend.analytics import run_analytics

# Background Loop
async def analytics_scheduler():
    while True:
        print("🔄 Scheduler: Running background analytics...")
        try:
            # This allows the scan to run without stopping the API
            await asyncio.to_thread(run_analytics) 
        except Exception as e:
            print(f"❌ Analytics Error: {e}")
        
        print("😴 Scan complete. Scheduler sleeping for 10 minutes...")
        await asyncio.sleep(600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- FIX: Moved table creation inside lifespan ---
    print("🚀 Initializing Database Tables...")
    Base.metadata.create_all(bind=engine)
    
    # Start the background task
    task = asyncio.create_task(analytics_scheduler())
    yield
    # Shutdown
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

# Root route added to stop the "Not Found" error on the main link
@app.get("/")
def root():
    return {"message": "Smart Money API is live. Visit /docs for API documentation or /health for status."}

@app.get("/health")
def health():
    return {"status": "online", "message": "Engine and Scheduler are humming."}

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