from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from contextlib import asynccontextmanager
import asyncio
import os

import requests
import json
from pydantic import BaseModel
from backend.database import SessionLocal, engine
from backend.models import Signal, Wallet, Transaction, ProcessedTransaction, Base
from scripts.collector import run_collection


# ---------------------------------------------------------------------------
# Wallet seeder
# ---------------------------------------------------------------------------

def seed_wallets_if_empty():
    db = SessionLocal()
    try:
        import json
        json_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'wallets.json')
        with open(json_path, 'r') as f:
            smart_wallets = json.load(f)

        existing_count = db.query(Wallet).count()
        json_count     = len(smart_wallets)

        if existing_count != json_count:
            print(f"Wallet count mismatch ({existing_count} in DB vs {json_count} in JSON). Syncing...")
            db.query(Wallet).delete()
            db.commit()
            for w in smart_wallets:
                db.add(Wallet(address=w['address'], label=w['label'], chain=w['chain']))
            db.commit()
            print(f"✅ Synced: {json_count} wallets.")
        else:
            print(f"✅ Wallets synced ({existing_count} wallets).")
    except Exception as e:
        print(f"Seed Error: {e}")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Junk cleanup
# ---------------------------------------------------------------------------

JUNK_TOKENS = [
    # Spam / scam tokens
    'NEIRO','FLOKI','RIZO','X','WOJAK','MEME','AMP','BEAM','TURBO',
    'RSR','SPELL','UBX','TLM','VOLT','SHIB','AKITA','PEIPEI','SOMETHING',
    'ETHF','ETHG','AF1','AFO','ETHFATHER','BIDEN','HQG','TRUMPTROLL','CONAN',
    'FREE','FAERIEDRAGON','SHIB2','ELONGATE','SAFEMOON','KISHU','XDOGE',
    'XD','CHUD','BAD','DTOKEN','4CHAN','XEN','STARL',
    # Stablecoins — never valid whale signals
    'USDC','USDT','DAI','WBTC','WETH','USDS','FDUSD','BUSD','TUSD','FRAX',
    # Yield-bearing stablecoin wrappers (appeared in Arbitrum alerts)
    'SUSDAI','USDAI','SUSDE','SDAI','SUSDS','SFRXETH',
    # Bridged / aliased stablecoins
    'USDT0','USD0','USDBC','AXLUSDC','BRIDGEDUSDC',
]


async def clean_orphan_transactions():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("No DATABASE_URL — skipping cleanup.")
        return
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur  = conn.cursor()

        cur.execute("""
            DELETE FROM transactions
            WHERE wallet_address NOT IN (SELECT address FROM wallets)
        """)
        deleted_txs = cur.rowcount

        placeholders = ", ".join(["%s"] * len(JUNK_TOKENS))
        cur.execute(f"""
            DELETE FROM signals
            WHERE amount_usd IS NULL
               OR UPPER(REPLACE(token, '$', '')) IN ({placeholders})
        """, JUNK_TOKENS)
        deleted_signals = cur.rowcount

        cur.execute(f"""
            DELETE FROM transactions
            WHERE UPPER(REPLACE(token, '$', '')) IN ({placeholders})
        """, JUNK_TOKENS)
        deleted_txs_junk = cur.rowcount

        # Also clear junk from processed_transactions so fingerprints
        # from stablecoin variants don't pollute the dedup table
        cur.execute(f"""
            DELETE FROM processed_transactions
            WHERE UPPER(REPLACE(token, '$', '')) IN ({placeholders})
        """, JUNK_TOKENS)
        deleted_processed = cur.rowcount

        conn.commit()
        cur.close()
        conn.close()
        print(
            f"🧹 Cleanup: {deleted_txs} orphan txs, "
            f"{deleted_signals} junk signals, "
            f"{deleted_txs_junk} junk transactions, "
            f"{deleted_processed} junk fingerprints removed."
        )
    except Exception as e:
        print(f"Cleanup error: {e}")


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

async def engine_scheduler():
    while True:
        try:
            print("⚙️  Triggering collection & analytics cycle...")
            await asyncio.to_thread(run_collection)
        except Exception as e:
            print(f"Engine Error: {e}")
        print("💤 Cycle complete. Sleeping 10 minutes...")
        await asyncio.sleep(600)


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

