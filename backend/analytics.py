import psycopg2
from psycopg2.extras import RealDictCursor
import asyncio
import time
import os
from dotenv import load_dotenv
from backend.telegram_bot import send_telegram_alert

load_dotenv()

# Stablecoins — never alert on these, too much noise
STABLECOINS = ["USDT", "USDC", "DAI", "BUSD", "TUSD", "FRAX", "LUSD", "USDP", "USDS"]


def send_alert_safe(alert_data):
    """Send Telegram alert without event loop conflicts."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_telegram_alert(alert_data))
        loop.close()
        time.sleep(1)  # Prevent Telegram flood control
    except Exception as e:
        print(f"⚠️ Telegram alert failed: {e}")


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

    # Only look at transactions from the last 1 hour
    query = """
        SELECT * FROM transactions
        WHERE amount_usd >= 5000
        AND timestamp > NOW() - INTERVAL '1 hour'
    """
    cur.execute(query)
    txs = cur.fetchall()

    count = 0
    for tx in txs:
        # Score based on transaction size
        if tx['amount_usd'] >= 500000:
            score = 95
        elif tx['amount_usd'] >= 100000:
            score = 85
        elif tx['amount_usd'] >= 50000:
            score = 75
        else:
            score = 40

        # Save signal to database
        insert_sql = """
            INSERT INTO signals (signal_type, token, conviction_score, wallets_involved, chain)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *;
        """
        cur.execute(insert_sql, (
            'BUY',
            tx['token'],
            score,
            tx['wallet_address'],
            tx.get('chain', 'ethereum')
        ))
        new_signal = cur.fetchone()
        count += 1

        # Only alert for score >= 75 AND not a stablecoin
        if score >= 75 and tx['token'] not in STABLECOINS:
            send_alert_safe({
                "token": new_signal['token'],
                "signal_type": new_signal['signal_type'],
                "conviction_score": new_signal['conviction_score']
            })

    conn.commit()
    cur.close()
    conn.close()
    return count


def detect_clusters():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Find tokens bought by 2+ different wallets in the last 24 hours
    cluster_query = """
        SELECT
            token,
            COUNT(DISTINCT wallet_address) as wallet_count,
            MAX(chain) as chain
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
            RETURNING *;
        """
        cur.execute(insert_sql, (
            'CLUSTER',
            c['token'],
            score,
            f"{c['wallet_count']} wallets",
            c['chain']
        ))
        new_cluster = cur.fetchone()

        # Only alert for clusters with score >= 75 and not stablecoins
        if score >= 75 and c['token'] not in STABLECOINS:
            send_alert_safe({
                "token": new_cluster['token'],
                "signal_type": "CLUSTER",
                "conviction_score": score
            })

    conn.commit()
    cur.close()
    conn.close()
    return len(clusters)


def run_analytics():
    print("\n--- ANALYTICS ENGINE STARTING ---")
    try:
        signals = detect_signals()
        clusters = detect_clusters()
        print(f"--- ANALYTICS COMPLETE: {signals} Signals, {clusters} Clusters ---")
    except Exception as e:
        print(f"⚠️ Analytics Error: {e}")