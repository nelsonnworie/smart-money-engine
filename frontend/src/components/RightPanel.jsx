import { useTheme } from '../context/ThemeContext'

function TopMoversWidget({ data }) {
  const { isDark } = useTheme()
  return (
    <div className="card-premium rounded-xl p-4 animate-slide-up stagger-3">
      <div className="flex items-center justify-between mb-3">
        <h3 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
          Top Movers Today
        </h3>
        <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-mono ${isDark ? 'bg-dark-700 text-dark-400' : 'bg-light-100 text-light-500'}`}>
          By Wallet
        </span>
      </div>
      <div className="space-y-2.5">
        {data.topMovers.map((item, idx) => (
          <div key={item.token} className="animate-slide-up" style={{ animationDelay: `${idx * 50 + 50}ms` }}>
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-2">
                <span className={`w-5 h-5 flex items-center justify-center text-[9px] font-bold rounded ${
                  idx < 3
                    ? isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-50 text-brand-600'
                    : isDark ? 'bg-dark-700 text-dark-400' : 'bg-light-100 text-light-500'
                }`}>#{item.rank}</span>
                <span className="text-sm font-bold">${item.token}</span>
                <span className={`text-[10px] font-medium px-1.5 py-0.5 rounded ${
                  item.signal === 'BUY'
                    ? isDark ? 'bg-green-500/10 text-green-400' : 'bg-green-50 text-green-700'
                    : isDark ? 'bg-red-500/10 text-red-400' : 'bg-red-50 text-red-700'
                }`}>{item.signal}</span>
              </div>
              <span className={`text-xs font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                {item.wallets} wallet{item.wallets > 1 ? 's' : ''}
              </span>
            </div>
            {/* Progress bar */}
            <div className={`h-1.5 rounded-full overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
              <div
                className="h-full rounded-full animate-progress"
                style={{
                  width: `${item.barPercent}%`,
                  background: 'linear-gradient(90deg, #00d4aa, #34d399)',
                  animationDelay: `${idx * 100}ms`,
                }}
              ></div>
            </div>
            <div className="flex justify-between mt-0.5">
              <span className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                {item.total}
              </span>
              <span className={`text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                {item.conviction}% conviction
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function TelegramBotWidget({ data }) {
  const { isDark } = useTheme()
  return (
    <div className="card-premium rounded-xl p-4 animate-slide-up stagger-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
            <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
          </svg>
          <h3 className={`text-xs font-bold uppercase tracking-wider ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
            Telegram Bot
          </h3>
        </div>
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse-glow"></span>
          <span className={`text-[10px] font-medium ${isDark ? 'text-green-400' : 'text-green-600'}`}>online</span>
        </div>
      </div>

      <p className={`text-[10px] font-mono mb-3 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
        {data.telegramBot.username}
      </p>

      {/* Chat simulation */}
      <div className={`rounded-lg p-3 space-y-2 text-xs ${isDark ? 'bg-dark-750/50' : 'bg-light-100'}`}>
        <div className={`rounded-lg p-2 ${isDark ? 'bg-dark-700' : 'bg-white'} max-w-[90%]`}>
          <span className={`text-[10px] ${isDark ? 'text-dark-500' : 'text-light-400'}`}>You</span>
          <p className={`font-medium ${isDark ? 'text-dark-200' : 'text-light-700'}`}>/start</p>
        </div>
        <div className={`rounded-lg p-2 ml-auto max-w-[95%] ${isDark ? 'bg-brand-500/10 border border-brand-400/10' : 'bg-brand-50 border border-brand-200'}`}>
          <span className="text-[10px] text-brand-500">Bot</span>
          <p className={`font-medium ${isDark ? 'text-dark-100' : 'text-light-800'}`}>
            Subscribed! You'll receive HIGH conviction alerts (70+) automatically.
          </p>
        </div>
        <div className={`rounded-lg p-2 ${isDark ? 'bg-dark-700' : 'bg-white'} max-w-[90%]`}>
          <span className={`text-[10px] ${isDark ? 'text-dark-500' : 'text-light-400'}`}>You</span>
          <p className={`font-medium ${isDark ? 'text-dark-200' : 'text-light-700'}`}>/signals</p>
        </div>
      </div>

      {/* Cluster signal example */}
      <div className={`mt-3 rounded-lg p-3 animate-slide-up stagger-5 ${isDark ? 'bg-dark-750/50 border border-dark-600/20' : 'bg-light-50 border border-light-200'}`}>
        <div className="flex items-center justify-between mb-1">
          <div className="flex items-center gap-2">
            <span className={`px-1.5 py-0.5 text-[9px] font-bold rounded ${
              data.telegramBot.recentSignals[0].action === 'BUY'
                ? 'bg-green-500/15 text-green-400'
                : 'bg-red-500/15 text-red-400'
            }`}>{data.telegramBot.recentSignals[0].action}</span>
            <span className="text-sm font-bold">${data.telegramBot.recentSignals[0].token}</span>
            {data.telegramBot.recentSignals[0].cluster && (
              <span className={`text-[9px] px-1 py-0.5 rounded-full ${
                isDark ? 'bg-accent-500/10 text-accent-400' : 'bg-accent-50 text-accent-600'
              }`}>CLUSTER</span>
            )}
          </div>
          <span className={`text-xs font-mono font-bold ${
            data.telegramBot.recentSignals[0].conviction >= 80
              ? isDark ? 'text-brand-400' : 'text-brand-600'
              : isDark ? 'text-dark-400' : 'text-light-500'
          }`}>{data.telegramBot.recentSignals[0].conviction}%</span>
        </div>
        <p className={`text-[10px] ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
          {data.telegramBot.recentSignals[0].wallets} wallets · {data.telegramBot.recentSignals[0].total} · {data.telegramBot.recentSignals[0].chain}
        </p>
      </div>
    </div>
  )
}

export default function RightPanel({ data }) {
  return (
    <div className="space-y-4">
      <TopMoversWidget data={data} />
      <TelegramBotWidget data={data} />
    </div>
  )
}