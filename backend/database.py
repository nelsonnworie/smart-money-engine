import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# 1. Database Setup
DATABASE_URL = os.getenv("DATABASE_URL")

# Fix for Railway/Heroku postgres naming
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Fallback for local development if .env is missing
if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:DESmond12$$@localhost:5432/smart_money_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Function to save a transaction
def save_transaction(tx_data):
    from backend.models import Transaction  # Local import to avoid circular errors
    db = SessionLocal()
    try:
        new_tx = Transaction(
            wallet_address=tx_data['wallet_address'],
            token=tx_data['token'],
            amount_usd=tx_data['amount_usd'],
            tx_hash=tx_data['tx_hash'],
            chain=tx_data.get('chain', 'ethereum'),
            action=tx_data.get('action', 'BUY'),
            timestamp=datetime.utcnow()
        )
        db.add(new_tx)
        db.commit()
        return True
    except Exception as e:
        print(f"⚠️ Error saving transaction: {e}")
        db.rollback()
        return False
    finally:
        db.close()