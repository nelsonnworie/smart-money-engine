import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'
import { walletData } from '../data/mockData'

const API_BASE = 'https://smart-money-engine-production.up.railway.app'

export default function WalletExplorer() {
  const { isDark } = useTheme()
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  // NEW: Live data state
  const [liveData, setLiveData] = useState(null)
  const [liveLoading, setLiveLoading] = useState(true)
  const [useMock, setUseMock] = useState(false)

  // Old mock data
  const mock = walletData.default

  // NEW: Fetch live data on mount (same pattern as SignalFeed, Clusters, TopMovers)
  useEffect(() => {
    let cancelled = false
    async function fetchLiveData() {
      try {
        const res = await fetch(`${API_BASE}/signals`)
        if (!res.ok) throw new Error('API error')
        const data = await res.json()
        if (!cancelled && data && data.length > 0) {
          setLiveData(data)
          setUseMock(false)
        } else {
          if (!cancelled) setUseMock(true)
        }
      } catch (e) {
        console.warn('Failed to fetch live wallet data, using mock:', e)
        if (!cancelled) setUseMock(true)
      } finally {
        if (!cancelled) setLiveLoading(false)
      }
    }
    fetchLiveData()
    return () => { cancelled = true }
  }, [])

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(query.trim())}`)
      const data = await res.json()
      if (data.error) {
        setError(data.error)
      } else {
        setResult(data)
      }
    } catch (err) {
      setError('Failed to search. Try again.')
    } finally {
      setLoading(false)
    }
  }

  const formatUsd = (amount) => {
    if (!amount) return '$0'
    if (amount >= 1000000) return `$${(amount / 1000000).toFixed(2)}M`
    if (amount >= 1000) return `$${(amount / 1000).toFixed(1)}K`
    return `$${amount.toFixed(0)}`
  }

  const formatTime = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    const now = new Date()
    const diffMins = Math.floor((now - date) / 60000)
    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleDateString()
  }

  const totalVolume = result?.signals?.reduce((s, x) => s + (x.amount_usd || 0), 0) || 0
  const buys = result?.signals?.filter(s => s.type === 'BUY').length || 0
  const sells = result?.signals?.filter(s => s.type === 'SELL').length || 0

  // NEW: Build aggregated data from live signals to power the same card display
  const signals = result?.signals || (useMock ? [] : liveData || [])
  const walletLabel = result?.wallet?.label || (useMock ? mock.ens : 'Live Wallet')
  const walletChain = result?.wallet?.chain || (useMock ? '' : '')
  const displayAddress = query || mock.address
  const displayLabels = result?.wallet?.chain ? [result.wallet.chain] : mock.labels || []
  const displaySignals = result?.signals || []
  const displayTotalHolding = result ? (result.signals?.length || 0) : mock.totalHolding
  const displayPnL = result ? formatUsd(totalVolume) : mock.profitLoss
  const displayTransactions = result ? buys : mock.totalTransactions.toLocaleString()
  const displayLastActive = result ? sells : mock.lastActive

  return (
    <div className="space-y-4">
      <div className={`flex items-center justify-between ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
        <h2 className="text-sm font-bold">Wallet Explorer</h2>
        {!result && (
          <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
            {liveLoading ? 'Loading...' : (useMock ? 'Demo' : 'Live')}
          </span>
        )}
      </div>

      {/* ===== Search Form ===== */}
      <form onSubmit={handleSearch} className={`card-premium rounded-xl p-3 flex gap-3 ${isDark ? 'bg-dark-800/50' : 'bg-white'}`}>
        <input
          type="text"
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search any wallet address (0x... or Solana address)"
          className={`flex-1 px-3 py-2 rounded-lg text-sm font-mono border focus:outline-none focus:ring-2 ${
            isDark
              ? 'bg-dark-800 border-dark-600 text-dark-100 focus:ring-brand-400/30'
              : 'bg-light-50 border-light-200 text-light-800 focus:ring-brand-500/30'
          }`}
        />
        <button
          type="submit"
          disabled={loading}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            loading ? 'opacity-50' : ''
          } ${isDark ? 'bg-brand-500/20 text-brand-400 hover:bg-brand-500/30' : 'bg-brand-500 text-white hover:bg-brand-600'}`}
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && (
        <div className={`p-3 rounded-lg text-sm ${isDark ? 'bg-red-500/10 text-red-400' : 'bg-red-50 text-red-600'}`}>
          {error}
        </div>
      )}

      {/* ===== Wallet Header ===== */}
      <div className={`card-premium rounded-xl p-4 animate-slide-up stagger-1`}>
        <div className="flex items-start gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold flex-shrink-0 ${
            isDark ? 'bg-brand-500/15 text-brand-400 border border-brand-400/20' : 'bg-brand-50 text-brand-600 border border-brand-200'
          }`}>
            W
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-lg font-bold">
                {walletLabel}
              </h2>
              <span className={`text-xs font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                {displayAddress}
              </span>
              {displayLabels.map((l, i) => (
                <span key={i} className={`text-[9px] px-1.5 py-0.5 rounded-full font-mono ${
                  isDark ? 'bg-accent-500/10 text-accent-400' : 'bg-accent-50 text-accent-600'
                }`}>{l}</span>
              ))}
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                  {result ? 'Signals' : 'Total Holdings'}
                </p>
                <p className="text-xl font-bold font-mono text-brand-500">
                  {displayTotalHolding}
                </p>
              </div>
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                  {result ? 'Volume' : 'PnL'}
                </p>
                <p className={`text-xl font-bold font-mono ${isDark ? 'text-green-400' : 'text-green-600'}`}>
                  {displayPnL}
                </p>
              </div>
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                  {result ? 'Buys' : 'Transactions'}
                </p>
                <p className="text-xl font-bold font-mono">
                  {displayTransactions}
                </p>
              </div>
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                  {result ? 'Sells' : 'Last Active'}
                </p>
                <p className="text-xl font-bold font-mono">
                  {displayLastActive}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ===== Signals List ===== */}
      {displaySignals.length > 0 && (
        <div>
          <h3 className={`text-xs font-bold uppercase tracking-wider mb-2 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
            Signals ({displaySignals.length})
          </h3>
          <div className="space-y-2">
            {displaySignals.map(s => (
              <div key={s.id} className={`card-premium rounded-xl p-3 flex items-center gap-3 ${
                s.type === 'BUY' ? 'border-l-2 border-green-500' : 'border-l-2 border-red-500'
              }`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                  s.type === 'BUY'
                    ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-700'
                    : isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-700'
                }`}>
                  {s.type === 'BUY' ? 'B' : 'S'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold">{s.token.startsWith('$') ? s.token : `$${s.token}`}</span>
                    <span className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                      {s.chain}
                    </span>
                  </div>
                  <p className={`text-[11px] font-mono mt-0.5 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    {formatUsd(s.amount_usd)} · {formatTime(s.time)}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className={`text-base font-bold font-mono ${
                    s.conviction >= 80 ? 'text-green-500' : s.conviction >= 70 ? 'text-yellow-500' : 'text-red-500'
                  }`}>
                    {s.conviction}%
                  </p>
                  <div className={`w-10 h-1 rounded-full mt-1 overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
                    <div className="h-full rounded-full" style={{
                      width: `${s.conviction}%`,
                      backgroundColor: s.conviction >= 80 ? '#00d4aa' : s.conviction >= 70 ? '#f59e0b' : '#ef4444'
                    }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ===== Portfolio Section ===== */}
      {mock.topHoldings?.length > 0 && (
        <div className={`card-premium rounded-xl p-4 animate-slide-up stagger-2`}>
          <h3 className={`text-xs font-bold uppercase tracking-wider mb-3 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
            Portfolio
          </h3>
          <div className="space-y-2">
            {mock.topHoldings.map((h, idx) => (
              <div key={h.token} className="animate-slide-up" style={{ animationDelay: `${idx * 80 + 200}ms` }}>
                <div className="flex items-center justify-between mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold">{h.token}</span>
                    <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>{h.amount}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold font-mono">{h.value}</span>
                    <span className={`text-[10px] font-mono ${
                      h.change24h >= 0
                        ? isDark ? 'text-green-400' : 'text-green-600'
                        : isDark ? 'text-red-400' : 'text-red-600'
                    }`}>
                      {h.change24h >= 0 ? '+' : ''}{h.change24h}%
                    </span>
                  </div>
                </div>
                <div className={`h-2 rounded-full overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
                  <div className="h-full rounded-full animate-progress"
                    style={{
                      width: `${h.allocation}%`,
                      background: 'linear-gradient(90deg, #00d4aa, #34d399)',
                      animationDelay: `${idx * 100}ms`,
                    }}
                  />
                </div>
                <div className="flex justify-between mt-0.5">
                  <span className={`text-[9px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                    {h.allocation}% allocation
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ===== Recent Activity Section ===== */}
      {mock.recentActivity?.length > 0 && (
        <div className={`card-premium rounded-xl p-4 animate-slide-up stagger-3`}>
          <h3 className={`text-xs font-bold uppercase tracking-wider mb-3 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
            Recent Activity
          </h3>
          <div className="space-y-2">
            {mock.recentActivity.map((act, idx) => (
              <div key={idx} className={`flex items-center gap-3 p-2 rounded-lg ${isDark ? 'hover:bg-dark-700/50' : 'hover:bg-light-100'} transition-colors animate-fade-in`}
                style={{ animationDelay: `${idx * 100}ms` }}>
                <div className={`w-7 h-7 rounded-md flex items-center justify-center text-[9px] font-bold flex-shrink-0 ${
                  act.type === 'Buy'
                    ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-600'
                    : act.type === 'Sell'
                      ? isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-600'
                      : isDark ? 'bg-accent-500/15 text-accent-400' : 'bg-accent-50 text-accent-600'
                }`}>
                  {act.type === 'Buy' ? 'B' : act.type === 'Sell' ? 'S' : 'Br'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-medium">{act.type} {act.token}</span>
                    <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>{act.amount}</span>
                  </div>
                  <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                    {act.chain} &middot; {act.time} &middot; {act.txHash}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ===== Empty state ===== */}
      {result && !result.wallet && !result.signals?.length && !mock.topHoldings?.length && !mock.recentActivity?.length && (
        <div className={`p-6 text-center rounded-xl ${isDark ? 'bg-dark-800/50 text-dark-400' : 'bg-light-50 text-light-500'}`}>
          No results found for this address
        </div>
      )}
    </div>
  )
}
      