import { useState, useEffect, useRef } from 'react'
import { useTheme } from '../context/ThemeContext'

const API_BASE = 'https://smart-money-engine-production.up.railway.app'

export default function SearchBar() {
  const { isDark } = useTheme()
  const [query, setQuery] = useState('')
  const [focused, setFocused] = useState(false)
  const [showDropdown, setShowDropdown] = useState(false)
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)
  const dropdownRef = useRef(null)
  const debounceRef = useRef(null)

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
    setError(null)

    if (val.length > 1) {
      setSearching(true)
      setShowDropdown(true)

      // Debounce: clear previous timeout
      if (debounceRef.current) clearTimeout(debounceRef.current)

      debounceRef.current = setTimeout(async () => {
        try {
          const res = await fetch(`${API_BASE}/api/search?q=${encodeURIComponent(val.trim())}`)
          if (!res.ok) throw new Error(`HTTP ${res.status}`)
          const data = await res.json()
          setResults(data)
        } catch (err) {
          console.error('Search failed:', err)
          setError(err.message || 'Search failed')
          setResults(null)
        } finally {
          setSearching(false)
        }
      }, 400) // 400ms debounce
    } else {
      setShowDropdown(false)
      setResults(null)
      setError(null)
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
          ) : error ? (
            <div className={`p-4 text-center ${isDark ? 'text-red-400' : 'text-red-600'}`}>
              <p className="text-sm font-medium">Search unavailable</p>
              <p className={`text-xs mt-1 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                Backend may be offline. Try again later.
              </p>
            </div>
          ) : results ? (
            <div className="p-3 space-y-2">
              {results.wallet ? (
                <div className={`flex items-center gap-3 p-2 rounded-lg ${isDark ? 'bg-dark-750/50' : 'bg-light-100'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-100 text-brand-700'
                  }`}>W</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {results.wallet.ens || results.wallet.address?.slice(0, 10) + '...' + results.wallet.address?.slice(-6)}
                    </p>
                    <p className={`text-xs font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                      {results.wallet.address}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold font-mono text-brand-500">
                      {results.wallet.balance || '$0'}
                    </p>
                    <p className={`text-[9px] ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                      {results.wallet.txCount || 0} trades
                    </p>
                  </div>
                </div>
              ) : results.tx ? (
                <div className={`flex items-center gap-3 p-2 rounded-lg ${isDark ? 'bg-dark-750/50' : 'bg-light-100'}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                    isDark ? 'bg-accent-500/15 text-accent-400' : 'bg-accent-100 text-accent-700'
                  }`}>TX</div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{results.tx.hash?.slice(0, 16)}...</p>
                    <p className={`text-xs ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                      {results.tx.chain} · {results.tx.type || 'transfer'}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold font-mono" style={{ color: results.tx.value > 0 ? '#00d4aa' : '#ef4444' }}>
                      {results.tx.value || '$0'}
                    </p>
                  </div>
                </div>
              ) : (
                <div className={`p-3 text-center text-sm ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                  No results found for "{query}"
                </div>
              )}
              <button
                onClick={() => { setShowDropdown(false); setQuery('') }}
                className={`w-full text-xs py-1.5 rounded-lg font-medium transition-colors ${
                  isDark ? 'text-brand-400 hover:bg-brand-500/8' : 'text-brand-600 hover:bg-brand-50'
                }`}
              >
                Clear search
              </button>
            </div>
          ) : null}
        </div>
      )}
    </div>
  )
}