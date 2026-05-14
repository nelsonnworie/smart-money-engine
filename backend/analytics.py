import psycopg2
from psycopg2.extras import RealDictCursor
import asyncio
import time
import os
from dotenv import load_dotenv
from backend.telegram_bot import send_telegram_alert

load_dotenv()

STABLECOINS = [
    "USDT", "USDC", "DAI", "BUSD", "TUSD",
    "FRAX", "LUSD", "USDP", "USDS", "FDUSD",
]


def send_alert_safe(alert_data):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_telegram_alert(alert_data))
        loop.close()
        time.sleep(1)
    except Exception as e:
        print(f"⚠️ Telegram alert failed: {e}")


def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return psycopg2.connect(
            host="localhost",
            port=5432,
            dbname="smart_money_db",
            user="postgres",
            password="DESmond12$$"
        )
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(DATABASE_URL)


def detect_signals():
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM transactions
        WHERE amount_usd >= 100000
          AND timestamp > NOW() - INTERVAL '1 hour'
    """)
    txs = cur.fetchall()

    count = 0
    for tx in txs:
        if   tx['amount_usd'] >= 500000: score = 95
        elif tx['amount_usd'] >= 250000: score = 85
        elif tx['amount_usd'] >= 100000: score = 75
        else:                            score = 40

        cur.execute("""
            INSERT INTO signals
                (signal_type, token, conviction_score, wallets_involved, chain, amount_usd)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            tx['action'],
            tx['token'],
            score,
            tx['wallet_address'],
            tx.get('chain', 'ethereum'),
            tx['amount_usd'],
        ))
        new_signal = cur.fetchone()
        count += 1

        if score >= 75 and tx['token'] not in STABLECOINS:
            send_alert_safe({
                "token":            new_signal['token'],
                "signal_type":      new_signal['signal_type'],
                "conviction_score": new_signal['conviction_score'],
                "amount_usd":       tx['amount_usd'],
                "chain":            tx.get('chain', 'ethereum'),
                "wallet":           tx['wallet_address'],
            })

    conn.commit()
    cur.close()
    conn.close()
    return count


def detect_clusters():
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            token,
            COUNT(DISTINCT wallet_address) AS wallet_count,
            MAX(chain)                     AS chain,
            SUM(amount_usd)                AS total_usd
        FROM transactions
        WHERE timestamp > NOW() - INTERVAL '24 hours'
          AND amount_usd >= 100000
        GROUP BY token
        HAVING COUNT(DISTINCT wallet_address) >= 2
    """)
    clusters = cur.fetchall()

    for c in clusters:
        score = min(c['wallet_count'] * 20, 100)

        cur.execute("""
            INSERT INTO signals
                (signal_type, token, conviction_score, wallets_involved, chain, amount_usd)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            'CLUSTER',
            c['token'],
            score,
            f"{c['wallet_count']} wallets",
            c['chain'],
            float(c['total_usd'] or 0),
        ))
        new_cluster = cur.fetchone()

        if score >= 75 and c['token'] not in STABLECOINS:
            send_alert_safe({
                "token":            new_cluster['token'],
                "signal_type":      "CLUSTER",
                "conviction_score": score,
                "amount_usd":       float(c['total_usd'] or 0),
                "chain":            c['chain'],
                "wallet":           f"{c['wallet_count']} wallets",
            })

    conn.commit()
    cur.close()
    conn.close()
    return len(clusters)


def run_analytics():
    print("\n--- ANALYTICS ENGINE STARTING ---")
    try:
        signals  = detect_signals()
        clusters = detect_clusters()
        print(f"--- ANALYTICS COMPLETE: {signals} Signals, {clusters} Clusters ---")
    except Exception as e:
        print(f"⚠️ Analytics Error: {e}")