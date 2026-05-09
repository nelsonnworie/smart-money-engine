import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Transaction, Wallet
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def save_transaction(tx_data):
    db = SessionLocal()
    try:
        # Check if exists to avoid duplicates
        exists = db.query(Transaction).filter(Transaction.tx_hash == tx_data['tx_hash']).first()
        if not exists:
            new_tx = Transaction(**tx_data)
            db.add(new_tx)
            db.commit()
            return True
        return False
    finally:
        db.close()