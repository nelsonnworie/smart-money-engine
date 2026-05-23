import { useState, useEffect, useRef } from 'react'
import { useTheme } from '../context/ThemeContext'
import { walletData } from '../data/mockData'

export default function SearchBar() {
  const { isDark } = useTheme()
  const [query, setQuery] = useState('')
  const [focused, setFocused] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState(null)
  const inputRef = useRef(null)
  const dropdownRef = useRef(null)

  // Keyboard shortcut
  useEffect(() => {
    const handler = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        inputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])

  // Close dropdown on click outside
  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target) &&
          inputRef.current && !inputRef.current.contains(e.target)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const handleSearch = (val) => {
    setQuery(val)
    if (val.length > 1) {
      setSearching(true)
      setShowDropdown(true)
      setTimeout(() => {
        setResults({
          address: '0x7a3f...b9e2',
          ens: 'alpha-whale.eth',
          totalHolding: '$124.8M',
          labels: ['Smart Whale', 'DeFi Alpha'],
        })
        setSearching(false)
      }, 600)
    } else {
      setShowDropdown(false)
      setResults(null)
    }
  }

  return (
    <div className="relative w-full max-w-lg">
      <div className={`relative flex items-center rounded-xl border transition-all duration-200 ${
        focused
          ? isDark
            ? 'border-brand-400/40 bg-dark-800 shadow-[0_0_20px_rgba(0,212,170,0.06)]'
            : 'border-brand-400 bg-white shadow-[0_0_15px_rgba(0,212,170,0.1)]'
          : isDark
            ? 'border-dark-600/30 bg-dark-800/60 hover:border-dark-500/50'
            : 'border-light-200 bg-light-50 hover:border-light-300'
      }`}>
        <svg className={`w-4 h-4 ml-3 ${isDark ? 'text-dark-400' : 'text-light-400'}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
        </svg>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleSearch(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Search wallet, transaction, token..."
          className={`flex-1 bg-transparent px-3 py-2.5 text-sm outline-none placeholder:text-dark-500 ${
            isDark ? 'text-dark-100' : 'text-light-800'
          }`}
        />
        <div className="flex items-center gap-1 mr-2">
          {searching && (
            <svg className={`w-4 h-4 animate-spin ${isDark ? 'text-brand-400' : 'text-brand-600'}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12a9 9 0 11-6.219-8.56" />
            </svg>
          )}
          <kbd className={`hidden sm:inline-flex text-[10px] px-1.5 py-0.5 rounded font-mono ${
            isDark ? 'bg-dark-700 text-dark-400' : 'bg-light-200 text-light-500'
          }`}>⌘K</kbd>
        </div>
      </div>

      {/* Dropdown */}
      {showDropdown && (
        <div
          ref={dropdownRef}
          className={`absolute top-full left-0 right-0 mt-2 rounded-xl overflow-hidden z-50 animate-scale-in ${
            isDark
              ? 'bg-dark-800 border border-dark-600/30 shadow-xl shadow-black/20'
              : 'bg-white border border-light-200 shadow-xl'
          }`}
        >
          {searching ? (
            <div className="p-4 text-center">
              <div className={`animate-pulse space-y-2`}>
                <div className={`h-3 rounded ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}></div>
                <div className={`h-3 rounded w-2/3 mx-auto ${isDark ? 'bg-dark-700' : 'bg-light-200'}`}></div>
              </div>
            </div>
          ) : results ? (
            <div className="p-3 space-y-2">
              <div className={`flex items-center gap-3 p-2 rounded-lg ${isDark ? 'bg-dark-750/50' : 'bg-light-100'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                  isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-100 text-brand-700'
                }`}>W</div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{results.ens || results.address}</p>
                  <p className={`text-xs font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>{results.address}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold font-mono text-brand-500">{results.totalHolding}</p>
                  <div className="flex gap-1 mt-0.5">
                    {results.labels.slice(0, 2).map((l, i) => (
                      <span key={i} className={`text-[9px] px-1 py-0.5 rounded-full ${
                        isDark ? 'bg-brand-500/10 text-brand-400' : 'bg-brand-50 text-brand-600'
                      }`}>{l}</span>
                    ))}
                  </div>
                </div>
              </div>
              <button
                onClick={() => { setShowDropdown(false); setQuery('') }}
                className={`w-full text-xs py-1.5 rounded-lg font-medium transition-colors ${
                  isDark ? 'text-brand-400 hover:bg-brand-500/8' : 'text-brand-600 hover:bg-brand-50'
                }`}
              >
                View full portfolio &rarr;
              </button>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}