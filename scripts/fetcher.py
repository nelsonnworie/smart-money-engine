"""
fetcher.py — Smart Money Engine v1.5
=====================================
Ethereum + Arbitrum  → Etherscan V2 (free tier, chainid param)
Base                 → Base public RPC eth_getLogs (free, no key)
BSC                  → BSC public RPC eth_getLogs (free, no key)
Solana               → Public Solana RPC (free, no key)

Price resolution chain:
  1. Stablecoin → $1
  2. ETH/WETH   → live Etherscan price
  3. FALLBACK_PRICES → hardcoded map
  4. DeFiLlama (by contract address) → live on-chain price
  5. DexScreener (by contract address) → last-resort DEX price
  6. Return 0
"""

import hashlib
import httpx
import os
import time
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# ─── API key (only for Ethereum + Arbitrum via Etherscan V2) ────────
ETHERSCAN_KEY = os.getenv("ETHERSCAN_KEY", "")

# Base, BSC use public RPCs — no keys needed
# Solana uses public RPC — no key needed

# ─── Endpoints ─────────────────────────────────────────────────────────
ETHERSCAN_V2_URL = "https://api.etherscan.io/v2/api"
BASE_RPC_URL     = "https://mainnet.base.org"
BSC_RPC_URL      = "https://bsc-dataseed.bnbchain.org"
SOLANA_RPC_URL   = "https://api.mainnet-beta.solana.com"
DEFILLAMA_URL    = "https://coins.llama.fi/prices/current"
DEXSCREENER_URL  = "https://api.dexscreener.com/latest/dex/tokens"

# ─── Token lists ─────────────────────────────────────────────────────────

STABLECOINS = {
    "USDT","USDC","DAI","BUSD","TUSD","FRAX","LUSD",
    "USDP","USDS","FDUSD","USDE","PYUSD","CRVUSD",
}

BLOCKLIST = {
    # Scam / spam / meme tokens
    "TRUMPTROLL","XDOGE","KISHU","WOJAK","XD","AKITA","CONAN",
    "FREE","VOLT","CHUD","BAD","DTOKEN","PEIPEI","4CHAN","XEN",
    "STARL","FAERIEDRAGON","SHIB2","ELONGATE","SAFEMOON",
    "NEIRO","FLOKI","RIZO","X","MEME","AMP","BEAM","TURBO",
    "RSR","SPELL","UBX","TLM","SHIB","SOMETHING","BIDEN","HQG",
    "ETHF","ETHG","AF1","AFO","ETHFATHER",
    # Yield-bearing stablecoin wrappers — not real whale signals
    "SUSDAI","SUSDE","SDAI","SUSDS","SFRXETH",
    # Bridged / aliased stablecoins — same as holding USDT/USDC
    "USDT0","USD0","USDBC","AXLUSDC","BRIDGEDUSDC","USD+",
}

NATIVE_WRAPPED = {
    "WETH": "ETH", "WBNB": "BNB", "WSOL": "SOL",
    "WMATIC": "MATIC", "WAVAX": "AVAX",
}

FALLBACK_PRICES = {
    "ETH": 2500.0, "WETH": 2500.0,
    "WBTC": 95000.0,
    "BNB": 600.0, "WBNB": 600.0,
    "SOL": 150.0, "WSOL": 150.0,
    "AVAX": 25.0, "MATIC": 0.55,
    "ARB":  0.45, "OP":   0.90,
    "LINK": 14.0, "UNI":  7.0,  "AAVE": 180.0,
    "CRV":  0.35, "LDO":  1.20, "MKR": 1800.0,
    "SNX":  2.50, "BAL":  2.80, "SUSHI": 0.80,
    "COMP": 45.0, "YFI":  6000.0,
    "GMX":  18.0, "GNS":  1.80,
    "PENDLE": 3.50, "RPL": 10.0,
    "GRT":  0.12, "ONDO": 0.85, "ARKM": 1.20,
    "ATA":  0.05, "REQ":  0.08, "GALA": 0.02,
    "MYRIA": 0.003, "MOODENG": 0.18,
    "GME":  5.50,
    "PEPE": 0.0000142,
    "DOGE": 0.38,
    **{s: 1.0 for s in STABLECOINS},
}

