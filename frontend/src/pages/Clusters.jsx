import { useTheme } from '../context/ThemeContext'
import { clusterData } from '../data/mockData'

export default function Clusters() {
  const { isDark } = useTheme()

  return (
    <div className="space-y-3">
      <div className={`flex items-center justify-between ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
        <h2 className="text-sm font-bold">Smart Money Clusters</h2>
        <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
          {clusterData.length} active clusters
        </span>
      </div>

      <div className="space-y-2.5">
        {clusterData.map((cluster, idx) => (
          <div key={cluster.id} className={`card-premium rounded-xl p-3.5 animate-slide-up stagger-${Math.min(idx + 1, 10)}`}>
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0"
                style={{ backgroundColor: `${cluster.color}15`, color: cluster.color }}>
                {cluster.name.charAt(0)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <h3 className="text-sm font-bold">{cluster.name}</h3>
                  <span className={`text-[8px] px-1.5 py-0.5 rounded-full font-mono ${
                    isDark ? 'bg-dark-700 text-dark-400' : 'bg-light-100 text-light-500'
                  }`}>{cluster.id}</span>
                  <span className={`text-[8px] px-1.5 py-0.5 rounded-full font-medium`}
                    style={{ backgroundColor: `${cluster.color}15`, color: cluster.color }}>
                    {cluster.signal}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
                  <div>
                    <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Wallets</p>
                    <p className="text-sm font-bold font-mono">{cluster.wallets}</p>
                  </div>
                  <div>
                    <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Total Value</p>
                    <p className="text-sm font-bold font-mono">{cluster.totalValue}</p>
                  </div>
                  <div>
                    <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>Avg Conviction</p>
                    <p className={`text-sm font-bold font-mono ${cluster.avgConviction >= 80 ? (isDark ? 'text-brand-400' : 'text-brand-600') : (isDark ? 'text-dark-300' : 'text-light-700')}`}>
                      {cluster.avgConviction}%
                    </p>
                  </div>
                  <div>
                    <p className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>24h Change</p>
                    <p className={`text-sm font-bold font-mono ${cluster.change24h >= 0 ? (isDark ? 'text-green-400' : 'text-green-600') : (isDark ? 'text-red-400' : 'text-red-600')}`}>
                      {cluster.change24h >= 0 ? '+' : ''}{cluster.change24h}%
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-2 flex-wrap">
                  <span className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                    Chains: {cluster.activeChains.join(', ')}
                  </span>
                  <span className={`text-[10px] font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    &middot; Volume: {cluster.volume24h}
                  </span>
                  <span className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                    &middot; {cluster.lastActive}
                  </span>
                </div>

                <div className="flex gap-1.5 mt-2 flex-wrap">
                  {cluster.topTokens.map(t => (
                    <span key={t} className={`text-[8px] px-2 py-0.5 rounded-full font-mono ${
                      isDark ? 'bg-dark-700 text-dark-300' : 'bg-light-100 text-light-600'
                    }`}>{t}</span>
                  ))}
                </div>
              </div>

              <div className="flex flex-col items-center justify-center flex-shrink-0 min-w-[44px] ml-1">
                <div className="text-sm font-bold font-mono leading-none mb-1" style={{ color: cluster.color }}>{cluster.avgConviction}%</div>
                <span className={`text-[8px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>avg</span>
                <div className={`w-9 h-1 rounded-full mt-1 overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
                  <div className="h-full rounded-full animate-progress"
                    style={{ width: `${cluster.avgConviction}%`, backgroundColor: cluster.color }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}