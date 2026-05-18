import psycopg2
from psycopg2.extras import RealDictCursor
import asyncio
import time
import os
import random
from dotenv import load_dotenv
from backend.telegram_bot import send_telegram_alert

load_dotenv()

STABLECOINS = ["USDT","USDC","DAI","BUSD","TUSD","FRAX","LUSD","USDP","USDS","FDUSD"]

BLOCKLIST = {
    "TRUMPTROLL","XDOGE","KISHU","WOJAK","XD","AKITA","CONAN",
    "FREE","VOLT","CHUD","BAD","DTOKEN","PEIPEI","4CHAN","XEN",
    "STARL","FAERIEDRAGON","SHIB2","ELONGATE","SAFEMOON",
}

BUY_INSIGHTS = [
    "Large position opened by a tracked smart wallet.\nMonitor for follow-up activity.",
    "Significant buy detected above threshold.\nWatch price action closely.",
    "Smart wallet accumulating — position size suggests conviction.\nDYOR.",
]

SELL_INSIGHTS = [
    "Smart wallet reducing position.\nWatch for potential price impact.",
    "Large sell detected — tracked wallet exiting.\nMonitor for continuation.",
    "Significant outflow from a monitored wallet.\nAssess your own exposure.",
]

CLUSTER_INSIGHTS = [
    "Multiple tracked wallets moved the same token recently.\nUnusual coordinated activity.",
    "Cluster of smart wallets accumulating within 12 hours.\nWorth watching closely.",
    "Several independent wallets in sync.\nMonitor for follow-through.",
]


def get_insight(signal_type: str) -> str:
    if signal_type == "BUY":   return random.choice(BUY_INSIGHTS)
    if signal_type == "SELL":  return random.choice(SELL_INSIGHTS)
    return random.choice(CLUSTER_INSIGHTS)


def score_to_label(score: int) -> str:
    """Per design doc Section 5.2: 70-100 = HIGH conviction."""
    if score >= 90: return "MEGA WHALE"
    if score >= 70: return "SIGNIFICANT WHALE"
    return "WHALE"


def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return psycopg2.connect(
            host="localhost", port=5432, dbname="smart_money_db",
            user="postgres", password="DESmond12$$",
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
        print(f"⚠️ Telegram alert failed: {e}")


def detect_signals():
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=RealDictCursor)

    # Per design doc: $10k minimum. We use $50k to reduce noise.
    cur.execute("""
        SELECT * FROM transactions
        WHERE amount_usd >= 50000
          AND amount_usd <= 30000000
          AND timestamp > NOW() - INTERVAL '7 days'
    """)
    txs = cur.fetchall()

    count = 0
    for tx in txs:
        usd    = float(tx["amount_usd"])
        action = str(tx.get("action", "TRANSFER")).upper().strip()
        if action not in ("BUY", "SELL"):
            action = "TRANSFER"

        # Conviction score — per design doc Section 5.2
        # Position size factor (20% weight approximated here until full scoring is live)
        if   usd >= 5_000_000: score = 95
        elif usd >= 1_000_000: score = 85
        elif usd >=   500_000: score = 80
        elif usd >=   100_000: score = 75
        else:                  score = 70  # $50k-$100k — minimum HIGH threshold

        label    = score_to_label(score)
        headline = f"{label} {action}"

        token_bare = tx["token"].replace("$", "").strip().upper()

        if token_bare in STABLECOINS or token_bare in BLOCKLIST:
            continue

        # Deduplication: 30 min window per token+action
        cur.execute("""
            SELECT COUNT(*) FROM signals
            WHERE token = %s
              AND signal_type = %s
              AND created_at > NOW() - INTERVAL '30 minutes'
        """, (tx["token"], action))

        if cur.fetchone()["count"] > 0:
            continue

        cur.execute("""
            INSERT INTO signals
              (signal_type, token, conviction_score, wallets_involved, chain, amount_usd)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (action, tx["token"], score, tx["wallet_address"],
              tx.get("chain", "ethereum"), usd))

        new_signal = cur.fetchone()
        count += 1

        # Alert on score >= 70 per design doc
        if score >= 70:
            send_alert_safe({
                "token":            new_signal["token"],
                "signal_type":      headline,
                "conviction_score": score,
                "amount_usd":       usd,
                "chain":            new_signal["chain"],
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
            MAX(chain)                      AS chain,
            SUM(amount_usd)                 AS total_usd
        FROM transactions
        WHERE timestamp   > NOW() - INTERVAL '7 days'
          AND amount_usd >= 50000
          AND amount_usd <= 30000000
        GROUP BY token
        HAVING COUNT(DISTINCT wallet_address) >= 2
    """)
    clusters = cur.fetchall()

    inserted = 0
    for c in clusters:
        token_bare = c["token"].replace("$", "").strip().upper()
        if token_bare in STABLECOINS or token_bare in BLOCKLIST:
            continue

        score = min(int(c["wallet_count"]) * 20, 100)
        total = float(c["total_usd"] or 0)

        cur.execute("""
            SELECT COUNT(*) FROM signals
            WHERE token = %s
              AND signal_type = 'CLUSTER'
              AND created_at > NOW() - INTERVAL '60 minutes'
        """, (c["token"],))

        if cur.fetchone()["count"] > 0:
            continue

        cur.execute("""
            INSERT INTO signals
              (signal_type, token, conviction_score, wallets_involved, chain, amount_usd)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, ("CLUSTER", c["token"], score,
              f"{c['wallet_count']} wallets", c["chain"], total))

        new_cluster = cur.fetchone()
        inserted += 1

        if score >= 70:
            label = score_to_label(score)
            send_alert_safe({
                "token":            new_cluster["token"],
                "signal_type":      f"{label} CLUSTER",
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


def update_wallet_stats():
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            UPDATE wallets w
            SET
                total_signals      = sub.total,
                profitable_signals = sub.profitable,
                win_rate           = CASE WHEN sub.total = 0 THEN 0
                                          ELSE ROUND((sub.profitable::numeric / sub.total) * 100, 1)
                                     END
            FROM (
                SELECT
                    wallets_involved AS wallet,
                    COUNT(*)         AS total,
                    COUNT(*) FILTER (WHERE s.outcome = 'WIN') AS profitable
                FROM signals s
                GROUP BY wallets_involved
            ) sub
            WHERE w.address = sub.wallet;
        """)
        conn.commit()
    except Exception as e:
        print(f"⚠️ update_wallet_stats skipped: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


def run_analytics():
    print("\n--- ANALYTICS ENGINE STARTING ---")
    try:
        signals  = detect_signals()
        clusters = detect_clusters()
        update_wallet_stats()
        print(f"--- DONE: {signals} new signals, {clusters} new clusters ---")
    except Exception as e:
        print(f"⚠️ Analytics Error: {e}")