MIN_ALERT_USD     =    50_000
MAX_REALISTIC_USD = 30_000_000
MIN_TOKEN_PRICE   =   0.000001

# ERC-20 Transfer event signature
TRANSFER_EVENT_SIG = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# ---------------------------------------------------------------------------
# Price cache
# ---------------------------------------------------------------------------

_eth_price_cache = {"price": 2500.0, "last_update": 0}
_price_cache: dict = {}


def get_eth_price() -> float:
    """Fetch ETH price via Etherscan V2 stats endpoint."""
    now = time.time()
    if now - _eth_price_cache["last_update"] < 300:
        return _eth_price_cache["price"]
    try:
        r = httpx.get(
            ETHERSCAN_V2_URL,
            params={
                "module":  "stats",
                "action":  "ethprice",
                "chainid": 1,
                "apikey":  ETHERSCAN_KEY,
            },
            timeout=8,
        )
        if r.status_code == 200:
            data = r.json()
            price = float(data.get("result", {}).get("ethusd", 2500))
            _eth_price_cache.update({"price": price, "last_update": now})
            return price
    except Exception:
        pass
    return _eth_price_cache["price"]


def get_token_price(symbol: str, chain: str = "", contract: str = "") -> float:
    """
    Price resolution chain:
      1. Stablecoin → $1
      2. ETH/WETH   → live Etherscan price
      3. FALLBACK_PRICES → hardcoded map
      4. DeFiLlama (by contract address) → live on-chain price
      5. DexScreener (by contract address) → last-resort DEX price
      6. Return 0
    """
    token = symbol.upper().replace("$", "").strip()
    token = NATIVE_WRAPPED.get(token, token)
    now = time.time()

    # ── Check cache ──
    cache_key = f"{token}:{chain}:{contract}"
    if cache_key in _price_cache and now - _price_cache[cache_key][1] < 600:
        return _price_cache[cache_key][0]

    # ── 1. Stablecoins ──
    if token in STABLECOINS:
        _price_cache[cache_key] = (1.0, now)
        return 1.0

    # ── 2. ETH / native gas ──
    if token in ("ETH", "WETH"):
        price = get_eth_price()
        _price_cache[cache_key] = (price, now)
        return price

    # ── 3. Hardcoded fallbacks ──
    if token in FALLBACK_PRICES:
        price = FALLBACK_PRICES[token]
        _price_cache[cache_key] = (price, now)
        return price

    # ── 4. DeFiLlama (live price by contract) ──
    if contract and chain:
        chain_map = {
            "ethereum": "ethereum",
            "arbitrum": "arbitrum",
            "base":     "base",
            "bsc":      "bsc",
            "solana":   "solana",
        }
        llm_chain = chain_map.get(chain.lower())
        if llm_chain and contract.startswith("0x"):
            try:
                url = f"{DEFILLAMA_URL}/{llm_chain}:{contract}"
                r = httpx.get(url, timeout=8)
                if r.status_code == 200:
                    data = r.json().get("coins", {})
                    key = f"{llm_chain}:{contract.lower()}"
                    if key in data:
                        price = float(data[key].get("price", 0))
                        if price > 0:
                            _price_cache[cache_key] = (price, now)
                            return price
            except Exception:
                pass

    # ── 5. DexScreener (last resort, by contract address) ──
    if contract:
        try:
            url = f"{DEXSCREENER_URL}/{contract}"
            r = httpx.get(url, timeout=8)
            if r.status_code == 200:
                pairs = r.json().get("pairs", [])
                if pairs:
                    best_price = 0
                    for pair in pairs:
                        p = float(pair.get("priceUsd", 0) or 0)
                        liq = float(pair.get("liquidity", {}).get("usd", 0) or 0)
                        if p > 0 and liq > 10000 and p > best_price:
                            best_price = p
                    if best_price > 0:
                        _price_cache[cache_key] = (best_price, now)
                        return best_price
        except Exception:
            pass

    # ── 6. Give up ──
    _price_cache[cache_key] = (0.0, now)
    return 0.0


