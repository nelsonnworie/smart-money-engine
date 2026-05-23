import { useTheme } from '../context/ThemeContext'
import { signalFeedData } from '../data/mockData'

const typeColors = {
  'Whale Accumulation': { bg: 'rgba(0,212,170,0.15)', text: '#00d4aa', label: 'Accumulation' },
  'Cluster Movement': { bg: 'rgba(139,92,246,0.15)', text: '#8b5cf6', label: 'Cluster' },
  'DEX Dumping': { bg: 'rgba(239,68,68,0.15)', text: '#ef4444', label: 'Dumping' },
  'New Position': { bg: 'rgba(251,191,36,0.15)', text: '#f59e0b', label: 'New Position' },
  'Bridge Activity': { bg: 'rgba(6,182,212,0.15)', text: '#06b6d4', label: 'Bridge' },
  'Liquidity Add': { bg: 'rgba(34,197,94,0.15)', text: '#22c55e', label: 'Liquidity Add' },
}

const chainColors = {
  Ethereum: '#627eea',
  Solana: '#14b8a6',
  Arbitrum: '#2d374b',
  Base: '#0052ff',
  Polygon: '#8247e5',
  Optimism: '#ff0420',
}

// Map signal type to actual trend direction
const typeTrends = {
  'Whale Accumulation': 'up',
  'New Position': 'up',
  'Liquidity Add': 'up',
  'Bridge Activity': 'up',
  'DEX Dumping': 'down',
  'Cluster Movement': 'down',
}

function getTrend(signal) {
  return typeTrends[signal.type] || 'neutral'
}

// Generate sparkline data matching the actual signal trend
function getSparklineData(signal) {
  const trend = getTrend(signal)
  const points = 12
  const data = []
  
  let val = 30 + Math.random() * 40
  for (let i = 0; i < points; i++) {
    if (trend === 'up') {
      val += 1.5 + Math.random() * 4
    } else if (trend === 'down') {
      val -= 1.5 + Math.random() * 4
    } else {
      val += (Math.random() - 0.5) * 6
    }
    val = Math.max(5, Math.min(95, val))
    data.push(Math.round(val * 10) / 10)
  }
  
  return data
}

// Pure line chart — no dots, no fill, no tails
function Sparkline({ data, color, width = 120, height = 24 }) {
  if (!data || data.length < 2) return null
  
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const stepX = width / (data.length - 1)
  
  const path = data.map((v, i) => {
    const x = i * stepX
    const y = height - ((v - min) / range) * height
    return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
      <path d={path} fill="none" stroke={color} strokeWidth="1.2" strokeLinecap="butt" strokeLinejoin="round" opacity="0.85" />
    </svg>
  )
}

export default function SignalFeed() {
  const { isDark } = useTheme()

  const getConvictionColor = (score) => {
    if (score >= 90) return isDark ? '#00d4aa' : '#059669'
    if (score >= 75) return '#f59e0b'
    return '#ef4444'
  }

  return (
    <div className="space-y-3">
      <div className={`flex items-center justify-between ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
        <h2 className="text-sm font-bold">Live Signal Feed</h2>
        <div className="flex items-center gap-1.5 text-[10px] font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse-glow"></span>
          <span className={isDark ? 'text-dark-400' : 'text-light-500'}>Real-time</span>
        </div>
      </div>

      <div className="space-y-2.5">
        {signalFeedData.map((signal, idx) => {
          const tc = typeColors[signal.type] || typeColors['Whale Accumulation']
          const convColor = getConvictionColor(signal.conviction)
          const sparkData = getSparklineData(signal)
          const trend = getTrend(signal)
          const sparkColor = trend === 'up' ? (isDark ? '#00d4aa' : '#059669') : (isDark ? '#ef4444' : '#dc2626')

          return (
            <div key={signal.id} className={`card-premium rounded-xl p-3.5 animate-slide-up stagger-${Math.min(idx + 1, 10)}`}>
              <div className="flex items-center gap-3">
                {/* Icon */}
                <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0"
                  style={{ backgroundColor: tc.bg, color: tc.text }}>
                  {signal.type.charAt(0)}
                </div>

                {/* Details */}
                <div className="flex-shrink-0" style={{ width: '180px' }}>
                  <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                    <span className="text-xs font-medium" style={{ color: tc.text }}>
                      {tc.label}
                    </span>
                    <span className={`text-[8px] px-1.5 py-0.5 rounded-full font-mono ${
                      isDark ? 'bg-dark-700 text-dark-400' : 'bg-light-100 text-light-500'
                    }`}>
                      {signal.id}
                    </span>
                    <span className="text-[8px] font-mono" style={{ color: chainColors[signal.chain] || '#94a3b8' }}>
                      {signal.chain}
                    </span>
                    {signal.label && (
                      <span className={`text-[8px] px-1.5 py-0.5 rounded-full font-mono ${
                        isDark ? 'bg-accent-500/10 text-accent-400' : 'bg-accent-50 text-accent-600'
                      }`}>
                        {signal.label}
                      </span>
                    )}
                  </div>

                  <h3 className="text-base font-bold leading-tight">{signal.token}</h3>
                  <p className={`text-[10px] mt-0.5 leading-tight truncate ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    {signal.description}
                  </p>
                  <div className="flex items-center gap-2 text-[9px] font-mono mt-0.5">
                    <span className={isDark ? 'text-dark-400' : 'text-light-500'}>
                      {signal.usdValue}
                    </span>
                    <span className={isDark ? 'text-dark-500' : 'text-light-400'}>{signal.timestamp}</span>
                  </div>
                </div>

                {/* Sparkline — fills the middle */}
                <div className="flex-1 flex items-center justify-center px-4">
                  <div className="w-full max-w-[160px]">
                    <Sparkline data={sparkData} color={sparkColor} width={140} height={24} />
                  </div>
                </div>

                {/* Conviction */}
                <div className="flex flex-col items-center justify-center flex-shrink-0 min-w-[56px]">
                  <div className="text-lg font-bold font-mono leading-none mb-1" style={{ color: convColor }}>
                    {signal.conviction}%
                  </div>
                  <div className={`w-12 h-1 rounded-full overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
                    <div className="h-full rounded-full animate-progress"
                      style={{ width: `${signal.conviction}%`, backgroundColor: convColor }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}