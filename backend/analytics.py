"""
analytics.py — Signal detection engine
=======================================
Fixes applied vs original:
  1. Permanent deduplication via processed_transactions fingerprint.
     Any tx alerted once is NEVER alerted again. No time windows.
  2. signal_type stored as raw action (BUY | SELL | CLUSTER) only.
     Telegram builds the display label — no double-prefixing.
  3. BUY/SELL classification done by parser (fetcher.py), not here.
  4. Dedup check happens BEFORE Telegram delivery, write is atomic.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import asyncio
import time
import os
import random
from dotenv import load_dotenv
from backend.telegram_bot import send_telegram_alert
from backend.database import build_fingerprint, mark_as_processed

load_dotenv()

STABLECOINS = {
    "USDT","USDC","DAI","BUSD","TUSD","FRAX","LUSD",
    "USDP","USDS","FDUSD","USDE","PYUSD","CRVUSD",
}

BLOCKLIST = {
    "TRUMPTROLL","XDOGE","KISHU","WOJAK","XD","AKITA","CONAN",
    "FREE","VOLT","CHUD","BAD","DTOKEN","PEIPEI","4CHAN","XEN",
    "STARL","FAERIEDRAGON","SHIB2","ELONGATE","SAFEMOON",
    "NEIRO","FLOKI","RIZO","X","MEME","AMP","BEAM","TURBO",
    "RSR","SPELL","UBX","TLM","SHIB","SOMETHING",
    "ETHF","ETHG","AF1","AFO","ETHFATHER","BIDEN","HQG",
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
    t = signal_type.upper()
    if t == "BUY":     return random.choice(BUY_INSIGHTS)
    if t == "SELL":    return random.choice(SELL_INSIGHTS)
    return random.choice(CLUSTER_INSIGHTS)


def score_to_label(score: int) -> str:
    if score >= 90: return "MEGA WHALE"
    if score >= 70: return "SIGNIFICANT WHALE"
    return "WHALE"


def get_db_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        return psycopg2.connect(
            host="localhost", port=5432, dbname="smart_money_db",
            user="postgres", password="postgres",
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
    """
    Core signal detection loop.

    Deduplication flow (per design doc):
      1. Build fingerprint for this tx
      2. Attempt atomic INSERT into processed_transactions
         → if INSERT succeeds: first time seen → proceed to alert
         → if INSERT fails (UNIQUE violation): already processed → skip
      3. Send Telegram AFTER successful insert only

    This ensures:
      - No duplicate alerts even across concurrent workers
      - No time-window gaps (permanent memory)
      - Alert send failure does NOT cause re-alert (fingerprint already written)
    """
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT * FROM transactions
        WHERE amount_usd >= 50000
          AND amount_usd <= 30000000
          AND timestamp  > NOW() - INTERVAL '30 days'
          AND action IN ('BUY', 'SELL')
        ORDER BY timestamp DESC
    """)
    txs = cur.fetchall()

    count = 0
    for tx in txs:
        usd    = float(tx["amount_usd"])
        action = str(tx.get("action", "BUY")).upper().strip()

        if action not in ("BUY", "SELL"):
            continue

        token_bare = tx["token"].replace("$", "").strip().upper()
        if token_bare in STABLECOINS or token_bare in BLOCKLIST:
            continue

        # Conviction score
        if   usd >= 5_000_000: score = 95
        elif usd >= 1_000_000: score = 85
        elif usd >=   500_000: score = 80
        elif usd >=   100_000: score = 75
        else:                  score = 70

        chain      = tx.get("chain", "ethereum") or "ethereum"
        tx_hash    = tx.get("tx_hash", "")
        wallet     = tx.get("wallet_address", "")

        # ── PERMANENT DEDUPLICATION ─────────────────────────────────────────
        # Build fingerprint FIRST. Attempt atomic write BEFORE alert.
        # DB unique constraint is the actual lock — safe under concurrency.
        fingerprint = build_fingerprint(chain, tx_hash, wallet, token_bare, action)

        inserted = mark_as_processed(
            fingerprint   = fingerprint,
            tx_hash       = tx_hash,
            wallet_address= wallet,
            token         = token_bare,
            action        = action,
            chain         = chain,
            amount_usd    = usd,
            alerted       = "YES" if score >= 70 else "SKIPPED",
        )

        if not inserted:
            # Already processed — skip permanently
            continue
        # ── END DEDUPLICATION ───────────────────────────────────────────────

        # Insert signal record
        cur.execute("""
            INSERT INTO signals
              (signal_type, token, conviction_score, wallets_involved, chain, amount_usd, tx_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            action,           # ← raw action only: BUY | SELL
            tx["token"],
            score,
            wallet,
            chain,
            usd,
            tx_hash,
        ))
        new_signal = cur.fetchone()
        conn.commit()
        count += 1

        if score >= 70:
            send_alert_safe({
                "token":            new_signal["token"],
                "signal_type":      action,       # ← raw: BUY | SELL (Telegram builds label)
                "conviction_score": score,
                "amount_usd":       usd,
                "chain":            chain,
                "wallet":           wallet,
                "insight":          get_insight(action),
            })

    cur.close()
    conn.close()
    return count


def detect_clusters():
    """
    Cluster detection — multiple wallets moving the same token.
    Uses same permanent dedup flow via a synthetic cluster fingerprint.
    """
    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT
            token,
            COUNT(DISTINCT wallet_address) AS wallet_count,
            MAX(chain)                      AS chain,
            SUM(amount_usd)                 AS total_usd,
            STRING_AGG(DISTINCT wallet_address, ',') AS wallets
        FROM transactions
        WHERE timestamp   > NOW() - INTERVAL '30 days'
          AND amount_usd >= 50000
          AND amount_usd <= 30000000
          AND action IN ('BUY', 'SELL')
        GROUP BY token
        HAVING COUNT(DISTINCT wallet_address) >= 2
    """)
    clusters = cur.fetchall()

    inserted = 0
    for c in clusters:
        token_bare = c["token"].replace("$", "").strip().upper()
        if token_bare in STABLECOINS or token_bare in BLOCKLIST:
            continue

        wallet_count = int(c["wallet_count"])
        score        = min(wallet_count * 20, 100)
        total        = float(c["total_usd"] or 0)
        chain        = c["chain"] or "ethereum"

        # Cluster fingerprint: deterministic on token + wallet set + day
        from datetime import date
        today       = date.today().isoformat()
        wallets_key = ",".join(sorted((c["wallets"] or "").split(",")))
        cluster_fp  = build_fingerprint(chain, today, wallets_key, token_bare, "CLUSTER")

        inserted_ok = mark_as_processed(
            fingerprint    = cluster_fp,
            tx_hash        = f"cluster_{today}_{token_bare}",
            wallet_address = wallets_key[:200],
            token          = token_bare,
            action         = "CLUSTER",
            chain          = chain,
            amount_usd     = total,
            alerted        = "YES" if score >= 70 else "SKIPPED",
        )

        if not inserted_ok:
            continue

        cur.execute("""
            INSERT INTO signals
              (signal_type, token, conviction_score, wallets_involved, chain, amount_usd)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING *;
        """, (
            "CLUSTER",
            c["token"],
            score,
            f"{wallet_count} wallets",
            chain,
            total,
        ))
        new_cluster = cur.fetchone()
        conn.commit()
        inserted += 1

        if score >= 70:
            send_alert_safe({
                "token":            new_cluster["token"],
                "signal_type":      "CLUSTER",   # ← raw action
                "conviction_score": score,
                "amount_usd":       total,
                "chain":            chain,
                "wallet":           f"{wallet_count} wallets",
                "insight":          get_insight("CLUSTER"),
            })

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