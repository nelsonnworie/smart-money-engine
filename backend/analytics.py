import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

def get_db_connection():
    return psycopg2.connect("postgresql://postgres:DESmond12$$@localhost:5432/smart_money_db")

def detect_signals():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query high-value transactions
    query = "SELECT * FROM transactions WHERE amount_usd > 10000 AND timestamp > NOW() - INTERVAL '1 hour'"
    cur.execute(query)
    txs = cur.fetchall()
    
    count = 0
    for tx in txs:
        score = 50 if tx['amount_usd'] > 500000 else (20 if tx['amount_usd'] > 50000 else 10)
        
        # Matches your Model.py exactly
        insert_sql = """
            INSERT INTO signals (signal_type, token, conviction_score, wallets_involved, chain)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_sql, (
            'BUY', 
            tx['token'], 
            score, 
            tx['wallet_address'], 
            tx.get('chain', 'ethereum')
        ))
        count += 1
        
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
        
        insert_sql = """
            INSERT INTO signals (signal_type, token, conviction_score, wallets_involved, chain)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_sql, (
            'CLUSTER', 
            c['token'], 
            score, 
            f"{c['wallet_count']} wallets", 
            c['chain']
        ))
        
    conn.commit()
    cur.close()
    conn.close()
    return len(clusters)

def run_analytics():
    print(f"\n--- 🧠 ANALYTICS ENGINE STARTING ---")
    try:
        signals = detect_signals()
        clusters = detect_clusters()
        print(f"--- ✅ ANALYTICS COMPLETE: {signals} Signals, {clusters} Clusters ---")
    except Exception as e:
        print(f"⚠️ Analytics Error: {e}")