import { useState } from 'react'
import { useTheme } from '../context/ThemeContext'
import Sidebar from './Sidebar'
import SearchBar from './SearchBar'
import KPICards from './KPICards'
import { kpiData, walletData } from '../data/mockData'

export default function Layout({ children, activeNav, setActiveNav }) {
  const { isDark, toggleTheme } = useTheme()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(true)

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        activeNav={activeNav}
        setActiveNav={setActiveNav}
        collapsed={sidebarCollapsed}
        setCollapsed={setSidebarCollapsed}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <header className={`flex items-center gap-4 px-4 lg:px-6 h-16 border-b flex-shrink-0 ${
          isDark ? 'bg-dark-850 border-dark-700/50' : 'bg-white border-light-300'
        }`}>
          <button
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            className={`lg:hidden p-2 rounded-lg transition-colors ${
              isDark ? 'hover:bg-dark-800 text-dark-300' : 'hover:bg-light-200 text-light-600'
            }`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={sidebarCollapsed ? 'M4 6h16M4 12h16M4 18h16' : 'M6 18L18 6M6 6l12 12'} />
            </svg>
          </button>

          <div className="flex-1 max-w-2xl">
            <SearchBar
              onSearch={(q) => console.log('Searching:', q)}
              results={walletData['0x7a3fb9e2']}
              loading={false}
            />
          </div>

          <button
            onClick={toggleTheme}
            className={`p-2.5 rounded-xl text-sm transition-all duration-200 flex-shrink-0 ${
              isDark
                ? 'bg-dark-800 text-dark-300 hover:text-dark-100 border border-dark-700/50'
                : 'bg-light-200 text-light-600 hover:text-light-800 border border-light-300'
            }`}
            title="Toggle theme"
          >
            {isDark ? '☀️' : '🌙'}
          </button>
        </header>

        {/* Scrollable content only — no footer here */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="mb-6">
              <KPICards data={kpiData} />
            </div>
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}