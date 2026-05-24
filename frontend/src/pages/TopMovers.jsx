import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'

const API_BASE = 'https://smart-money-engine-production.up.railway.app'

export default function TopMovers({ activeNav }) {
  const { isDark } = useTheme()
  const [movers, setMovers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function fetchData() {
      try {
        const res = await fetch(`${API_BASE}/signals`)
        if (!res.ok) throw new Error('API error')
        const data = await res.json()
        if (!cancelled) {
          // Step 1: If a chain filter is active, filter the raw data first
          let filteredData = data
          if (['eth', 'sol', 'arb', 'base', 'bnb'].includes(activeNav)) {
            const chainMap = { eth: 'ethereum', sol: 'solana', arb: 'arbitrum', base: 'base', bnb: 'bnb' }
            const targetChain = chainMap[activeNav]
            if (targetChain) {
              filteredData = data.filter(s => {
                const chain = (s.chain || '').toLowerCase()
                return chain === targetChain
              })
            }
          }

          // Step 2: Aggregate by token (works on either full or chain-filtered data)
          const tokenMap = {}
          filteredData.forEach(s => {
            const key = (s.token || 'UNKNOWN').replace('$', '')
            if (!tokenMap[key]) {
              tokenMap[key] = { token: key, buys: 0, sells: 0, volume: 0, count: 0, totalConviction: 0, chains: new Set() }
            }
            tokenMap[key].count++
            tokenMap[key].volume += s.amount_usd || 0
            tokenMap[key].totalConviction += s.conviction_score || 0
            if (s.signal_type === 'BUY') tokenMap[key].buys++
            if (s.signal_type === 'SELL') tokenMap[key].sells++
            tokenMap[key].chains.add(s.chain || 'unknown')
          })

          let sorted = Object.values(tokenMap)
            .sort((a, b) => b.volume - a.volume)
            .slice(0, 20)
            .map((t, i) => ({
              rank: i + 1,
              token: t.token,
              name: t.token,
              price: `$${(t.volume / t.count / 1000).toFixed(2)}`,
              change24h: Math.round((t.buys - t.sells) / Math.max(t.count, 1) * 10),
              volume: t.volume >= 1000000 ? `$${(t.volume / 1000000).toFixed(1)}M` : `$${(t.volume / 1000).toFixed(1)}K`,
              signal: t.buys > t.sells ? 'Strong Buy' : t.sells > t.buys ? 'Distribution' : 'Neutral',
              conviction: Math.round(t.totalConviction / t.count),
              smartMoneyFlow: t.buys > t.sells ? 'Net Buying' : 'Net Selling',
              walletCount: t.count,
            }))

          // Step 3: Apply conviction filters (high / medium / low)
          if (activeNav === 'high') sorted = sorted.filter(m => m.conviction >= 80)
          else if (activeNav === 'medium') sorted = sorted.filter(m => m.conviction >= 50 && m.conviction < 80)
          else if (activeNav === 'low') sorted = sorted.filter(m => m.conviction < 50)

          setMovers(sorted)
        }
      } catch (e) {
        console.warn('Failed to fetch top movers:', e)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    fetchData()
    return () => { cancelled = true }
  }, [activeNav])

  const chainNames = {
    eth: 'Ethereum',
    sol: 'Solana',
    arb: 'Arbitrum',
    base: 'Base',
    bnb: 'BNB Chain',
  }

  if (loading) {
    return (
      <div className="space-y-3 pb-4">
        <h2 className={`text-sm font-bold ${isDark ? 'text-dark-300' : 'text-light-700'}`}>Top Movers</h2>
        {[1,2,3,4,5].map(i => (
          <div key={i} className={`animate-pulse rounded-xl p-4 ${isDark ? 'bg-dark-800/50' : 'bg-light-100/50'}`}>
            <div className={`h-3 rounded w-1/4 mb-2 ${isDark ? 'bg-dark-700' : 'bg-light-200'}`} />
            <div className={`h-3 rounded w-1/2 ${isDark ? 'bg-dark-700' : 'bg-light-200'}`} />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3 pb-4">
      <div className={`flex items-center justify-between mb-1 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
        <h2 className="text-sm font-bold">
          {activeNav === 'high' ? 'High Conviction Movers' :
           activeNav === 'medium' ? 'Medium Conviction Movers' :
           activeNav === 'low' ? 'Low Conviction Movers' :
           chainNames[activeNav] ? `${chainNames[activeNav]} Movers` :
           'Top Movers'}
        </h2>
        <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
          {movers.length} assets
        </span>
      </div>

      {movers.length === 0 ? (
        <div className={`p-6 text-center rounded-xl ${isDark ? 'bg-dark-800/50 text-dark-400' : 'bg-light-50 text-light-500'}`}>
          No movers data yet
        </div>
      ) : (
        <>
          <div className={`hidden md:grid grid-cols-7 gap-3 px-4 py-2 text-[10px] font-mono uppercase tracking-wider ${
            isDark ? 'text-dark-500' : 'text-light-400'
          }`}>
            <span>#</span>
            <span>Token</span>
            <span>Price</span>
            <span>24h</span>
            <span>Volume</span>
            <span>Signal</span>
            <span className="text-right">Conviction</span>
          </div>

          {movers.map((m, idx) => (
            <div key={m.token} className={`card-premium rounded-xl p-4 animate-slide-up stagger-${Math.min(idx + 1, 10)}`}>
              <div className="grid grid-cols-2 md:grid-cols-7 gap-3 items-center">
                <div className="flex items-center gap-2">
                  <span className={`w-6 h-6 flex items-center justify-center text-[10px] font-bold rounded ${
                    idx < 3
                      ? isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-50 text-brand-600'
                      : isDark ? 'bg-dark-700 text-dark-400' : 'bg-light-100 text-light-500'
                  }`}>#{m.rank}</span>
                </div>
                <div>
                  <p className="text-sm font-bold font-mono">${m.token}</p>
                  <p className={`text-[10px] ${isDark ? 'text-dark-400' : 'text-light-500'}`}>{m.name}</p>
                </div>
                <div>
                  <p className="text-sm font-mono">{m.price}</p>
                </div>
                <div>
                  <p className={`text-sm font-mono font-bold ${m.change24h >= 0 ? (isDark ? 'text-green-400' : 'text-green-600') : (isDark ? 'text-red-400' : 'text-red-600')}`}>
                    {m.change24h >= 0 ? '+' : ''}{m.change24h}%
                  </p>
                </div>
                <div>
                  <p className="text-sm font-mono">{m.volume}</p>
                </div>
                <div>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                    m.signal === 'Strong Buy'
                      ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-600'
                      : m.signal === 'Distribution'
                        ? isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-600'
                        : isDark ? 'bg-dark-700 text-dark-300' : 'bg-light-100 text-light-600'
                  }`}>{m.signal}</span>
                </div>
                <div className="text-right">
                  <div className="flex items-center justify-end gap-2">
                    <div className={`w-14 h-1.5 rounded-full overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
                      <div className="h-full rounded-full animate-progress"
                        style={{
                          width: `${m.conviction}%`,
                          backgroundColor: m.conviction >= 90 ? '#00d4aa' : m.conviction >= 75 ? '#f59e0b' : '#ef4444',
                        }}
                      ></div>
                    </div>
                    <span className="text-sm font-bold font-mono min-w-[36px]"
                      style={{ color: m.conviction >= 90 ? '#00d4aa' : m.conviction >= 75 ? '#f59e0b' : '#ef4444' }}>
                      {m.conviction}%
                    </span>
                  </div>
                  <p className={`text-[9px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                    {m.smartMoneyFlow} &middot; {m.walletCount} wallets
                  </p>
                </div>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  )
}