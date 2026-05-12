import psycopg2
from psycopg2.extras import RealDictCursor
import asyncio
import os
from dotenv import load_dotenv
from backend.telegram_bot import send_telegram_alert

load_dotenv()

def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if not DATABASE_URL:
        DATABASE_URL = "postgresql://postgres:DESmond12$$@localhost:5432/smart_money_db"
    return psycopg2.connect(DATABASE_URL)

def detect_signals():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    # Query transactions >= $5k from the last hour
    query = "SELECT * FROM transactions WHERE amount_usd >= 5000 AND timestamp > NOW() - INTERVAL '1 hour'"
    cur.execute(query)
    txs = cur.fetchall()
    
    count = 0
    for tx in txs:
        if tx['amount_usd'] >= 500000: score = 95
        elif tx['amount_usd'] >= 100000: score = 85
        elif tx['amount_usd'] >= 50000: score = 75
        else: score = 40
        
        insert_sql = "INSERT INTO signals (signal_type, token, conviction_score, wallets_involved, chain) VALUES (%s, %s, %s, %s, %s) RETURNING *;"
        cur.execute(insert_sql, ('BUY', tx['token'], score, tx['wallet_address'], tx.get('chain', 'ethereum')))
        new_signal = cur.fetchone()
        count += 1
        
        if score >= 40:
            alert_data = {"token": new_signal['token'], "signal_type": new_signal['signal_type'], "conviction_score": new_signal['conviction_score']}
            try:
                asyncio.run(send_telegram_alert(alert_data))
            except Exception as e:
                print(f"⚠️ Telegram alert failed: {e}")
    conn.commit()
    cur.close()
    conn.close()
    return count

def detect_clusters():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cluster_query = """
        SELECT token, COUNT(DISTINCT wallet_address) as wallet_count, MAX(chain) as chain
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        GROUP BY token
        HAVING COUNT(DISTINCT wallet_address) >= 2
    """
    cur.execute(cluster_query)
    clusters = cur.fetchall()
    
    for c in clusters:
        score = min(c['wallet_count'] * 20, 100)
        insert_sql = "INSERT INTO signals (signal_type, token, conviction_score, wallets_involved, chain) VALUES (%s, %s, %s, %s, %s) RETURNING *;"
        cur.execute(insert_sql, ('CLUSTER', c['token'], score, f"{c['wallet_count']} wallets", c['chain']))
        new_cluster = cur.fetchone()
        if score >= 40:
            try:
                asyncio.run(send_telegram_alert({"token": new_cluster['token'], "signal_type": "CLUSTER", "conviction_score": score}))
            except Exception as e:
                print(f"⚠️ Telegram cluster alert failed: {e}")
    conn.commit()
    cur.close()
    conn.close()
    return len(clusters)

# --- THIS IS THE FUNCTION YOUR COLLECTOR IS LOOKING FOR ---
def run_analytics():
    print(f"\n--- 🧠 ANALYTICS ENGINE STARTING ---")
    try:
        signals = detect_signals()
        clusters = detect_clusters()
        print(f"--- ✅ ANALYTICS COMPLETE: {signals} Signals, {clusters} Clusters ---")
    except Exception as e:
        print(f"⚠️ Analytics Error: {e}")