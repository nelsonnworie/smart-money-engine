import os
import psycopg2
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

def test_connection():
    print("🚀 Starting Day 1 Validation...")
    
    # Test Database
    try:
        db_url = os.getenv("DATABASE_URL")
        conn = psycopg2.connect(db_url)
        print("✅ DATABASE: Connection Successful!")
        conn.close()
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")

    # Test API Key Presence
    keys = ["COVALENT_KEY", "ALCHEMY_KEY", "HELIUS_KEY", "ETHERSCAN_KEY"]
    for key in keys:
        if os.getenv(key):
            print(f"✅ API KEY: {key} is loaded.")
        else:
            print(f"❌ API KEY MISSING: {key}")

if __name__ == "__main__":
    test_connection()