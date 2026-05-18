import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:DESmond12$$@localhost:5432/smart_money_db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=2
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def save_transaction(tx_data):
    from backend.models import Transaction
    db = SessionLocal()
    try:
        existing = db.query(Transaction).filter(
            Transaction.tx_hash == tx_data['tx_hash']
        ).first()
        if existing:
            return False

        real_timestamp = tx_data.get('timestamp')
        if not isinstance(real_timestamp, datetime):
            real_timestamp = datetime.utcnow()

        new_tx = Transaction(
            wallet_address=tx_data['wallet_address'],
            token=tx_data['token'],
            amount_usd=tx_data['amount_usd'],
            tx_hash=tx_data['tx_hash'],
            chain=tx_data.get('chain', 'ethereum'),
            action=tx_data.get('action', 'BUY'),
            timestamp=real_timestamp,
        )
        db.add(new_tx)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()