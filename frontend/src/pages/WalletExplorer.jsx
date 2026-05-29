import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'

import { API_BASE } from '../config'

export default function WalletExplorer() {
  const { isDark } = useTheme()
  const [query, setQuery] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!query.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await fetch(`${API_BASE}/api/explore?q=${encodeURIComponent(query.trim())}`)
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

  // Compute stats from the search result
  const signals = result?.signals || []
  const transactions = result?.transactions || []
  const wallet = result?.wallet
  const totalVolume = signals.reduce((s, x) => s + (x.amount_usd || 0), 0)
  const buys = signals.filter(s => (s.type || s.signal_type) === 'BUY').length
  const sells = signals.filter(s => (s.type || s.signal_type) === 'SELL').length
  const hasData = wallet || signals.length > 0 || transactions.length > 0

  return (
    <div className="space-y-4">
      <div className={`flex items-center justify-between ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
        <h2 className="text-sm font-bold">Wallet Explorer</h2>
      </div>

      {/* Search Form */}
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

      {/* No search yet */}
      {!result && !loading && !error && (
        <div className={`p-6 text-center rounded-xl ${isDark ? 'bg-dark-800/50 text-dark-400' : 'bg-light-50 text-light-500'}`}>
          Enter a wallet address above to explore signals and transactions
        </div>
      )}

      {/* Wallet Header */}
      {hasData && (
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
                  {wallet?.label || query?.slice(0, 10) + '...' || 'Unknown'}
                </h2>
                <span className={`text-xs font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                  {query}
                </span>
                {wallet?.chain && (
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-mono ${
                    isDark ? 'bg-accent-500/10 text-accent-400' : 'bg-accent-50 text-accent-600'
                  }`}>{wallet.chain}</span>
                )}
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
                <div>
                  <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Signals</p>
                  <p className="text-xl font-bold font-mono text-brand-500">{signals.length}</p>
                </div>
                <div>
                  <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Volume</p>
                  <p className={`text-xl font-bold font-mono ${isDark ? 'text-green-400' : 'text-green-600'}`}>{formatUsd(totalVolume)}</p>
                </div>
                <div>
                  <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Buys</p>
                  <p className="text-xl font-bold font-mono">{buys}</p>
                </div>
                <div>
                  <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Sells</p>
                  <p className="text-xl font-bold font-mono">{sells}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Signals List */}
      {signals.length > 0 && (
        <div>
          <h3 className={`text-xs font-bold uppercase tracking-wider mb-2 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
            Signals ({signals.length})
          </h3>
          <div className="space-y-2">
            {signals.map(s => (
              <div key={s.id} className={`card-premium rounded-xl p-3 flex items-center gap-3 ${
                (s.type || s.signal_type) === 'BUY' ? 'border-l-2 border-green-500' : 'border-l-2 border-red-500'
              }`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                  (s.type || s.signal_type) === 'BUY'
                    ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-700'
                    : isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-700'
                }`}>
                  {(s.type || s.signal_type) === 'BUY' ? 'B' : 'S'}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold">{s.token?.startsWith('$') ? s.token : `$${s.token}`}</span>
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
                    (s.conviction || s.conviction_score) >= 80 ? 'text-green-500' : (s.conviction || s.conviction_score) >= 70 ? 'text-yellow-500' : 'text-red-500'
                  }`}>
                    {s.conviction || s.conviction_score}%
                  </p>
                  <div className={`w-10 h-1 rounded-full mt-1 overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
                    <div className="h-full rounded-full" style={{
                      width: `${s.conviction || s.conviction_score}%`,
                      backgroundColor: (s.conviction || s.conviction_score) >= 80 ? '#00d4aa' : (s.conviction || s.conviction_score) >= 70 ? '#f59e0b' : '#ef4444'
                    }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Transactions List */}
      {transactions.length > 0 && (
        <div>
          <h3 className={`text-xs font-bold uppercase tracking-wider mb-2 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
            Transactions ({transactions.length})
          </h3>
          <div className="space-y-2">
            {transactions.map((t, idx) => (
              <div key={idx} className={`card-premium rounded-xl p-3 flex items-center gap-3`}>
                <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold ${
                  (t.action || '').toUpperCase() === 'BUY'
                    ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-700'
                    : (t.action || '').toUpperCase() === 'SELL'
                      ? isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-700'
                      : isDark ? 'bg-accent-500/15 text-accent-400' : 'bg-accent-50 text-accent-600'
                }`}>
                  {(t.action || '?').charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-bold">{t.token?.startsWith('$') ? t.token : `$${t.token}`}</span>
                    <span className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                      {t.chain}
                    </span>
                  </div>
                  <p className={`text-[11px] font-mono mt-0.5 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    {formatUsd(t.value)} · {formatTime(t.time)} · {t.hash?.slice(0, 10)}...
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state after search */}
      {result && !hasData && (
        <div className={`p-6 text-center rounded-xl ${isDark ? 'bg-dark-800/50 text-dark-400' : 'bg-light-50 text-light-500'}`}>
          No results found for this address
        </div>
      )}
    </div>
  )
}