# ---------------------------------------------------------------------------
# Base parser
# ---------------------------------------------------------------------------

class BaseParser:
    chain: str = "unknown"

    def normalize_token(self, symbol: str) -> str:
        t = symbol.upper().replace("$", "").strip()
        return NATIVE_WRAPPED.get(t, t)

    def is_blocked(self, token: str) -> bool:
        return token in BLOCKLIST or token in STABLECOINS

    def compute_usd(self, token: str, raw_amount: int, decimals: int,
                    chain: str = "", contract: str = ""):
        amount = raw_amount / (10 ** max(0, min(decimals, 30)))
        price  = get_token_price(token, chain, contract)
        return round(amount * price, 2), price

    def passes_filters(self, token: str, amount_usd: float, price: float) -> bool:
        if self.is_blocked(token):
            return False
        if price < MIN_TOKEN_PRICE or price == 0:
            return False
        if amount_usd < MIN_ALERT_USD or amount_usd > MAX_REALISTIC_USD:
            return False
        return True

    def get_transactions(self, address: str) -> list[dict]:
        """
        Fetch and parse transactions, then deduplicate by tx_hash.

        Why deduplication is needed:
          A DEX swap generates TWO ERC-20 Transfer events in one tx:
            - Wallet sends USDC  → parser sees SELL
            - Wallet receives ETH → parser sees BUY
          Both share the same tx_hash. Without dedup, the same swap
          fires both a BUY and SELL alert — which is wrong.

        Resolution rule:
          For a swap (both BUY and SELL in same tx), keep the BUY.
          Rationale: receiving a token is the intentional position entry.
          The SELL of the paired token is just the cost of the swap.
          If only one side passes the USD filter, keep that one.
        """
        raw_list = self.fetch(address)

        # Parse all — collect by tx_hash
        by_tx: dict[str, list[dict]] = {}
        for raw in raw_list:
            parsed = self.parse_raw(raw, address)
            if not parsed:
                continue
            tx_hash = parsed.get("tx_hash", "")
            if not tx_hash:
                continue
            by_tx.setdefault(tx_hash, []).append(parsed)

        # Resolve duplicates per tx_hash
        results = []
        for tx_hash, entries in by_tx.items():
            if len(entries) == 1:
                results.append(entries[0])
                continue

            # Multiple transfers in same tx (swap)
            # Prefer BUY (received token = intentional position)
            buys  = [e for e in entries if e.get("action") == "BUY"]
            sells = [e for e in entries if e.get("action") == "SELL"]

            if buys:
                # Keep the highest-value BUY (in case of multi-hop swap)
                best = max(buys, key=lambda e: e.get("amount_usd", 0))
                results.append(best)
            elif sells:
                best = max(sells, key=lambda e: e.get("amount_usd", 0))
                results.append(best)

        return results

    def _rpc_call(self, rpc_url: str, method: str, params: list) -> dict | None:
        """Make a JSON-RPC call."""
        try:
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params,
            }
            r = httpx.post(rpc_url, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"⚠️ [{self.chain}] RPC error ({method}): {e}")
        return None


# ---------------------------------------------------------------------------
# Etherscan V2 parser (Ethereum + Arbitrum)
# ---------------------------------------------------------------------------

