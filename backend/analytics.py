import psycopg2
from psycopg2.extras import RealDictCursor
import asyncio
import time
import os
import random
from dotenv import load_dotenv
from backend.telegram_bot import send_telegram_alert

load_dotenv()

STABLECOINS = [
    "USDT", "USDC", "DAI", "BUSD", "TUSD",
    "FRAX", "LUSD", "USDP", "USDS", "FDUSD",
    "USDE", "PYUSD", "GUSD", "HUSD", "SUSD",
]

BLOCKLIST = [
    "TRUMPTROLL", "XDOGE", "KISHU", "WOJAK", "XD", "AKITA",
    "CONAN", "FREE", "VOLT", "CHUD", "BAD", "DTOKEN", "PEIPEI",
    "4CHAN", "XEN", "STARL", "FAERIEDRAGON", "BIDEN", "HQG",
    "ETHF", "ETHG", "AF1", "AFO", "ETHFATHER",
]

BUY_INSIGHTS = [
    "Large position opened by a tracked smart wallet. Monitor for follow-up activity.",
    "Significant buy detected above threshold. Watch price action closely.",
    "Smart wallet accumulating — position size suggests high conviction. DYOR.",
]
SELL_INSIGHTS = [
    "Smart wallet reducing position. Watch for potential price impact.",
    "Large sell detected — tracked wallet exiting. Monitor for continuation.",
    "Significant outflow from a monitored wallet. Assess your own exposure.",
]
CLUSTER_INSIGHTS = [
    "Multiple tracked wallets moved the same token recently. Unusual coordinated activity.",
    "Cluster of smart wallets accumulating within 12 hours. Worth watching closely.",
    "Several independent wallets in sync — rare pattern. Monitor for follow-through.",
]


def get_insight(signal_type: str) -> str:
    if signal_type == "BUY":
        return random.choice(BUY_INSIGHTS)
    elif signal_type == "SELL":
        return random.choice(SELL_INSIGHTS)
    return random.choice(CLUSTER_INSIGHTS)


def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return psycopg2.connect(
            host="localhost", port=5432,
            dbname="smart_money_db",
            user="postgres",
            password="DESmond12$$",
        )
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return psycopg2.connect(DATABASE_URL)


def send_alert_safe(alert_data: dict):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(send_telegram_alert(alert_data))
        loop.close()
        time.sleep(1)
    except Exception as e:
        print(f"  Alert failed: {e}")


def clean_token(raw: str) -> str:
    """Always return uppercase token without $ prefix e.g. ETH not $ETH."""
    return raw.replace("$", "").strip().upper()


def detect_signals():
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM transactions
        WHERE amount_usd >= 100000
          AND amount_usd <= 50000000
          AND timestamp > NOW() - INTERVAL '1 hour'
    """)
    txs = cur.fetchall()

    count = 0
    for tx in txs:
        usd    = float(tx["amount_usd"])
        token  = clean_token(tx["token"])
        action = str(tx.get("action", "BUY")).upper().strip()
        if action not in ("BUY", "SELL"):
            action = "BUY"

        # Skip stablecoins and blocklisted tokens
        if token in STABLECOINS or token in BLOCKLIST:
            continue

        # Score by size
        if   usd >= 1_000_000: score = 95
        elif usd >=   500_000: score = 85
        elif usd >=   250_000: score = 80
        else:                  score = 75

        # Deduplication — skip if same token+action signal in last 30 min
        cur.execute("""
            SELECT COUNT(*) as count FROM signals
            WHERE token = %s
              AND signal_type = %s
              AND created_at > NOW() - INTERVAL '30 minutes'
        """, (token, action))
        if cur.fetchone()["count"] > 0:
            continue

        # Insert signal — includes amount_usd
        cur.execute("""
            INSERT INTO signals
                (signal_type, token, conviction_score, wallets_involved, chain, amount_usd)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            action,
            token,
            score,
            tx["wallet_address"],
            tx.get("chain", "ethereum"),
            usd,
        ))
        new_signal = cur.fetchone()
        count += 1

        print(f"  Signal: {action} {token} ${usd:,.0f} score={score}")

        send_alert_safe({
            "token":            token,
            "signal_type":      action,
            "conviction_score": score,
            "amount_usd":       usd,
            "chain":            tx.get("chain", "ethereum"),
            "wallet":           tx["wallet_address"],
            "insight":          get_insight(action),
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
        WHERE timestamp   > NOW() - INTERVAL '12 hours'
          AND amount_usd >= 100000
          AND amount_usd <= 50000000
        GROUP BY token
        HAVING COUNT(DISTINCT wallet_address) >= 2
    """)
    clusters = cur.fetchall()

    inserted = 0
    for c in clusters:
        token = clean_token(c["token"])
        if token in STABLECOINS or token in BLOCKLIST:
            continue

        score = min(int(c["wallet_count"]) * 20, 100)
        total = float(c["total_usd"] or 0)

        # Deduplication
        cur.execute("""
            SELECT COUNT(*) as count FROM signals
            WHERE token = %s
              AND signal_type = 'CLUSTER'
              AND created_at > NOW() - INTERVAL '60 minutes'
        """, (token,))
        if cur.fetchone()["count"] > 0:
            continue

        # Insert cluster signal — includes amount_usd
        cur.execute("""
            INSERT INTO signals
                (signal_type, token, conviction_score, wallets_involved, chain, amount_usd)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            "CLUSTER",
            token,
            score,
            f"{c['wallet_count']} wallets",
            c["chain"],
            total,
        ))
        new_cluster = cur.fetchone()
        inserted += 1

        print(f"  Cluster: {token} {c['wallet_count']} wallets ${total:,.0f} score={score}")

        send_alert_safe({
            "token":            token,
            "signal_type":      "CLUSTER",
            "conviction_score": score,
            "amount_usd":       total,
            "chain":            c["chain"],
            "wallet":           f"{c['wallet_count']} wallets",
            "insight":          get_insight("CLUSTER"),
        })

    conn.commit()
    cur.close()
    conn.close()
    return inserted


def run_analytics():
    print("\n--- ANALYTICS ENGINE STARTING ---")
    try:
        signals  = detect_signals()
        clusters = detect_clusters()
        print(f"--- DONE: {signals} new signals, {clusters} new clusters ---")
    except Exception as e:
        print(f"Analytics Error: {e}")