import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
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


class Signal(Base):
    __tablename__ = 'signals'
    id                = Column(Integer, primary_key=True)
    signal_type       = Column(String)
    token             = Column(String)
    conviction_score  = Column(Integer)
    wallets_involved  = Column(String)
    chain             = Column(String)
    created_at        = Column(DateTime(timezone=True), server_default=func.now())
    amount_usd        = Column(Float, default=0.0)
    outcome           = Column(String, default='PENDING')


class Alert(Base):
    __tablename__ = 'alerts_sent'
    id         = Column(Integer, primary_key=True)
    signal_id  = Column(Integer)
    channel    = Column(String)
    sent_at    = Column(DateTime(timezone=True), server_default=func.now())


if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("Tables ready.")