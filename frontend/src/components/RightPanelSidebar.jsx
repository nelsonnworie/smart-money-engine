import { useTheme } from '../context/ThemeContext'

export default function RightPanelSidebar({ data, collapsed }) {
  const { isDark } = useTheme()

  if (collapsed) return null

  return (
    <div className="space-y-3 px-3 pb-2">
      {/* Divider */}
      <div className={`pt-2 border-t ${isDark ? 'border-dark-700/30' : 'border-light-200'}`}>
        <p className={`text-[10px] font-semibold uppercase tracking-widest mb-2 px-1 ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
          Top Movers
        </p>
      </div>

      {data.topMovers.map((item, idx) => (
        <div key={item.token} className="animate-slide-up px-1" style={{ animationDelay: `${idx * 50}ms` }}>
          <div className="flex items-center justify-between mb-0.5">
            <div className="flex items-center gap-1.5 min-w-0">
              <span className={`text-[9px] font-mono w-4 ${isDark ? 'text-dark-400' : 'text-light-400'}`}>#{item.rank}</span>
              <span className="text-xs font-bold">${item.token}</span>
              <span className={`text-[8px] font-medium px-1 py-0.5 rounded ${
                item.signal === 'BUY'
                  ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-700'
                  : isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-700'
              }`}>{item.signal}</span>
            </div>
            <span className={`text-[10px] font-mono flex-shrink-0 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
              {item.wallets}w
            </span>
          </div>
          <div className={`h-1 rounded-full overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
            <div className="h-full rounded-full animate-progress"
              style={{
                width: `${item.barPercent}%`,
                background: 'linear-gradient(90deg, #00d4aa, #34d399)',
                animationDelay: `${idx * 100}ms`,
              }}
            ></div>
          </div>
          <div className="flex justify-between mt-0.5">
            <span className={`text-[8px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>{item.total}</span>
            <span className={`text-[8px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>{item.conviction}%</span>
          </div>
        </div>
      ))}

      {/* Telegram Bot Section */}
      <div className={`pt-2 border-t ${isDark ? 'border-dark-700/30' : 'border-light-200'}`}>
        <div className="flex items-center justify-between px-1 mb-2">
          <div className="flex items-center gap-1.5">
            <svg className="w-3 h-3 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
              <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
            </svg>
            <p className={`text-[10px] font-semibold uppercase tracking-wider ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
              Telegram Bot
            </p>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-1 h-1 rounded-full bg-green-500 animate-pulse-glow"></span>
            <span className={`text-[8px] font-medium ${isDark ? 'text-green-400' : 'text-green-600'}`}>online</span>
          </div>
        </div>

        <div className={`rounded-lg p-2 space-y-1.5 text-[10px] ${isDark ? 'bg-dark-750/50' : 'bg-light-100'}`}>
          <div className={`rounded p-1.5 ${isDark ? 'bg-dark-700' : 'bg-white'} max-w-[85%]`}>
            <p className={`font-medium ${isDark ? 'text-dark-200' : 'text-light-700'}`}>/signals</p>
          </div>
          <div className={`rounded p-1.5 ml-auto max-w-[90%] ${isDark ? 'bg-brand-500/10 border border-brand-400/10' : 'bg-brand-50 border border-brand-200'}`}>
            <p className={`font-medium ${isDark ? 'text-dark-100' : 'text-light-800'}`}>
              <span className="text-brand-500">ARB</span> BUY · 87% conviction
            </p>
            <p className={isDark ? 'text-dark-400' : 'text-light-500'}>3 wallets · $1.2M</p>
          </div>
        </div>
      </div>
    </div>
  )
}