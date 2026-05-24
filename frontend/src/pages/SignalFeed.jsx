import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'
import { signalFeedData } from '../data/mockData'

const API_BASE = 'https://smart-money-engine-production.up.railway.app'

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
  ethereum: '#627eea',
  solana: '#14b8a6',
  arbitrum: '#2d374b',
  base: '#0052ff',
  bnb: '#f0b90b',
}

function getTrend(signal) {
  if (signal.signal_type === 'BUY') return 'up'
  if (signal.signal_type === 'SELL') return 'down'
  return 'neutral'
}

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

function formatUsd(amount) {
  if (!amount) return '$0'
  if (amount >= 1000000) return `$${(amount / 1000000).toFixed(1)}M`
  if (amount >= 1000) return `$${(amount / 1000).toFixed(1)}K`
  return `$${amount.toFixed(0)}`
}

function formatTime(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins} min ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours} hour ago`
  return date.toLocaleDateString()
}

export default function SignalFeed() {
  const { isDark } = useTheme()
  const [liveSignals, setLiveSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [useMock, setUseMock] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function fetchSignals() {
      try {
        const res = await fetch(`${API_BASE}/signals`)
        if (!res.ok) throw new Error('API error')
        const data = await res.json()
        if (!cancelled && data && data.length > 0) {
          setLiveSignals(data.slice(0, 20))
          setUseMock(false)
        } else {
          if (!cancelled) setUseMock(true)
        }
      } catch (e) {
        console.warn('Failed to fetch live signals, using mock:', e)
        if (!cancelled) setUseMock(true)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    fetchSignals()
    return () => { cancelled = true }
  }, [])

  const signals = useMock ? signalFeedData : liveSignals

  const getConvictionColor = (score) => {
    if (score >= 90) return isDark ? '#00d4aa' : '#059669'
    if (score >= 75) return '#f59e0b'
    return '#ef4444'
  }

  if (loading) {
    return (
      <div className="space-y-3">
        <div className={`flex items-center justify-between ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
          <h2 className="text-sm font-bold">Live Signal Feed</h2>
        </div>
        {[1, 2, 3].map(i => (
          <div key={i} className={`animate-pulse rounded-xl p-3.5 ${isDark ? 'bg-dark-800/50' : 'bg-light-100/50'}`}>
            <div className="flex items-center gap-3">
              <div className={`w-8 h-8 rounded-lg ${isDark ? 'bg-dark-700' : 'bg-light-200'}`} />
              <div className="flex-1 space-y-2">
                <div className={`h-3 rounded w-1/3 ${isDark ? 'bg-dark-700' : 'bg-light-200'}`} />
                <div className={`h-3 rounded w-2/3 ${isDark ? 'bg-dark-700' : 'bg-light-200'}`} />
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className={`flex items-center justify-between ${isDark ? 'text-dark-300' : 'text-light-700'}`}>
        <h2 className="text-sm font-bold">Live Signal Feed</h2>
        <div className="flex items-center gap-1.5 text-[10px] font-mono">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse-glow"></span>
          <span className={isDark ? 'text-dark-400' : 'text-light-500'}>
            {useMock ? 'Demo' : 'Real-time'}
          </span>
        </div>
      </div>

      <div className="space-y-2.5">
        {signals.map((signal, idx) => {
          // Handle both mock format and API format
          const type = signal.type || (signal.signal_type === 'BUY' ? 'Whale Accumulation' : signal.signal_type === 'SELL' ? 'DEX Dumping' : signal.signal_type)
          const tc = typeColors[type] || typeColors['Whale Accumulation']
          const convScore = signal.conviction || signal.conviction_score || 70
          const convColor = getConvictionColor(convScore)
          const sparkData = getSparklineData(signal)
          const trend = getTrend(signal)
          const sparkColor = trend === 'up' ? (isDark ? '#00d4aa' : '#059669') : (isDark ? '#ef4444' : '#dc2626')
          const chain = signal.chain || 'ethereum'
          const token = signal.token || 'Unknown'
          const amount = signal.amount_usd || 0
          const desc = signal.description || `${signal.signal_type || type} ${token}`
          const label = signal.label || signal.wallet?.slice(0, 10) || ''

          return (
            <div key={signal.id || idx} className={`card-premium rounded-xl p-3.5 animate-slide-up stagger-${Math.min(idx + 1, 10)}`}>
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold flex-shrink-0"
                  style={{ backgroundColor: tc.bg, color: tc.text }}>
                  {(signal.type || signal.signal_type || '?').charAt(0)}
                </div>

                <div className="flex-shrink-0" style={{ width: '180px' }}>
                  <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                    <span className="text-xs font-medium" style={{ color: tc.text }}>
                      {tc.label || signal.signal_type}
                    </span>
                    {signal.id && (
                      <span className={`text-[8px] px-1.5 py-0.5 rounded-full font-mono ${
                        isDark ? 'bg-dark-700 text-dark-400' : 'bg-light-100 text-light-500'
                      }`}>
                        {typeof signal.id === 'number' ? `#${signal.id}` : signal.id}
                      </span>
                    )}
                    <span className="text-[8px] font-mono" style={{ color: chainColors[chain] || '#94a3b8' }}>
                      {chain.charAt(0).toUpperCase() + chain.slice(1)}
                    </span>
                  </div>

                  <h3 className="text-base font-bold leading-tight">
                    {token.startsWith('$') ? token : `$${token}`}
                  </h3>
                  <p className={`text-[10px] mt-0.5 leading-tight truncate ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    {desc}
                  </p>
                  <div className="flex items-center gap-2 text-[9px] font-mono mt-0.5">
                    <span className={isDark ? 'text-dark-400' : 'text-light-500'}>
                      {formatUsd(amount)}
                    </span>
                    <span className={isDark ? 'text-dark-500' : 'text-light-400'}>
                      {formatTime(signal.created_at)}
                    </span>
                  </div>
                </div>

                <div className="flex-1 flex items-center justify-center px-4">
                  <div className="w-full max-w-[160px]">
                    <Sparkline data={sparkData} color={sparkColor} width={140} height={24} />
                  </div>
                </div>

                <div className="flex flex-col items-center justify-center flex-shrink-0 min-w-[56px]">
                  <div className="text-lg font-bold font-mono leading-none mb-1" style={{ color: convColor }}>
                    {convScore}%
                  </div>
                  <div className={`w-12 h-1 rounded-full overflow-hidden ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}>
                    <div className="h-full rounded-full animate-progress"
                      style={{ width: `${convScore}%`, backgroundColor: convColor }}
                    />
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