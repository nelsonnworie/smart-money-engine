import { useState, useEffect } from 'react'
import { ThemeProvider, useTheme } from './context/ThemeContext'
import Sidebar from './components/Sidebar'
import KPICards from './components/KPICards'
import SearchBar from './components/SearchBar'
import Footer from './components/Footer'
import SignalFeed from './pages/SignalFeed'
import Clusters from './pages/Clusters'
import WalletExplorer from './pages/WalletExplorer'
import TopMovers from './pages/TopMovers'
import { kpiData, rightPanelData, chainData } from './data/mockData'

function AppContent() {
  const { isDark, toggleTheme } = useTheme()
  const [activeNav, setActiveNav] = useState('signals')
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [timeLeft, setTimeLeft] = useState(30)
  const [isRefreshing, setIsRefreshing] = useState(false)

  useEffect(() => {
    const interval = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          setIsRefreshing(true)
          setTimeout(() => setIsRefreshing(false), 1000)
          return 30
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  const renderPage = () => {
    switch (activeNav) {
      case 'signals': return <SignalFeed />
      case 'clusters': return <Clusters />
      case 'explorer': return <WalletExplorer />
      case 'movers':
      case 'high':
      case 'medium':
      case 'low':
      case 'eth':
      case 'sol':
      case 'arb':
      case 'base':
      case 'bnb':
      case 'matic':
        return <TopMovers activeNav={activeNav} />
      default: return <SignalFeed />
    }
  }

  return (
    <div className="flex flex-col min-h-screen">

      {/* ── HEADER ── */}
      <header className={`sticky top-0 z-40 flex items-center gap-2 sm:gap-4 px-3 sm:px-6 h-14 border-b transition-colors duration-300 glass ${
        isDark ? 'border-dark-700/40 bg-dark-950/80' : 'border-light-200 bg-white/90'
      }`}>
        
        {/* Hamburger for mobile */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden relative w-8 h-8 flex items-center justify-center rounded-lg transition-all duration-300 cursor-pointer"
          aria-label="Toggle menu"
        >
          <div className="flex flex-col gap-1">
            <span className={`block w-5 h-0.5 rounded transition-all duration-300 ${
              mobileMenuOpen ? 'rotate-45 translate-y-1.5' : ''
            } ${isDark ? 'bg-dark-300' : 'bg-light-600'}`} />
            <span className={`block w-5 h-0.5 rounded transition-all duration-300 ${
              mobileMenuOpen ? 'opacity-0' : ''
            } ${isDark ? 'bg-dark-300' : 'bg-light-600'}`} />
            <span className={`block w-5 h-0.5 rounded transition-all duration-300 ${
              mobileMenuOpen ? '-rotate-45 -translate-y-1.5' : ''
            } ${isDark ? 'bg-dark-300' : 'bg-light-600'}`} />
          </div>
        </button>

        <div className="flex items-center gap-3 min-w-fit">
          <div className="w-8 h-8 rounded-lg overflow-hidden flex-shrink-0">
            <img src="/vite.svg" alt="SME" className="w-full h-full object-cover" />
          </div>
          <div className="hidden sm:block">
            <h1 className="text-sm font-bold tracking-tight leading-tight">
              <span style={{ color: '#00d4aa' }}>SMART MONEY</span>
              <span style={{ color: '#f59e0b' }}> ENGINE</span>
            </h1>
            <p className={`text-[10px] font-medium tracking-wider capitalize leading-tight ${
              isDark ? 'text-dark-400' : 'text-light-500'
            }`}>
              Cross-Chain Signal Platform
            </p>
          </div>
        </div>

        <div className="flex-1 flex justify-center max-w-lg mx-auto min-w-0">
          <SearchBar />
        </div>

        <div className="flex items-center gap-2 sm:gap-3 min-w-fit">
          <div className="hidden md:flex items-center gap-2 text-xs">
            <div className={`w-1.5 h-1.5 rounded-full ${
              isRefreshing
                ? 'bg-brand-400 animate-pulse-glow'
                : isDark ? 'bg-brand-500' : 'bg-brand-600'
            }`} />
            <span className={isDark ? 'text-dark-400' : 'text-light-500'}>
              {isRefreshing ? 'Refreshing...' : 'Live · ' + timeLeft + 's'}
            </span>
          </div>

          <button
            onClick={toggleTheme}
            className={`relative w-9 h-9 flex items-center justify-center rounded-lg transition-all duration-300 cursor-pointer ${
              isDark
                ? 'bg-dark-800 border border-dark-600/30 hover:border-brand-400/30 hover:shadow-[0_0_15px_rgba(0,212,170,0.1)]'
                : 'bg-light-100 border border-light-200 hover:border-brand-400/50 hover:shadow-sm'
            }`}
            title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            <svg viewBox="0 0 24 24" className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {isDark ? (
                <>
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" className="text-brand-400 fill-brand-400/10" />
                  <circle cx="12" cy="12" r="1.5" className="fill-brand-400/30" />
                </>
              ) : (
                <>
                  <circle cx="12" cy="12" r="5" className="text-amber-500" />
                  <line x1="12" y1="1" x2="12" y2="3" className="text-amber-400" />
                  <line x1="12" y1="21" x2="12" y2="23" className="text-amber-400" />
                  <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" className="text-amber-400" />
                  <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" className="text-amber-400" />
                  <line x1="1" y1="12" x2="3" y2="12" className="text-amber-400" />
                  <line x1="21" y1="12" x2="23" y2="12" className="text-amber-400" />
                  <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" className="text-amber-400" />
                  <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" className="text-amber-400" />
                </>
              )}
            </svg>
          </button>
        </div>
      </header>

      {/* ── BELOW HEADER ── */}
      <div className="flex flex-1 min-h-0 relative">

        {/* MOBILE OVERLAY */}
        {mobileMenuOpen && (
          <div
            className="md:hidden fixed inset-0 z-30 bg-black/50"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}

        {/* Sidebar — hidden on mobile unless toggled */}
        <div className={`
          sticky top-14 h-[calc(100vh-3.5rem)] flex-shrink-0 z-40
          transition-all duration-300
          hidden md:block
          ${mobileMenuOpen ? '!block fixed left-0 top-14 bottom-0 w-64 shadow-2xl' : ''}
        `}>
          <Sidebar
            activeNav={activeNav}
            setActiveNav={(nav) => { setActiveNav(nav); setMobileMenuOpen(false); }}
            collapsed={sidebarCollapsed}
            setCollapsed={setSidebarCollapsed}
            chainData={chainData}
            rightPanelData={rightPanelData}
          />
        </div>

        {/* Main content + footer */}
        <div className="flex flex-col flex-1 min-w-0 overflow-y-auto">

          {/* KPI cards */}
          <div className="px-3 sm:px-6 pt-4 sm:pt-5 pb-2 sm:pb-3">
            <KPICards data={kpiData} />
          </div>

          {/* Page content */}
          <div className="px-3 sm:px-6 pb-6 flex-1">
            {renderPage()}
          </div>

          <Footer />

        </div>

      </div>
    </div>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  )
}