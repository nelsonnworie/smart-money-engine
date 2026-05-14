import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from dotenv import load_dotenv

# Load database URL from .env
load_dotenv()
Base = declarative_base()

# Table 1: Wallets
class Wallet(Base):
    __tablename__ = 'wallets'
    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    chain = Column(String)
    label = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Table 2: Transactions
class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    tx_hash = Column(String, unique=True)
    wallet_address = Column(String)
    token = Column(String)
    amount_usd = Column(Float)
    action = Column(String) # Buy, Sell, Transfer
    chain = Column(String)
    timestamp = Column(DateTime)

# Table 3: Signals (For Day 2-3 logic)
class Signal(Base):
    __tablename__ = 'signals'
    id = Column(Integer, primary_key=True)
    signal_type = Column(String)
    token = Column(String)
    amount_usd = Column(Float, default=0.0)
    conviction_score = Column(Integer)
    wallets_involved = Column(String)
    chain = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Table 4: Alerts Sent
class Alert(Base):
    __tablename__ = 'alerts_sent'
    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer)
    channel = Column(String) # Telegram/Discord
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

# This part actually CREATES the tables in your Postgres Database
if __name__ == "__main__":
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✅ SUCCESS: 4 Tables (Wallets, Transactions, Signals, Alerts) created in smart_money_db!")