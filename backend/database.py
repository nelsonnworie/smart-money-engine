import os
import hashlib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/smart_money_db"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=2
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Fingerprint helpers
# ---------------------------------------------------------------------------

def build_fingerprint(chain: str, tx_hash: str, wallet_address: str,
                      token: str, action: str) -> str:
    """
    Deterministic fingerprint for a wallet-level transaction event.
    Same inputs always produce the same fingerprint.
    Stored in processed_transactions to prevent re-alerting forever.
    """
    raw = f"{chain.lower()}:{tx_hash.lower()}:{wallet_address.lower()}:{token.upper()}:{action.upper()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def is_already_processed(fingerprint: str) -> bool:
    """
    Returns True if this fingerprint has EVER been processed.
    Uses a raw psycopg2 connection for atomic check (no ORM overhead).
    """
    import psycopg2
    db_url = os.getenv("DATABASE_URL", DATABASE_URL)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    try:
        conn = psycopg2.connect(db_url)
        cur  = conn.cursor()
        cur.execute(
            "SELECT 1 FROM processed_transactions WHERE fingerprint = %s LIMIT 1",
            (fingerprint,)
        )
        exists = cur.fetchone() is not None
        cur.close()
        conn.close()
        return exists
    except Exception as e:
        print(f"⚠️ is_already_processed error: {e}")
        return False   # fail open — allow processing if DB check fails


def mark_as_processed(fingerprint: str, tx_hash: str, wallet_address: str,
                      token: str, action: str, chain: str,
                      amount_usd: float, alerted: str = "YES") -> bool:
    """
    Atomically inserts the fingerprint into processed_transactions.
    Returns True if inserted (first time), False if already existed (duplicate).
    The UNIQUE constraint on fingerprint is the real lock — concurrent workers safe.
    """
    import psycopg2
    db_url = os.getenv("DATABASE_URL", DATABASE_URL)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    try:
        conn = psycopg2.connect(db_url)
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO processed_transactions
              (fingerprint, tx_hash, wallet_address, token, action, chain, amount_usd, alerted)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (fingerprint) DO NOTHING
        """, (fingerprint, tx_hash, wallet_address, token, action, chain, amount_usd, alerted))
        inserted = cur.rowcount > 0
        conn.commit()
        cur.close()
        conn.close()
        return inserted
    except Exception as e:
        print(f"⚠️ mark_as_processed error: {e}")
        return False


# ---------------------------------------------------------------------------
# Transaction saver
# ---------------------------------------------------------------------------

def save_transaction(tx_data: dict) -> bool:
    """
    Saves a new transaction to the transactions table.
    Returns True if new, False if already existed (tx_hash unique constraint).
    """
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
        print(f"⚠️ save_transaction error: {e}")
        return False
    finally:
        db.close()