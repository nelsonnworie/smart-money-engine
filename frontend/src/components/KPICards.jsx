import { useTheme } from '../context/ThemeContext'

const KpiIcon = ({ type }) => {
  const props = { className: "w-4 h-4", viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: "1.5", strokeLinecap: "round", strokeLinejoin: "round" }
  switch (type) {
    case 'signals':
      return <svg {...props}><path d="M12 20V10" /><path d="M18 20V4" /><path d="M6 20v-4" /></svg>
    case 'clusters':
      return <svg {...props}><circle cx="9" cy="7" r="3" /><circle cx="17" cy="12" r="3" /><circle cx="9" cy="17" r="3" /><path d="M9 10v4" /><path d="M12 12h2" /></svg>
    case 'chains':
      return <svg {...props}><circle cx="12" cy="12" r="3" /><circle cx="12" cy="12" r="8" /><path d="M2 12h20" /><path d="M12 2v20" /></svg>
    case 'conviction':
      return <svg {...props}><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2z" /></svg>
    default:
      return null
  }
}

export default function KPICards({ data }) {
  const { isDark } = useTheme()

  const cards = [
    {
      id: 'signals', label: 'Total Signals',
      value: data.totalSignals.toLocaleString(),
      change: data.totalSignalsChange, type: 'signals',
      color: '#00d4aa',
      iconBg: 'rgba(0,212,170,0.08)',
      iconBorder: 'rgba(0,212,170,0.12)',
      bars: [40, 55, 45, 70, 60, 100],
    },
    {
      id: 'clusters', label: 'Active Clusters',
      value: data.activeClusters,
      change: data.activeClustersChange, type: 'clusters',
      color: '#8b5cf6',
      iconBg: 'rgba(139,92,246,0.08)',
      iconBorder: 'rgba(139,92,246,0.12)',
      bars: [50, 65, 55, 80, 70, 90],
    },
    {
      id: 'chains', label: 'Chains Detected',
      value: data.chainsDetected,
      change: data.chainsDetectedChange, type: 'chains',
      color: '#3b82f6',
      iconBg: 'rgba(59,130,246,0.08)',
      iconBorder: 'rgba(59,130,246,0.12)',
      bars: [60, 60, 70, 70, 80, 90],
    },
    {
      id: 'conviction', label: 'High Conviction',
      value: data.highConviction,
      change: data.highConvictionChange, type: 'conviction',
      color: '#f59e0b',
      iconBg: 'rgba(245,158,11,0.08)',
      iconBorder: 'rgba(245,158,11,0.12)',
      bars: [80, 90, 75, 85, 65, 70],
    },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
      {cards.map((card, idx) => (
        <div
          key={card.id}
          className={`card-premium relative rounded-xl p-3.5 overflow-hidden animate-slide-up stagger-${idx + 1}`}
        >
          {/* Top shimmer line */}
          <div
            className="absolute top-0 left-0 right-0 h-px"
            style={{ background: `linear-gradient(90deg, transparent, ${card.color}66, transparent)` }}
          />

          <div className="flex items-start justify-between mb-2">
            <div
              className="p-1.5 rounded-lg"
              style={{
                background: card.iconBg,
                border: `1px solid ${card.iconBorder}`,
                color: card.color,
              }}
            >
              <KpiIcon type={card.type} />
            </div>

            <div className={`flex items-center gap-0.5 text-[10px] font-semibold px-1.5 py-0.5 rounded-full ${
              card.change >= 0
                ? isDark ? 'text-green-400 bg-green-500/10' : 'text-green-700 bg-green-50'
                : isDark ? 'text-red-400 bg-red-500/10' : 'text-red-700 bg-red-50'
            }`}>
              <svg
                className={`w-2.5 h-2.5 ${card.change < 0 ? 'rotate-180' : ''}`}
                viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
              >
                <path d="M18 15l-6-6-6 6" />
              </svg>
              {Math.abs(card.change)}%
            </div>
          </div>

          <p className="text-xl font-bold font-mono tracking-tight animate-count-up"
            style={{ color: isDark ? '#f1f5f9' : '#0f172a' }}>
            {card.value}
          </p>
          <p className={`text-[11px] mt-0.5 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
            {card.label}
          </p>

          {/* Sparkline bars */}
          <div className="flex items-end gap-0.5 mt-3" style={{ height: '20px' }}>
            {card.bars.map((h, i) => (
              <div
                key={i}
                className="flex-1 rounded-sm"
                style={{
                  height: `${h}%`,
                  background: i === card.bars.length - 1
                    ? card.color
                    : `${card.color}28`,
                  transition: 'height 0.3s ease',
                }}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}