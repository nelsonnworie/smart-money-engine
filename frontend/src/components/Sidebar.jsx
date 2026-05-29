import { useTheme } from '../context/ThemeContext'
import RightPanel from './RightPanel'

const mainNav = [
  { id: 'signals', label: 'Signal Feed', icon: 'S' },
  { id: 'explorer', label: 'Wallet Explorer', icon: 'W' },
  { id: 'clusters', label: 'Clusters', icon: 'C' },
  { id: 'movers', label: 'Top Movers', icon: 'M' },
]

const convictions = [
  { id: 'high', label: 'High', range: '80-100%', color: '#00d4aa' },
  { id: 'medium', label: 'Medium', range: '50-79%', color: '#f59e0b' },
  { id: 'low', label: 'Low', range: '0-49%', color: '#ef4444' },
]

export default function Sidebar({ activeNav, setActiveNav, collapsed, setCollapsed, chainData, rightPanelData }) {
  const { isDark } = useTheme()

  const NavButton = ({ id, label, icon, isActive }) => (
    <button
      onClick={() => setActiveNav(id)}
      className={`w-full flex items-center gap-3 px-6 py-2.5 text-base font-medium transition-all duration-200 cursor-pointer group ${
        isActive
          ? isDark
            ? 'bg-brand-500/10 text-brand-400 border border-brand-400/20 shadow-[0_0_12px_rgba(0,212,170,0.06)]'
            : 'bg-brand-50 text-brand-700 border border-brand-200'
          : isDark
            ? 'text-dark-300 hover:text-dark-100 hover:bg-dark-800/50 hover:border-dark-600/30 border border-transparent'
            : 'text-light-600 hover:text-light-800 hover:bg-light-100 border border-transparent'
      }`}
    >
      <span className={`w-6 h-6 flex items-center justify-center text-xs font-bold rounded-md flex-shrink-0 ${
        isActive
          ? isDark ? 'bg-brand-500/20 text-brand-400' : 'bg-brand-100 text-brand-700'
          : isDark ? 'bg-dark-800 text-dark-400' : 'bg-light-200 text-light-500'
      }`}>
        {icon}
      </span>
      {!collapsed && (
        <>
          <span className="truncate">{label}</span>
          {isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-brand-500 animate-pulse-glow flex-shrink-0"></span>}
        </>
      )}
    </button>
  )

  const sectionTitle = (text) => (
    !collapsed && (
      <p className={`text-[10px] font-semibold uppercase tracking-widest mb-2 px-6 ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
        {text}
      </p>
    )
  )

  return (
    <aside className={`h-full flex-shrink-0 flex flex-col border-r z-40 transition-all duration-300 ${
      collapsed ? 'w-16' : 'w-70'
    } ${isDark ? 'bg-dark-900/90 border-dark-700/30' : 'bg-white/90 border-light-200'}`}>
      {/* Collapse toggle */}
      <div className="flex-1 overflow-y-auto p-3 space-y-5">
  {/* Block 1: Main — with collapse toggle in the section header */}
  <div>
    <div className="flex items-center justify-between px-6 mb-2">
      <p className={`text-[10px] font-semibold uppercase tracking-widest ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
        Navigation
      </p>
      {/* Collapse toggle INSIDE the Navigation header */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className={`p-1 rounded-md transition-colors cursor-pointer ${
          isDark ? 'hover:bg-dark-700 text-dark-400' : 'hover:bg-light-100 text-light-500'
        }`}
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      >
        <svg className="w-3.5 h-3.5 transition-transform duration-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          {collapsed
            ? <path d="M13 17l5-5-5-5M6 17l5-5-5-5" />
            : <path d="M11 17l-5-5 5-5M18 17l-5-5 5-5" />
          }
        </svg>
      </button>
    </div>
    <div className="space-y-1">
      {mainNav.map(item => (
        <NavButton key={item.id} {...item} isActive={activeNav === item.id} />
      ))}
    </div>
  </div>

        {/* Block 2: Chains */}
        <div>
          {sectionTitle('Chains')}
          <div className="space-y-1">
            {chainData.map(chain => {
             const chainNavId = { 'Ethereum': 'eth', 'Solana': 'sol', 'Arbitrum': 'arb', 'Base': 'base', 'BNB Chain': 'bnb', 'Polygon': 'matic' }[chain.name] || chain.name.toLowerCase()
              const isActive = activeNav === chainNavId
              return (
                <button
                  key={chain.name}
                  onClick={() => setActiveNav(chainNavId)}
                  className={`w-full flex items-center gap-3 px-6 py-2 text-base font-medium transition-all duration-200 cursor-pointer ${
                    isActive
                      ? isDark
                        ? 'bg-brand-500/10 text-brand-400 border border-brand-400/20'
                        : 'bg-brand-50 text-brand-700 border border-brand-200'
                      : isDark
                        ? 'text-dark-300 hover:text-dark-100 hover:bg-dark-800/50'
                        : 'text-light-600 hover:text-light-800 hover:bg-light-100'
                  }`}
                >
                  <span className="w-6 h-6 flex items-center justify-center text-xs font-bold rounded-md flex-shrink-0"
                    style={{ backgroundColor: `${chain.color}15`, color: chain.color }}>
                    {chain.name.charAt(0)}
                  </span>
                  {!collapsed && (
                    <>
                      <span className="truncate">{chain.name}</span>
                      <span className={`ml-auto text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                        {chain.signals24h}
                      </span>
                    </>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Block 3: Convictions */}
        <div>
          {sectionTitle('Conviction')}
          <div className="space-y-1">
            {convictions.map(c => {
              const isActive = activeNav === c.id
              return (
                <button
                  key={c.id}
                  onClick={() => setActiveNav(c.id)}
                  className={`w-full flex items-center gap-3 px-6 py-2 text-base font-medium transition-all duration-200 cursor-pointer ${
                    isActive
                      ? isDark
                        ? 'bg-brand-500/10 text-brand-400 border border-brand-400/20'
                        : 'bg-brand-50 text-brand-700 border border-brand-200'
                      : isDark
                        ? 'text-dark-300 hover:text-dark-100 hover:bg-dark-800/50'
                        : 'text-light-600 hover:text-light-800 hover:bg-light-100'
                  }`}
                >
                  <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: c.color }}></span>
                  {!collapsed && (
                    <>
                      <span className="truncate">{c.label}</span>
                      <span className={`ml-auto text-[10px] font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                        {c.range}
                      </span>
                    </>
                  )}
                </button>
              )
            })}
          </div>
        </div>

        {/* Telegram Bot */}
        {!collapsed && (
          <div className={`pt-3 border-t ${isDark ? 'border-dark-700/30' : 'border-light-200'}`}>
            <a href="https://t.me/SmartMoneySignalBot" target="_blank" rel="noopener noreferrer"
              className={`flex items-center gap-3 px-6 py-2.5 text-base font-medium transition-all duration-200 group cursor-pointer ${
                isDark ? 'text-dark-300 hover:text-brand-400 hover:bg-brand-500/5' : 'text-light-600 hover:text-brand-600 hover:bg-brand-50'
              }`}>
              <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
              <span className="truncate">Telegram Bot</span>
              <span className="ml-auto">
                <span className={`text-[9px] px-1.5 py-0.5 rounded-full font-semibold ${
                  isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-50 text-brand-600'
                }`}>LIVE</span>
              </span>
            </a>
          </div>
        )}

        {/* Right Panel */}
        {!collapsed && rightPanelData && (
          <div className="pt-3">
            <RightPanel data={rightPanelData} />
          </div>
        )}
      </div>
    </aside>
  )
}