class EtherscanV2Parser(BaseParser):
    """Uses Etherscan V2 for chains the free tier supports (ETH, ARB)."""
    chain:    str = ""
    chain_id: int = 1

    def fetch(self, address: str) -> list:
        if not ETHERSCAN_KEY:
            print(f"⚠️ [{self.chain}] ETHERSCAN_KEY not set in .env — skipping {address[:10]}")
            return []

        params = {
            "module":     "account",
            "action":     "tokentx",
            "chainid":    self.chain_id,
            "address":    address,
            "startblock": 0,
            "endblock":   99_999_999,
            "page":       1,
            "offset":     50,
            "sort":       "desc",
            "apikey":     ETHERSCAN_KEY,
        }

        try:
            r = httpx.get(ETHERSCAN_V2_URL, params=params, timeout=30)
            data = r.json()
            if data.get("status") == "1":
                return data.get("result", [])
            elif data.get("message") == "NOTOK":
                err = data.get("result", "unknown")
                if "No transactions found" not in str(err):
                    print(f"⚠️ [{self.chain}] API: {err[:100]}")
            return []
        except Exception as e:
            print(f"⚠️ [{self.chain}] fetch error for {address[:10]}: {e}")
        return []

    def parse_raw(self, raw_tx: dict, wallet_address: str) -> dict | None:
        try:
            token_symbol = raw_tx.get("tokenSymbol", "UNKNOWN")
            token = self.normalize_token(token_symbol)
            if self.is_blocked(token):
                return None

            decimals = int(raw_tx.get("tokenDecimal", 18) or 18)
            raw_val  = int(raw_tx.get("value", 0) or 0)
            contract = raw_tx.get("contractAddress", "")
            amount_usd, price = self.compute_usd(token, raw_val, decimals, self.chain, contract)

            if not self.passes_filters(token, amount_usd, price):
                return None

            to_addr   = raw_tx.get("to", "").lower()
            from_addr = raw_tx.get("from", "").lower()
            wallet    = wallet_address.lower()

            if to_addr == wallet:
                action = "BUY"
            elif from_addr == wallet:
                action = "SELL"
            else:
                return None

            dt = datetime.utcnow()
            try:
                dt = datetime.fromtimestamp(
                    int(raw_tx.get("timeStamp", 0)), tz=timezone.utc
                ).replace(tzinfo=None)
            except Exception:
                pass

            return {
                "tx_hash":        raw_tx.get("hash"),
                "token":          token,
                "amount_usd":     amount_usd,
                "action":         action,
                "timestamp":      dt,
                "from":           from_addr,
                "to":             to_addr,
                "wallet_address": wallet_address,
                "chain":          self.chain,
            }
        except Exception as e:
            print(f"⚠️ [{self.chain}] parse_raw error: {e}")
            return None


# ---------------------------------------------------------------------------
# RPC-based parser (Base, BSC via eth_getLogs)
# ---------------------------------------------------------------------------

