// Smart Money Engine API Service
// Connects to your Railway backend

const API_BASE = 'https://smart-money-engine-production.up.railway.app'

export async function fetchSignals() {
  const res = await fetch(`${API_BASE}/signals`)
  if (!res.ok) throw new Error('Failed to fetch signals')
  return res.json()
}

export async function fetchWallets() {
  const res = await fetch(`${API_BASE}/wallets`)
  if (!res.ok) throw new Error('Failed to fetch wallets')
  return res.json()
}

export async function fetchTopMovers() {
  const res = await fetch(`${API_BASE}/top-movers`)
  if (!res.ok) throw new Error('Failed to fetch top movers')
  return res.json()
}

export async function fetchClusters() {
  const res = await fetch(`${API_BASE}/clusters`)
  if (!res.ok) throw new Error('Failed to fetch clusters')
  return res.json()
}

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`)
  if (!res.ok) throw new Error('Failed to fetch health')
  return res.json()
}

export async function fetchWalletByAddress(address) {
  const res = await fetch(`${API_BASE}/wallets/${address}`)
  if (!res.ok) throw new Error('Wallet not found')
  return res.json()
}

export { API_BASE }