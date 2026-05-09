import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

# --- CONNECTION ---
def get_db_connection():
    # Using the verified credentials from your .env
    return psycopg2.connect("postgresql://postgres:DESmond12$$@localhost:5432/smart_money_db")

# --- HOUR 1-4: SIGNAL DETECTOR ---
def detect_signals():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query all transactions from the last 1 hour
    query = "SELECT * FROM transactions WHERE amount_usd > 10000 AND timestamp > NOW() - INTERVAL '1 hour'"
    cur.execute(query)
    txs = cur.fetchall()
    
    count = 0
    for tx in txs:
        # CONVICTION SCORER LOGIC
        score = 0
        if tx['amount_usd'] > 500000: score += 50
        elif tx['amount_usd'] > 50000: score += 20
        
        level = "HIGH" if score >= 50 else ("MEDIUM" if score >= 20 else "LOW")

        # THE EXACT INSERT CODE FROM STEP 2
        insert_sql = """
            INSERT INTO signals (signal_type, token_symbol, wallet_address, amount_usd, conviction_score, conviction_level)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cur.execute(insert_sql, ('BUY', tx['token_symbol'], tx['wallet_address'], tx['amount_usd'], score, level))
        print(f"🚩 Signal: BUY ${tx['token_symbol']} ${tx['amount_usd']:,.2f} — Conviction: {level}")
        count += 1
        
    conn.commit()
    cur.close()
    conn.close()
    return count

# --- HOUR 4-5: CLUSTER DETECTOR ---
def detect_clusters():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cluster_query = """
        SELECT token_symbol, COUNT(DISTINCT wallet_address) as wallet_count, SUM(amount_usd) as total_usd
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        GROUP BY token_symbol
        HAVING COUNT(DISTINCT wallet_address) >= 2
    """
    cur.execute(cluster_query)
    clusters = cur.fetchall()
    
    for c in clusters:
        score = min(c['wallet_count'] * 20, 100)
        level = "HIGH" if score >= 70 else "MEDIUM"
        
        insert_sql = """
            INSERT INTO signals (signal_type, token_symbol, amount_usd, conviction_score, conviction_level)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_sql, ('CLUSTER', c['token_symbol'], c['total_usd'], score, level))
        print(f"💎 CLUSTER: {c['wallet_count']} wallets bought ${c['token_symbol']}!")
        
    conn.commit()
    cur.close()
    conn.close()
    return len(clusters)

# --- THE MASTER FUNCTION ---
def run_analytics():
    print(f"\n--- 🧠 ANALYTICS ENGINE STARTING ---")
    try:
        signals = detect_signals()
        clusters = detect_clusters()
        print(f"--- ✅ ANALYTICS COMPLETE: {signals} Signals, {clusters} Clusters ---")
    except Exception as e:
        print(f"⚠️ Analytics Error: {e}")