class RPCTokenParser(BaseParser):
    """Uses eth_getLogs on public RPCs to get ERC-20 Transfer events."""
    chain:   str = ""
    rpc_url: str = ""

    def fetch(self, address: str) -> list:
        address = address.lower()
        addr_padded = "0x" + address[2:].zfill(64)

        # Query: wallet as receiver (BUY)
        params = [{
            "address": [],
            "topics": [
                TRANSFER_EVENT_SIG,
                None,
                addr_padded,
            ],
            "fromBlock": "0x0",
            "toBlock":   "latest",
        }]
        result = self._rpc_call(self.rpc_url, "eth_getLogs", params)
        logs = []
        if result and "result" in result:
            logs.extend(result["result"])

        # Query: wallet as sender (SELL)
        params[0]["topics"] = [
            TRANSFER_EVENT_SIG,
            addr_padded,
            None,
        ]
        result = self._rpc_call(self.rpc_url, "eth_getLogs", params)
        if result and "result" in result:
            logs.extend(result["result"])

        # Deduplicate
        seen = set()
        unique_logs = []
        for log in logs:
            key = f"{log.get('transactionHash')}_{log.get('logIndex')}"
            if key not in seen:
                seen.add(key)
                unique_logs.append(log)

        unique_logs.sort(key=lambda x: int(x.get("blockNumber", "0x0"), 16), reverse=True)
        return unique_logs[:50]

    def parse_raw(self, log: dict, wallet_address: str) -> dict | None:
        try:
            wallet = wallet_address.lower()
            tx_hash = log.get("transactionHash", "")
            topics = log.get("topics", [])
            data   = log.get("data", "0x")

            if len(topics) < 3:
                return None

            from_addr = "0x" + topics[1][-40:] if len(topics[1]) >= 40 else topics[1]
            to_addr   = "0x" + topics[2][-40:] if len(topics[2]) >= 40 else topics[2]

            if to_addr.lower() == wallet:
                action = "BUY"
            elif from_addr.lower() == wallet:
                action = "SELL"
            else:
                return None

            raw_val = int(data, 16) if data and data != "0x" else 0
            if raw_val == 0:
                return None

            contract = log.get("address", "").lower()
            block_num = int(log.get("blockNumber", "0x0"), 16)

            # Get token info via eth_call
            token_symbol, token_decimals = self._get_token_info(contract)
            token = self.normalize_token(token_symbol)
            if self.is_blocked(token):
                return None

            amount_usd, price = self.compute_usd(token, raw_val, token_decimals, self.chain, contract)

            if not self.passes_filters(token, amount_usd, price):
                return None

            ts = self._get_block_timestamp(block_num)

            return {
                "tx_hash":        tx_hash,
                "token":          token,
                "amount_usd":     amount_usd,
                "action":         action,
                "timestamp":      ts,
                "from":           from_addr.lower(),
                "to":             to_addr.lower(),
                "wallet_address": wallet_address,
                "chain":          self.chain,
            }
        except Exception as e:
            print(f"⚠️ [{self.chain}] parse_raw error: {e}")
            return None

    def _get_token_info(self, contract: str) -> tuple[str, int]:
        """Get token symbol and decimals via eth_call."""
        symbol = "TOKEN"
        decimals = 18
        try:
            # symbol() — 0x95d89b41
            sym_data = self._rpc_call(self.rpc_url, "eth_call", [{
                "to": contract,
                "data": "0x95d89b41",
            }, "latest"])
            if sym_data and "result" in sym_data:
                raw = sym_data["result"]
                if raw and raw != "0x":
                    decoded = bytes.fromhex(raw[2:])
                    try:
                        if len(decoded) > 64:
                            str_len = int.from_bytes(decoded[32:64], 'big')
                            str_bytes = decoded[64:64+str_len]
                            symbol = str_bytes.decode('utf-8', errors='replace').strip('\x00').upper()
                    except Exception:
                        pass

            # decimals() — 0x313ce567
            dec_data = self._rpc_call(self.rpc_url, "eth_call", [{
                "to": contract,
                "data": "0x313ce567",
            }, "latest"])
            if dec_data and "result" in dec_data:
                raw = dec_data["result"]
                if raw and raw != "0x":
                    decimals = int(raw, 16)
        except Exception:
            pass
        return symbol, decimals

    def _get_block_timestamp(self, block_num: int) -> datetime:
        """Get block timestamp via eth_getBlockByNumber."""
        try:
            result = self._rpc_call(self.rpc_url, "eth_getBlockByNumber", [
                hex(block_num), False
            ])
            if result and "result" in result:
                ts = int(result["result"].get("timestamp", "0x0"), 16)
                return datetime.fromtimestamp(ts, tz=timezone.utc).replace(tzinfo=None)
        except Exception:
            pass
        return datetime.utcnow()


# ---------------------------------------------------------------------------
# Chain-specific parsers
# ---------------------------------------------------------------------------

class EthereumParser(EtherscanV2Parser):
    chain    = "ethereum"
    chain_id = 1

class ArbitrumParser(EtherscanV2Parser):
    chain    = "arbitrum"
    chain_id = 42161

