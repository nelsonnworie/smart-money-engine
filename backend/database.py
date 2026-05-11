import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models import Transaction, Wallet
from dotenv import load_dotenv

load_dotenv()

# 1. Get the URL from the environment
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Fix the Railway 'postgres://' vs 'postgresql://' issue
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# 3. Create the engine (with a backup for local development)
if not DATABASE_URL:
    print("⚠️ WARNING: No DATABASE_URL found, falling back to local.")
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/smart_money"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)