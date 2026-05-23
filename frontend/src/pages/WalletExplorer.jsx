import { useTheme } from '../context/ThemeContext'
import { walletData } from '../data/mockData'

export default function WalletExplorer() {
  const { isDark } = useTheme()
  const w = walletData.default

  return (
    <div className="space-y-3 pb-4">
      {/* Wallet Header */}
      <div className={`card-premium rounded-xl p-4 animate-slide-up stagger-1`}>
        <div className="flex items-start gap-4">
          <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-lg font-bold flex-shrink-0 ${
            isDark ? 'bg-brand-500/15 text-brand-400 border border-brand-400/20' : 'bg-brand-50 text-brand-600 border border-brand-200'
          }`}>
            W
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-lg font-bold">{w.ens || 'Wallet'}</h2>
              <span className={`text-xs font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>{w.address}</span>
              {w.labels.map((l, i) => (
                <span key={i} className={`text-[9px] px-1.5 py-0.5 rounded-full font-mono ${
                  isDark ? 'bg-accent-500/10 text-accent-400' : 'bg-accent-50 text-accent-600'
                }`}>{l}</span>
              ))}
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Total Holdings</p>
                <p className="text-xl font-bold font-mono text-brand-500">{w.totalHolding}</p>
              </div>
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>PnL</p>
                <p className={`text-xl font-bold font-mono ${isDark ? 'text-green-400' : 'text-green-600'}`}>{w.profitLoss}</p>
              </div>
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Transactions</p>
                <p className="text-xl font-bold font-mono">{w.totalTransactions.toLocaleString()}</p>
              </div>
              <div>
                <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Last Active</p>
                <p className="text-xl font-bold font-mono">{w.lastActive}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio */}
      <div className={`card-premium rounded-xl p-4 animate-slide-up stagger-2`}>
        <h3 className={`text-xs font-bold uppercase tracking-wider mb-3 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>Portfolio</h3>
        <div className="space-y-2">
          {w.topHoldings.map((h, idx) => (
            <div key={h.token} className="animate-slide-up" style={{ animationDelay: `${idx * 80 + 200}ms` }}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold">{h.token}</span>
                  <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>{h.amount}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold font-mono">{h.value}</span>
                  <span className={`text-[10px] font-mono ${h.change24h >= 0 ? (isDark ? 'text-green-400' : 'text-green-600') : (isDark ? 'text-red-400' : 'text-red-600')}`}>
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
                ></div>
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

      {/* Activity */}
      <div className={`card-premium rounded-xl p-4 animate-slide-up stagger-3`}>
        <h3 className={`text-xs font-bold uppercase tracking-wider mb-3 ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
          Recent Activity
        </h3>
        <div className="space-y-2">
          {w.recentActivity.map((act, idx) => (
            <div key={idx} className={`flex items-center gap-3 p-2 rounded-lg ${isDark ? 'hover:bg-dark-700/50' : 'hover:bg-light-100'} transition-colors animate-fade-in`}
              style={{ animationDelay: `${idx * 100}ms` }}>
              <div className={`w-7 h-7 rounded-md flex items-center justify-center text-[9px] font-bold flex-shrink-0 ${
                act.type === 'Buy'
                  ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-600'
                  : act.type === 'Sell'
                    ? isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-600'
                    : isDark ? 'bg-accent-500/15 text-accent-400' : 'bg-accent-50 text-accent-600'
              }`}>{act.type === 'Buy' ? 'B' : act.type === 'Sell' ? 'S' : 'Br'}</div>
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
    </div>
  )
}