class BaseChainParser(RPCTokenParser):
    chain   = "base"
    rpc_url = BASE_RPC_URL

class BNBParser(RPCTokenParser):
    chain   = "bsc"
    rpc_url = BSC_RPC_URL


# ---------------------------------------------------------------------------
# Solana parser — public RPC (FREE, no API key required)
# ---------------------------------------------------------------------------

class SolanaParser(BaseParser):
    chain = "solana"
    RPC_URL = SOLANA_RPC_URL

    def _rpc_call(self, method: str, params: list) -> dict | None:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        try:
            r = httpx.post(self.RPC_URL, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"⚠️ [solana] RPC error ({method}): {e}")
        return None

    def fetch(self, address: str) -> list:
        try:
            result = self._rpc_call("getSignaturesForAddress", [
                address, {"limit": 20}
            ])
            if not result or "result" not in result:
                return []
            signatures = [s["signature"] for s in result["result"] if "signature" in s]
            if not signatures:
                return []
            transactions = []
            for sig in signatures[:10]:  # increased from 5 to 10
                tx_data = self._rpc_call("getTransaction", [
                    sig,
                    {"encoding": "jsonParsed", "maxSupportedTransactionVersion": 0}
                ])
                if tx_data and "result" in tx_data and tx_data["result"]:
                    tx_data["result"]["signature"] = sig
                    transactions.append(tx_data["result"])
                time.sleep(0.3)
            return transactions
        except Exception as e:
            print(f"⚠️ [solana] fetch error for {address[:10]}: {e}")
        return []

    def parse_raw(self, raw_tx: dict, wallet_address: str) -> dict | None:
        try:
            wallet = wallet_address
            account_keys = raw_tx.get("transaction", {}).get("message", {}).get("accountKeys", [])
            pre_sol  = raw_tx.get("meta", {}).get("preBalances", []) or []
            post_sol = raw_tx.get("meta", {}).get("postBalances", []) or []

            # ── Native SOL check ──
            for i, acct in enumerate(account_keys):
                acct_key = acct["pubkey"] if isinstance(acct, dict) else acct
                if acct_key == wallet and i < len(pre_sol) and i < len(post_sol):
                    sol_diff = (post_sol[i] - pre_sol[i]) / 1e9
                    if abs(sol_diff) > 0:
                        action = "BUY" if sol_diff < 0 else "SELL"
                        amount_usd = abs(sol_diff) * get_token_price("SOL")
                        if MIN_ALERT_USD <= amount_usd <= MAX_REALISTIC_USD:
                            dt = datetime.utcnow()
                            try:
                                dt = datetime.fromtimestamp(
                                    raw_tx.get("blockTime", 0), tz=timezone.utc
                                ).replace(tzinfo=None)
                            except Exception:
                                pass
                            return {
                                "tx_hash": raw_tx.get("signature", ""),
                                "token": "SOL",
                                "amount_usd": round(amount_usd, 2),
                                "action": action,
                                "timestamp": dt,
                                "from": wallet if action == "SELL" else "",
                                "to": wallet if action == "BUY" else "",
                                "wallet_address": wallet,
                                "chain": self.chain,
                            }

            # ── SPL token balance check ──
            pre_balances  = raw_tx.get("meta", {}).get("preTokenBalances", []) or []
            post_balances = raw_tx.get("meta", {}).get("postTokenBalances", []) or []
            if not pre_balances or not post_balances:
                return None

            pre_map = {}
            for b in pre_balances:
                mint = b.get("mint", "")
                owner = b.get("owner", "")
                if owner == wallet:
                    amt = int(b.get("uiTokenAmount", {}).get("amount", "0") or "0")
                    dec = int(b.get("uiTokenAmount", {}).get("decimals", 0) or 0)
                    pre_map[mint] = {"amount": amt, "decimals": dec}

            post_map = {}
            for b in post_balances:
                mint = b.get("mint", "")
                owner = b.get("owner", "")
                if owner == wallet:
                    amt = int(b.get("uiTokenAmount", {}).get("amount", "0") or "0")
                    dec = int(b.get("uiTokenAmount", {}).get("decimals", 0) or 0)
                    post_map[mint] = {"amount": amt, "decimals": dec}

            all_mints = set(list(pre_map.keys()) + list(post_map.keys()))
            for mint in all_mints:
                pre_amt  = pre_map.get(mint, {}).get("amount", 0) or 0
                post_amt = post_map.get(mint, {}).get("amount", 0) or 0
                if pre_amt == post_amt:
                    continue
                diff = post_amt - pre_amt
                action = "BUY" if diff > 0 else "SELL"
                sol_change = 0
                for i, acct in enumerate(account_keys):
                    acct_key = acct["pubkey"] if isinstance(acct, dict) else acct
                    if acct_key == wallet and i < len(pre_sol) and i < len(post_sol):
                        sol_change = (post_sol[i] - pre_sol[i]) / 1e9
                        break
                if sol_change == 0:
                    continue
                amount_usd = abs(sol_change) * get_token_price("SOL")
                if amount_usd < MIN_ALERT_USD or amount_usd > MAX_REALISTIC_USD:
                    continue
                dt = datetime.utcnow()
                try:
                    dt = datetime.fromtimestamp(
                        raw_tx.get("blockTime", 0), tz=timezone.utc
                    ).replace(tzinfo=None)
                except Exception:
                    pass
                return {
                    "tx_hash": raw_tx.get("signature", ""),
                    "token": "SPL",
                    "amount_usd": round(amount_usd, 2),
                    "action": action,
                    "timestamp": dt,
                    "from": wallet if action == "SELL" else "",
                    "to": wallet if action == "BUY" else "",
                    "wallet_address": wallet,
                    "chain": self.chain,
                }
            return None
        except Exception as e:
            print(f"⚠️ [solana] parse_raw error: {e}")
            return None