def run_db_migrations():
    """
    Safe column-level migrations for columns added after initial deploy.
    ADD COLUMN IF NOT EXISTS is idempotent — safe to run every startup.
    """
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    if not DATABASE_URL:
        print("No DATABASE_URL — skipping migrations.")
        return
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur  = conn.cursor()

        migrations = [
            # signals.tx_hash — added in v1.1, missing on pre-existing Railway DB
            "ALTER TABLE signals ADD COLUMN IF NOT EXISTS tx_hash VARCHAR",
            "ALTER TABLE signals ADD COLUMN IF NOT EXISTS outcome VARCHAR DEFAULT 'PENDING'",
            # wallets — safety checks
            "ALTER TABLE wallets ADD COLUMN IF NOT EXISTS win_rate FLOAT DEFAULT 0.0",
            "ALTER TABLE wallets ADD COLUMN IF NOT EXISTS total_signals INTEGER DEFAULT 0",
            "ALTER TABLE wallets ADD COLUMN IF NOT EXISTS profitable_signals INTEGER DEFAULT 0",
            "ALTER TABLE wallets ADD COLUMN IF NOT EXISTS outcome VARCHAR DEFAULT 'PENDING'",
        ]

        for sql in migrations:
            try:
                cur.execute(sql)
                conn.commit()
            except Exception as e:
                conn.rollback()
                print(f"Migration note ({sql[:55]}...): {e}")

        cur.close()
        conn.close()
        print("DB migrations complete.")
    except Exception as e:
        print(f"Migration error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    await asyncio.to_thread(run_db_migrations)
    await asyncio.to_thread(seed_wallets_if_empty)
    await clean_orphan_transactions()
    task = asyncio.create_task(engine_scheduler())
    yield
    task.cancel()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(title="Smart Money API", version="1.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Smart Money API v1.1 — live.",
        "endpoints": [
            "/health", "/signals", "/wallets",
            "/top-movers", "/clusters",
            "/admin/db-status", "/admin/dedup-status",
        ]
    }


@app.get("/health")
def health():
    return {"status": "online", "engine": "running", "version": "1.1.0"}


@app.get("/signals")
def get_signals(db: Session = Depends(get_db)):
    return db.query(Signal).order_by(Signal.created_at.desc()).limit(100).all()


@app.get("/wallets")
def get_wallets(db: Session = Depends(get_db)):
    return db.query(Wallet).all()


@app.get("/top-movers")
def get_top_movers(db: Session = Depends(get_db)):
    results = db.query(
        Transaction.token,
        func.count(Transaction.id).label('count')
    ).group_by(Transaction.token).order_by(
        func.count(Transaction.id).desc()
    ).limit(10).all()
    return [{"token": r[0], "count": r[1]} for r in results]

# Add these alongside your existing routes:
@app.get("/api/health")
def api_health():
    return {"status": "online"}

@app.get("/api/analytics/dashboard")
def api_dashboard(db: Session = Depends(get_db)):
    """Return aggregated dashboard stats for the frontend."""
    from sqlalchemy import func
    
    total_signals = db.query(func.count(Signal.id)).scalar() or 0
    total_wallets = db.query(func.count(Wallet.id)).scalar() or 0
    total_tx = db.query(func.count(Transaction.id)).scalar() or 0
    
    latest_signals = db.query(Signal).order_by(Signal.created_at.desc()).limit(10).all()
    
    return {
        "total_signals": total_signals,
        "total_wallets": total_wallets,
        "total_transactions": total_tx,
        "recent_signals": [
            {
                "token": s.token,
                "type": s.signal_type,
                "score": s.conviction_score,
                "amount_usd": s.amount_usd,
                "chain": s.chain,
                "time": str(s.created_at),
            }
            for s in latest_signals
        ],
        "collection_summary": "running",
    }

@app.get("/clusters")
def get_clusters(db: Session = Depends(get_db)):
    return db.query(Signal).filter(
        Signal.signal_type == 'CLUSTER'
    ).order_by(Signal.created_at.desc()).limit(50).all()

@app.get("/api/search")
def search_wallet(q: str = "", db: Session = Depends(get_db)):
    """Search wallets, transactions, or signals by query string."""
    if not q:
        return {"error": "No query provided"}
    
    wallet = None
    signals = []
    txns = []
    error_detail = None
    
    # Each query wrapped individually so one failure doesn't crash the endpoint
    try:
        wallet = db.query(Wallet).filter(
            Wallet.address.ilike(f"%{q}%")
        ).first()
    except Exception as e:
        error_detail = f"Wallet query: {e}"
    
    try:
        signals = db.query(Signal).filter(
            Signal.wallets_involved.ilike(f"%{q}%")
        ).order_by(Signal.created_at.desc()).limit(50).all()
    except Exception as e:
        error_detail = f"Signal query: {e}"
    
    try:
        txns = db.query(Transaction).filter(
            Transaction.wallet_address.ilike(f"%{q}%")
        ).order_by(Transaction.timestamp.desc()).limit(50).all()
    except Exception as e:
        error_detail = f"Transaction query: {e}"
    
    total_signals = len(signals)
    total_volume = sum(s.amount_usd or 0 for s in signals)
    buy_count = sum(1 for s in signals if s.signal_type == 'BUY')
    sell_count = sum(1 for s in signals if s.signal_type == 'SELL')
    
    return {
        "wallet": {
            "address": q,
            "label": wallet.label if wallet else "",
            "chain": wallet.chain if wallet else "",
            "total_signals": total_signals,
            "total_volume": total_volume,
            "buys": buy_count,
            "sells": sell_count,
        } if wallet or total_signals > 0 else None,
        "signals": [
            {
                "id": s.id,
                "token": s.token,
                "type": s.signal_type,
                "signal_type": s.signal_type,
                "amount_usd": s.amount_usd,
                "chain": s.chain,
                "conviction": s.conviction_score,
                "conviction_score": s.conviction_score,
                "time": str(s.created_at),
                "tx_hash": s.tx_hash,
            }
            for s in signals
        ],
        "transactions": [
            {
                "hash": t.tx_hash,
                "token": t.token,
                "value": t.amount_usd,
                "chain": t.chain,
                "action": t.action,
                "time": str(t.timestamp),
            }
            for t in txns
        ],
        "_debug_error": error_detail,
    }


@app.get("/api/explore")
def explore_wallet(q: str = "", db: Session = Depends(get_db)):
    """
    Universal wallet explorer — searches ANY address on any chain.
    Checks internal DB first, then falls back to Etherscan/Solscan/Covalent.
    """
    if not q:
        return {"error": "No address provided"}
    
    q_clean = q.strip()
    result = {
        "wallet": None,
        "signals": [],
        "transactions": [],
        "balances": [],
        "source": "internal"
    }
    
    # --- Step 1: Check internal DB first ---
    wallet = None
    signals = []
    txns = []
    try:
        wallet = db.query(Wallet).filter(Wallet.address.ilike(f"%{q_clean}%")).first()
    except: pass
    try:
        signals = db.query(Signal).filter(Signal.wallets_involved.ilike(f"%{q_clean}%")).order_by(Signal.created_at.desc()).limit(50).all()
    except: pass
    try:
        txns = db.query(Transaction).filter(Transaction.wallet_address.ilike(f"%{q_clean}%")).order_by(Transaction.timestamp.desc()).limit(50).all()
    except: pass
    
    if wallet or signals or txns:
        total_volume = sum(s.amount_usd or 0 for s in signals)
        buy_count = sum(1 for s in signals if s.signal_type == 'BUY')
        sell_count = sum(1 for s in signals if s.signal_type == 'SELL')
        result.update({
            "wallet": {
                "address": q_clean,
                "label": wallet.label if wallet else "Monitored Wallet",
                "chain": wallet.chain if wallet else "unknown",
                "total_signals": len(signals),
                "total_volume": total_volume,
                "buys": buy_count,
                "sells": sell_count,
            } if wallet or signals else None,
            "signals": [
                {"id": s.id, "token": s.token, "type": s.signal_type, "signal_type": s.signal_type, "amount_usd": s.amount_usd, "chain": s.chain, "conviction": s.conviction_score, "conviction_score": s.conviction_score, "time": str(s.created_at), "tx_hash": s.tx_hash}
                for s in signals
            ],
            "transactions": [
                {"hash": t.tx_hash, "token": t.token, "value": t.amount_usd, "chain": t.chain, "action": t.action, "time": str(t.timestamp)}
                for t in txns
            ],
            "source": "internal"
        })
        return result
    
    # --- Step 2: Not in DB — try external APIs ---
    
    # Detect chain by address format
    if q_clean.startswith('0x') and len(q_clean) == 42:
        # Ethereum / EVM chain
        etherscan_key = os.getenv("ETHERSCAN_KEY", "")
        
        try:
            # Get ETH balance
            eth_balance = 0
            try:
                bal_resp = requests.get(
                    f"https://api.etherscan.io/api?module=account&action=balance&address={q_clean}&tag=latest&apikey={etherscan_key}",
                    timeout=10
                )
                bal_data = bal_resp.json()
                if bal_data.get('status') == '1':
                    eth_balance = int(bal_data['result']) / 1e18
            except: pass
            
            # Get recent transactions
            external_txns = []
            try:
                tx_resp = requests.get(
                    f"https://api.etherscan.io/api?module=account&action=txlist&address={q_clean}&startblock=0&endblock=99999999&sort=desc&apikey={etherscan_key}",
                    timeout=10
                )
                tx_data = tx_resp.json()
                if tx_data.get('status') == '1':
                    for tx in tx_data['result'][:20]:
                        external_txns.append({
                            "hash": tx['hash'],
                            "token": "ETH",
                            "value": int(tx['value']) / 1e18,
                            "chain": "ethereum",
                            "action": "RECEIVE" if tx['to'].lower() == q_clean.lower() else "SEND",
                            "time": tx['timeStamp'],
                        })
            except: pass
            
            # Get ERC-20 token balances via Covalent
            balances = []
            covalent_key = os.getenv("COVALENT_KEY", "")
            if covalent_key:
                try:
                    cov_resp = requests.get(
                        f"https://api.covalenthq.com/v1/1/address/{q_clean}/balances_v2/?key={covalent_key}",
                        timeout=10
                    )
                    cov_data = cov_resp.json()
                    if cov_data.get('data') and cov_data['data'].get('items'):
                        for item in cov_data['data']['items'][:10]:
                            if item['balance'] and int(item['balance']) > 0:
                                decimals = int(item['contract_decimals']) if item.get('contract_decimals') else 18
                                raw_balance = int(item['balance'])
                                if raw_balance > 0:
                                    human_balance = raw_balance / (10 ** decimals)
                                    balances.append({
                                        "token": item.get('contract_ticker_symbol', 'UNKNOWN'),
                                        "contract": item.get('contract_address', ''),
                                        "balance": round(human_balance, 4),
                                        "value_usd": round(item.get('quote', 0), 2) if item.get('quote') else None,
                                        "logo": item.get('logo_url', ''),
                                    })
                except: pass
            
            result.update({
                "wallet": {
                    "address": q_clean,
                    "label": "Ethereum Wallet",
                    "chain": "ethereum",
                    "eth_balance": round(eth_balance, 4),
                },
                "transactions": external_txns,
                "balances": balances,
                "source": "etherscan"
            })
        except Exception as e:
            result["error"] = str(e)
    
    elif len(q_clean) >= 32 and not q_clean.startswith('0x'):
        # Solana address
        solscan_key = os.getenv("SOLSCAN_KEY", "")
        helius_key = os.getenv("HELIUS_KEY", "")
        
        try:
            # Get SOL balance via Helius
            sol_balance = 0
            if helius_key:
                try:
                    hel_resp = requests.post(
                        f"https://api.helius.xyz/v0/addresses/{q_clean}/balances?apiKey={helius_key}",
                        timeout=10
                    )
                    hel_data = hel_resp.json()
                    if hel_data and 'tokens' in hel_data:
                        for tok in hel_data['tokens']:
                            if tok.get('mint') == 'So11111111111111111111111111111111111111112':
                                sol_balance = tok.get('amount', 0) / 1e9
                except: pass
            
            # Get recent Solana transactions via Solscan
            external_txns = []
            if solscan_key:
                try:
                    ss_resp = requests.get(
                        f"https://api.solscan.io/v2/account/transactions?address={q_clean}&limit=20",
                        headers={"Accept": "application/json", "token": solscan_key},
                        timeout=10
                    )
                    ss_data = ss_resp.json()
                    if ss_data and ss_data.get('data'):
                        for tx in ss_data['data'][:20]:
                            external_txns.append({
                                "hash": tx.get('txHash', ''),
                                "token": "SOL",
                                "value": (tx.get('lamports', 0) or 0) / 1e9,
                                "chain": "solana",
                                "action": tx.get('txType', 'UNKNOWN'),
                                "time": str(tx.get('blockTime', '')),
                            })
                except: pass
            
            result.update({
                "wallet": {
                    "address": q_clean,
                    "label": "Solana Wallet",
                    "chain": "solana",
                    "sol_balance": round(sol_balance, 4),
                },
                "transactions": external_txns,
                "source": "solscan"
            })
        except Exception as e:
            result["error"] = str(e)
    
    else:
        # Unknown format — try Covalent anyway
        covalent_key = os.getenv("COVALENT_KEY", "")
        result.update({
            "wallet": {"address": q_clean, "label": "Unknown Wallet", "chain": "unknown"},
            "source": "external"
        })
    
    return result


@app.get("/admin/db-status")
def db_status(db: Session = Depends(get_db)):
    signal_tokens = db.execute(text(
        "SELECT token, COUNT(*) as count, MIN(amount_usd) as min_usd "
        "FROM signals GROUP BY token ORDER BY count DESC LIMIT 20"
    )).fetchall()
    tx_wallets = db.execute(text(
        "SELECT wallet_address, COUNT(*) as count "
        "FROM transactions GROUP BY wallet_address ORDER BY count DESC LIMIT 10"
    )).fetchall()
    return {
        "signal_tokens": [
            {"token": r[0], "count": r[1], "min_usd": r[2]}
            for r in signal_tokens
        ],
        "tx_wallets": [
            {"wallet": r[0][:20] + "...", "count": r[1]}
            for r in tx_wallets
        ],
        "total_signals":       db.execute(text("SELECT COUNT(*) FROM signals")).scalar(),
        "total_transactions":  db.execute(text("SELECT COUNT(*) FROM transactions")).scalar(),
        "total_processed":     db.execute(text("SELECT COUNT(*) FROM processed_transactions")).scalar(),
    }


@app.get("/admin/dedup-status")
def dedup_status(db: Session = Depends(get_db)):
    """Shows the permanent deduplication memory status."""
    recent = db.execute(text("""
        SELECT token, action, chain, amount_usd, alerted, processed_at
        FROM processed_transactions
        ORDER BY processed_at DESC
        LIMIT 20
    """)).fetchall()
    total = db.execute(text("SELECT COUNT(*) FROM processed_transactions")).scalar()
    alerted = db.execute(text(
        "SELECT COUNT(*) FROM processed_transactions WHERE alerted = 'YES'"
    )).scalar()
    return {
        "total_processed": total,
        "total_alerted":   alerted,
        "recent_entries": [
            {
                "token":        r[0],
                "action":       r[1],
                "chain":        r[2],
                "amount_usd":   r[3],
                "alerted":      r[4],
                "processed_at": str(r[5]),
            }
            for r in recent
        ],
    }

# ---------------------------------------------------------------------------
# Settings Routes
# ---------------------------------------------------------------------------

DEFAULT_SETTINGS = {
    "alert_threshold": 70,
    "min_volume": 10000,
    "chains": {
        "ethereum": True,
        "solana": True,
        "arbitrum": True,
        "base": True,
        "bnb": True,
    },
    "signal_types": {
        "BUY": True,
        "SELL": True,
        "CLUSTER": True,
    },
    "notification_sounds": True,
    "telegram_enabled": False,
}

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), '..', 'user_settings.json')

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
    except: pass
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

@app.get("/api/settings")
def get_settings():
    return load_settings()

@app.post("/api/settings")
def update_settings(body: dict):
    current = load_settings()
    current.update(body)
    save_settings(current)
    return {"status": "saved", "settings": current}