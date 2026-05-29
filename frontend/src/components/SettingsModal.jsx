import { useState, useEffect } from 'react'
import { useTheme } from '../context/ThemeContext'

import { API_BASE } from '../config'

const chainIcons = {
  ethereum: { color: '#627eea', label: 'Ethereum' },
  solana: { color: '#14b8a6', label: 'Solana' },
  arbitrum: { color: '#2d374b', label: 'Arbitrum' },
  base: { color: '#0052ff', label: 'Base' },
  bnb: { color: '#f0b90b', label: 'BNB Chain' },
}

export default function SettingsModal({ open, onClose }) {
  const { isDark } = useTheme()
  const [settings, setSettings] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (open) {
      setLoading(true)
      setSaved(false)
      fetch(`${API_BASE}/api/settings`)
        .then(r => r.json())
        .then(data => {
          setSettings(data)
          setLoading(false)
        })
        .catch(() => {
          // If settings endpoint fails, use defaults
          setSettings({
            alert_threshold: 70,
            min_volume: 10000,
            chains: { ethereum: true, solana: true, arbitrum: true, base: true, bnb: true },
            signal_types: { BUY: true, SELL: true, CLUSTER: true },
            notification_sounds: true,
            telegram_enabled: false,
          })
          setLoading(false)
        })
    }
  }, [open])

  const update = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setSaved(false)
  }

  const updateNested = (parent, key, value) => {
    setSettings(prev => ({
      ...prev,
      [parent]: { ...prev[parent], [key]: value }
    }))
    setSaved(false)
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const res = await fetch(`${API_BASE}/api/settings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      })
      if (res.ok) {
        setSaved(true)
        setTimeout(() => onClose(), 1000)
      }
    } catch (e) {
      console.warn('Failed to save settings', e)
    } finally {
      setSaving(false)
    }
  }

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      
      <div className={`relative w-full max-w-lg rounded-2xl p-6 animate-slide-up ${
        isDark ? 'bg-dark-800 border border-dark-600/30' : 'bg-white border border-light-200'
      }`}>
        <div className="flex items-center justify-between mb-6">
          <h2 className={`text-lg font-bold ${isDark ? 'text-dark-100' : 'text-light-800'}`}>
            ⚙️ Settings
          </h2>
          <button onClick={onClose} className={`p-1 rounded-lg ${isDark ? 'hover:bg-dark-700 text-dark-400' : 'hover:bg-light-100 text-light-500'}`}>
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <svg className={`w-6 h-6 animate-spin ${isDark ? 'text-brand-400' : 'text-brand-600'}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12a9 9 0 11-6.219-8.56" />
            </svg>
          </div>
        ) : !settings ? (
          <div className={`text-center py-8 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
            Failed to load settings
          </div>
        ) : (
          <>
            <div className="space-y-5">
              {/* Alert Threshold */}
              <div>
                <label className={`text-sm font-medium block mb-2 ${isDark ? 'text-dark-200' : 'text-light-700'}`}>
                  Alert Threshold — Minimum Conviction Score
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="50"
                    max="95"
                    step="5"
                    value={settings.alert_threshold || 70}
                    onChange={e => update('alert_threshold', parseInt(e.target.value))}
                    className="flex-1 accent-brand-500"
                  />
                  <span className={`text-lg font-bold font-mono min-w-[48px] text-right ${
                    (settings.alert_threshold || 70) >= 80 ? 'text-green-500' : (settings.alert_threshold || 70) >= 70 ? 'text-yellow-500' : 'text-red-500'
                  }`}>
                    {settings.alert_threshold || 70}%
                  </span>
                </div>
                <p className={`text-[10px] font-mono mt-1 ${isDark ? 'text-dark-500' : 'text-light-400'}`}>
                  Only show signals with conviction at or above this threshold
                </p>
              </div>

              {/* Min Volume Filter */}
              <div>
                <label className={`text-sm font-medium block mb-2 ${isDark ? 'text-dark-200' : 'text-light-700'}`}>
                  Minimum Volume
                </label>
                <select
                  value={settings.min_volume || 10000}
                  onChange={e => update('min_volume', parseInt(e.target.value))}
                  className={`w-full px-3 py-2 rounded-lg text-sm font-mono border focus:outline-none focus:ring-2 ${
                    isDark
                      ? 'bg-dark-800 border-dark-600 text-dark-100 focus:ring-brand-400/30'
                      : 'bg-light-50 border-light-200 text-light-800 focus:ring-brand-500/30'
                  }`}
                >
                  <option value={0}>No minimum</option>
                  <option value={10000}>$10K+</option>
                  <option value={50000}>$50K+</option>
                  <option value={100000}>$100K+</option>
                  <option value={1000000}>$1M+</option>
                </select>
              </div>

              {/* Chains */}
              <div>
                <label className={`text-sm font-medium block mb-2 ${isDark ? 'text-dark-200' : 'text-light-700'}`}>
                  Chains to Monitor
                </label>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {Object.entries(chainIcons).map(([key, chain]) => (
                    <button
                      key={key}
                      onClick={() => updateNested('chains', key, !settings.chains?.[key])}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                        settings.chains?.[key]
                          ? isDark ? 'bg-dark-700 border border-dark-500' : 'bg-light-100 border border-light-300'
                          : isDark ? 'bg-dark-800/50 border border-dark-700 text-dark-500 opacity-50' : 'bg-light-50 border border-light-200 text-light-400 opacity-50'
                      }`}
                    >
                      <span className="w-3 h-3 rounded-full" style={{ backgroundColor: chain.color }} />
                      {chain.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Signal Types */}
              <div>
                <label className={`text-sm font-medium block mb-2 ${isDark ? 'text-dark-200' : 'text-light-700'}`}>
                  Signal Types
                </label>
                <div className="flex gap-2">
                  {['BUY', 'SELL', 'CLUSTER'].map(type => (
                    <button
                      key={type}
                      onClick={() => updateNested('signal_types', type, !settings.signal_types?.[type])}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                        settings.signal_types?.[type]
                          ? type === 'BUY'
                            ? 'bg-green-500/15 text-green-500'
                            : type === 'SELL'
                              ? 'bg-red-500/15 text-red-500'
                              : 'bg-purple-500/15 text-purple-500'
                          : isDark ? 'bg-dark-700 text-dark-500' : 'bg-light-100 text-light-400'
                      }`}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Notification Sounds */}
              <div className="flex items-center justify-between">
                <label className={`text-sm font-medium ${isDark ? 'text-dark-200' : 'text-light-700'}`}>
                  Notification Sounds
                </label>
                <button
                  onClick={() => update('notification_sounds', !settings.notification_sounds)}
                  className={`relative w-10 h-5 rounded-full transition-colors ${
                    settings.notification_sounds ? 'bg-brand-500' : isDark ? 'bg-dark-700' : 'bg-light-200'
                  }`}
                >
                  <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                    settings.notification_sounds ? 'translate-x-5' : ''
                  }`} />
                </button>
              </div>

              {/* Telegram */}
              <div className={`rounded-xl p-3 ${isDark ? 'bg-dark-750/50 border border-dark-600/20' : 'bg-light-50 border border-light-200'}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <svg className="w-4 h-4 text-blue-400" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
                    </svg>
                    <span className={`text-xs font-medium ${isDark ? 'text-dark-200' : 'text-light-700'}`}>Telegram Bot</span>
                  </div>
                  <button
                    onClick={() => update('telegram_enabled', !settings.telegram_enabled)}
                    className={`relative w-10 h-5 rounded-full transition-colors ${
                      settings.telegram_enabled ? 'bg-brand-500' : isDark ? 'bg-dark-700' : 'bg-light-200'
                    }`}
                  >
                    <span className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                      settings.telegram_enabled ? 'translate-x-5' : ''
                    }`} />
                  </button>
                </div>
                {settings.telegram_enabled && (
                  <p className={`text-[10px] font-mono mt-2 ${isDark ? 'text-dark-400' : 'text-light-500'}`}>
                    Connect via @SmartMoneySignalBot to receive real-time alerts
                  </p>
                )}
              </div>
            </div>

            <button
              onClick={handleSave}
              disabled={saving}
              className={`w-full mt-6 py-2.5 rounded-xl text-sm font-bold transition-all ${
                saved
                  ? 'bg-green-500 text-white'
                  : isDark
                    ? 'bg-brand-500/20 text-brand-400 hover:bg-brand-500/30'
                    : 'bg-brand-500 text-white hover:bg-brand-600'
              }`}
            >
              {saved ? '✓ Saved' : saving ? 'Saving...' : 'Save Settings'}
            </button>
          </>
        )}
      </div>
    </div>
  )
}