# ---------------------------------------------------------------------------
# Parser registry
# ---------------------------------------------------------------------------

PARSER_REGISTRY: dict[str, BaseParser] = {
    "ethereum": EthereumParser(),
    "arbitrum": ArbitrumParser(),
    "base":     BaseChainParser(),
    "bsc":      BNBParser(),
    "solana":   SolanaParser(),
}


def get_parser(chain: str) -> BaseParser | None:
    return PARSER_REGISTRY.get(chain.lower())


def fetch_wallet_transactions(address: str, chain: str) -> list:
    parser = get_parser(chain)
    if not parser:
        print(f"⚠️ No parser registered for chain: {chain}")
        return []
    return parser.get_transactions(address)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"ETH price:   ${get_eth_price():.2f}")
    print(f"PEPE price:  ${get_token_price('PEPE')}")
    print(f"SOL price:   ${get_token_price('SOL')}")
    print(f"\nRegistered chains: {list(PARSER_REGISTRY.keys())}")
    print(f"ETHERSCAN_KEY: {'✅ Set' if ETHERSCAN_KEY else '❌ Missing'}")

    # Quick test some wallets
    test_wallets = [
        ("0x28a55C4b4f9615FDE3CDAdDf6cc01FcF2E38A6b0", "ethereum"),
        ("0x5D2F4460Ac3514AdA79f5D9838916E508Ab39Bb7", "arbitrum"),
        ("DEXCD63uBftz5TTyRJqqgmPA1sidnYrGToKoXTwfgywo", "solana"),
    ]
    print("\n--- Quick wallet tests ---")
    for addr, ch in test_wallets:
        txs = fetch_wallet_transactions(addr, ch)
        print(f"{ch[:8]} {addr[:10]}... → {len(txs)} parsed txs")
        for t in txs[:3]:
            print(f"   {t['action']} {t['token']} ${t['amount_usd']}")