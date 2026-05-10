from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from contextlib import asynccontextmanager
import asyncio

from backend.database import SessionLocal
from backend.models import Signal, Wallet, Transaction
from backend.analytics import run_analytics

# This handles the background loop
async def analytics_scheduler():
    while True:
        print("🔄 Scheduler: Running background analytics...")
        run_analytics()
        # Wait 10 minutes (600 seconds) before running again
        await asyncio.sleep(600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: This runs when you start the server
    task = asyncio.create_task(analytics_scheduler())
    yield
    # SHUTDOWN: This runs when you stop the server
    task.cancel()

app = FastAPI(title="Smart Money API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits your frontend to access the data
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