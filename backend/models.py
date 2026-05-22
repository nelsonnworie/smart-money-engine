import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, UniqueConstraint, Index, Text
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from dotenv import load_dotenv

load_dotenv()
Base = declarative_base()


class Wallet(Base):
    __tablename__ = 'wallets'
    id                 = Column(Integer, primary_key=True)
    address            = Column(String, unique=True, nullable=False)
    chain              = Column(String)
    label              = Column(String)
    created_at         = Column(DateTime(timezone=True), server_default=func.now())
    win_rate           = Column(Float, default=0.0)
    total_signals      = Column(Integer, default=0)
    profitable_signals = Column(Integer, default=0)
    outcome            = Column(String, default='PENDING')


class Transaction(Base):
    __tablename__ = 'transactions'
    id             = Column(Integer, primary_key=True)
    tx_hash        = Column(String, unique=True)
    wallet_address = Column(String)
    token          = Column(String)
    amount_usd     = Column(Float)
    action         = Column(String)
    chain          = Column(String)
    timestamp      = Column(DateTime)

    __table_args__ = (
        Index('ix_transactions_wallet', 'wallet_address'),
        Index('ix_transactions_token',  'token'),
        Index('ix_transactions_ts',     'timestamp'),
    )


class ProcessedTransaction(Base):
    """
    Permanent deduplication memory.
    Once a tx fingerprint is written here, it is NEVER alerted again.
    No time windows. No exceptions.

    Fingerprint format:  {chain}:{tx_hash}:{wallet_address}:{token}:{action}
    This is enforced at DB level via UNIQUE constraint — the DB is the lock.
    """
    __tablename__ = 'processed_transactions'
    id             = Column(Integer, primary_key=True)
    fingerprint    = Column(String, nullable=False)
    tx_hash        = Column(String, nullable=False)
    wallet_address = Column(String, nullable=False)
    token          = Column(String)
    action         = Column(String)
    chain          = Column(String)
    amount_usd     = Column(Float)
    alerted        = Column(String, default='YES')   # YES | SKIPPED (below threshold)
    processed_at   = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('fingerprint', name='uq_processed_fingerprint'),
        Index('ix_processed_tx_hash', 'tx_hash'),
    )


class Signal(Base):
    __tablename__ = 'signals'
    id               = Column(Integer, primary_key=True)
    signal_type      = Column(String)          # BUY | SELL | CLUSTER — raw action only
    token            = Column(String)
    conviction_score = Column(Integer)
    wallets_involved = Column(String)
    chain            = Column(String)
    created_at       = Column(DateTime(timezone=True), server_default=func.now())
    amount_usd       = Column(Float, default=0.0)
    outcome          = Column(String, default='PENDING')
    tx_hash          = Column(String)          # link back to source tx

    __table_args__ = (
        Index('ix_signals_token',   'token'),
        Index('ix_signals_created', 'created_at'),
    )


class Alert(Base):
    __tablename__ = 'alerts_sent'
    id        = Column(Integer, primary_key=True)
    signal_id = Column(Integer)
    channel   = Column(String)
    sent_at   = Column(DateTime(timezone=True), server_default=func.now())


if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/smart_money_db")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✅ All tables created (including processed_transactions).")