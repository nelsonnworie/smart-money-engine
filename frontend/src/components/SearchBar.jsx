import { useState, useEffect, useRef } from 'react'
import { useTheme } from '../context/ThemeContext'

import { API_BASE } from '../config'

export default function SearchBar({ onNavigateToExplorer }) {
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

  // ⌘K / Ctrl+K shortcut to focus search
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

  // Close dropdown on outside click
  useEffect(() => {
    const handler = (e) => {
      if (
        dropdownRef.current && !dropdownRef.current.contains(e.target) &&
        inputRef.current && !inputRef.current.contains(e.target)
      ) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  const doSearch = async (val) => {
    if (val.length < 2) {
      setShowDropdown(false)
      setResults(null)
      return
    }
    setSearching(true)
    setShowDropdown(true)
    try {
      const res = await fetch(`${API_BASE}/api/explore?q=${encodeURIComponent(val.trim())}`)
      if (!res.ok) throw new Error('Search failed')
      const data = await res.json()
      setResults(data)
      setError(null)
    } catch (err) {
      setError(err.message)
      setResults(null)
    } finally {
      setSearching(false)
    }
  }

  const handleInput = (val) => {
    setQuery(val)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => doSearch(val), 400)
  }

  // Instead of navigate('/explorer?q=...'), switch the active tab to explorer
  const goToExplorer = (address) => {
    setShowDropdown(false)
    setQuery('')
    if (onNavigateToExplorer) {
      onNavigateToExplorer(address)
    }
  }

  const formatUsd = (amount) => {
    if (!amount) return '$0'
    if (amount >= 1000000) return `$${(amount / 1000000).toFixed(2)}M`
    if (amount >= 1000) return `$${(amount / 1000).toFixed(1)}K`
    return `$${amount.toFixed(0)}`
  }

  return (
    <div className="relative w-full max-w-lg">
      {/* Input */}
      <div className={`relative flex items-center rounded-xl border transition-all duration-200 ${
        focused
          ? isDark
            ? 'border-brand-400/40 bg-dark-800 shadow-[0_0_20px_rgba(0,212,170,0.06)]'
            : 'border-brand-400 bg-white shadow-[0_0_15px_rgba(0,212,170,0.1)]'
          : isDark
            ? 'border-dark-600/30 bg-dark-800/60 hover:border-dark-500/50'
            : 'border-light-200 bg-light-50 hover:border-light-300'
      }`}>
        <svg
          className={`w-4 h-4 ml-3 flex-shrink-0 ${isDark ? 'text-dark-400' : 'text-light-400'}`}
          viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <path d="M21 21l-4.35-4.35" />
        </svg>

        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => handleInput(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          placeholder="Search wallet, transaction, token..."
          className={`flex-1 bg-transparent px-3 py-2.5 text-sm outline-none ${
            isDark
              ? 'text-dark-100 placeholder:text-dark-500'
              : 'text-light-800 placeholder:text-light-400'
          }`}
        />

        <div className="flex items-center gap-1 mr-2">
          {searching && (
            <svg
              className={`w-4 h-4 animate-spin ${isDark ? 'text-brand-400' : 'text-brand-600'}`}
              viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            >
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
          className={`absolute top-full left-0 right-0 mt-2 rounded-xl overflow-hidden z-50 ${
            isDark
              ? 'bg-dark-800 border border-dark-600/30 shadow-xl shadow-black/20'
              : 'bg-white border border-light-200 shadow-xl'
          }`}
        >
          {/* Loading skeleton */}
          {searching && (
            <div className="p-4 text-center">
              <div className="animate-pulse space-y-2">
                <div className={`h-3 rounded ${isDark ? 'bg-dark-700' : 'bg-light-200'}`} />
                <div className={`h-3 rounded w-2/3 mx-auto ${isDark ? 'bg-dark-700' : 'bg-light-200'}`} />
              </div>
            </div>
          )}

          {/* Error */}
          {!searching && error && (
            <div className={`p-4 text-center ${isDark ? 'text-red-400' : 'text-red-600'}`}>
              <p className="text-sm font-medium">Search unavailable</p>
            </div>
          )}

          {/* Results */}
          {!searching && !error && results?.signals?.length > 0 && (
            <div className="p-3 space-y-2">
              {/* Wallet summary row */}
              <div
                onClick={() => goToExplorer(query)}
                className={`flex items-center gap-3 p-2 rounded-lg cursor-pointer transition-colors ${
                  isDark ? 'hover:bg-dark-700/50' : 'hover:bg-light-100'
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 ${
                  isDark ? 'bg-brand-500/15 text-brand-400' : 'bg-brand-100 text-brand-700'
                }`}>
                  W
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {query.slice(0, 10)}...{query.slice(-6)}
                  </p>
                  <p className={`text-xs font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    {results.signals.length} signals ·{' '}
                    {formatUsd(results.signals.reduce((s, x) => s + (x.amount_usd || 0), 0))}
                  </p>
                </div>
                <div className="text-right flex-shrink-0">
                  <p className="text-sm font-bold font-mono text-brand-500">
                    {results.signals.filter(s => s.signal_type === 'BUY').length}B
                    {' / '}
                    {results.signals.filter(s => s.signal_type === 'SELL').length}S
                  </p>
                </div>
              </div>

              {/* Recent signals preview */}
              <p className={`text-[10px] font-mono px-1 ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                Recent signals
              </p>
              {results.signals.slice(0, 3).map((s, i) => (
                <div key={i} className="flex items-center gap-2 px-2 py-1.5 rounded-lg text-xs">
                  <span className={`w-5 h-5 rounded flex items-center justify-center text-[8px] font-bold flex-shrink-0 ${
                    s.signal_type === 'BUY'
                      ? isDark ? 'bg-green-500/15 text-green-400' : 'bg-green-50 text-green-700'
                      : isDark ? 'bg-red-500/15 text-red-400' : 'bg-red-50 text-red-700'
                  }`}>
                    {s.signal_type === 'BUY' ? 'B' : 'S'}
                  </span>
                  <span className="font-medium">
                    {s.token?.startsWith('$') ? s.token : `$${s.token}`}
                  </span>
                  <span className={`font-mono ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    {formatUsd(s.amount_usd)}
                  </span>
                  <span className={`ml-auto font-mono ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                    {s.conviction_score}%
                  </span>
                </div>
              ))}

              <button
                onClick={() => { setShowDropdown(false); setQuery('') }}
                className={`w-full text-xs py-1.5 rounded-lg font-medium transition-colors ${
                  isDark ? 'text-brand-400 hover:bg-brand-500/10' : 'text-brand-600 hover:bg-brand-50'
                }`}
              >
                Clear search
              </button>
            </div>
          )}

          {/* No results */}
          {!searching && !error && results && !results?.signals?.length && !results?.transactions?.length && !results?.balances?.length && (
            <div className={`p-4 text-center text-sm ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
              No results found for "{query}"
            </div>
          )}
        </div>
      )}
    </div>
  )
}