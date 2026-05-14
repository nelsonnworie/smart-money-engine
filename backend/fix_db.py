import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Add missing column
cur.execute('ALTER TABLE signals ADD COLUMN IF NOT EXISTS amount_usd FLOAT;')
conn.commit()

# Show all columns in signals table
cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'signals'")
print('Signals columns:', [r[0] for r in cur.fetchall()])

cur.close()
conn.close()
print('Done!')