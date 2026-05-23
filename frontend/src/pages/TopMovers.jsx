import { useTheme } from '../context/ThemeContext'
import { topMoversData, signalFeedData } from '../data/mockData'

export default function TopMovers({ activeNav }) {
  const { isDark } = useTheme()

  // Filter by conviction if nav is high/medium/low
  const filteredMovers = (() => {
    if (activeNav === 'high') return topMoversData.filter(m => m.conviction >= 80)
    if (activeNav === 'medium') return topMoversData.filter(m => m.conviction >= 50 && m.conviction < 80)
    if (activeNav === 'low') return topMoversData.filter(m => m.conviction < 50)
    // Filter by chain
    const chainMap = { eth: 'LINK', sol: 'SOL', arb: 'ARB', base: 'AERO', matic: 'BNB' }
    if (chainMap[activeNav]) {
      return topMoversData.filter(m => m.token === chainMap[activeNav] || signalFeedData.some(s => s.chain.toLowerCase().startsWith(activeNav.slice(0, 3)) && s.token === m.token))
    }
    return topMoversData
  })()

  const sorted = [...filteredMovers].sort((a, b) => b.conviction - a.conviction)

  return (
    <div className="space-y-3 pb-4">
      <div className={`flex items-center justify-between mb-1 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
        <h2 className="text-sm font-bold">
          {activeNav === 'high' ? 'High Conviction Movers' :
           activeNav === 'medium' ? 'Medium Conviction Movers' :
           activeNav === 'low' ? 'Low Conviction Movers' :
           'Top Movers'}
        </h2>
        <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
          {sorted.length} assets
        </span>
      </div>

      {/* Table Header */}
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

      {sorted.map((m, idx) => (
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
                m.signal.includes('Buy') || m.signal.includes('Accumulate')
                  ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-600'
                  : m.signal.includes('Distribute')
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
    </div>
  )
}