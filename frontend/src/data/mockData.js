// ── KPI Data ──
export const kpiData = {
  totalSignals: 2847,
  totalSignalsChange: 12.5,
  activeClusters: 189,
  activeClustersChange: 8.3,
  chainsDetected: 14,
  chainsDetectedChange: 2,
  highConviction: 42,
  highConvictionChange: -3.1,
}

// ── Signal Feed Data ──
export const signalFeedData = [
  {
    id: 'SIG-001', type: 'Whale Accumulation', chain: 'Ethereum', token: 'LINK',
    amount: '2,847,321', usdValue: '$48.2M', timestamp: '2 min ago', conviction: 94,
    wallet: '0x7a3f...b9e2', label: 'alpha-whale.eth',
    description: 'Multi-sig wallet accumulated 2.84M LINK across 3 CEX withdrawals',
    tokens: ['LINK', 'USDC'],
  },
  {
    id: 'SIG-002', type: 'Cluster Movement', chain: 'Solana', token: 'JUP',
    amount: '15,420,000', usdValue: '$22.1M', timestamp: '8 min ago', conviction: 88,
    wallet: '0xd4e7...a1f3', label: 'sol-whales.sol',
    description: 'Coordinated cluster of 12 wallets acquired JUP in synchronized tx',
    tokens: ['JUP', 'SOL'],
  },
  {
    id: 'SIG-003', type: 'DEX Dumping', chain: 'Arbitrum', token: 'ARB',
    amount: '3,500,000', usdValue: '$5.6M', timestamp: '15 min ago', conviction: 76,
    wallet: '0xb2c1...f7d4', label: '',
    description: 'Smart money distributing ARB via Uniswap V3 pools',
    tokens: ['ARB', 'USDC'],
  },
  {
    id: 'SIG-004', type: 'New Position', chain: 'Base', token: 'AERO',
    amount: '892,450', usdValue: '$3.2M', timestamp: '22 min ago', conviction: 91,
    wallet: '0xf19e...c2b7', label: 'defi-yield.eth',
    description: 'Fresh AERO position opened by top-performing DeFi whale',
    tokens: ['AERO', 'ETH'],
  },
  {
    id: 'SIG-005', type: 'Bridge Activity', chain: 'Polygon', token: 'USDC',
    amount: '12,500,000', usdValue: '$12.5M', timestamp: '31 min ago', conviction: 85,
    wallet: '0x8d2a...e4c9', label: '',
    description: 'Large USDC bridge from Ethereum to Polygon via LayerZero',
    tokens: ['USDC'],
  },
  {
    id: 'SIG-006', type: 'Whale Accumulation', chain: 'Ethereum', token: 'PEPE',
    amount: '850,000,000,000', usdValue: '$10.8M', timestamp: '45 min ago', conviction: 97,
    wallet: '0x3e1b...d8f6', label: 'meme-whale.eth',
    description: 'Fresh whale wallet accumulated 850B PEPE from Binance',
    tokens: ['PEPE'],
  },
  {
    id: 'SIG-007', type: 'Liquidity Add', chain: 'Optimism', token: 'OP/ETH',
    amount: '250,000 OP', usdValue: '$425K', timestamp: '1 hour ago', conviction: 72,
    wallet: '0xc5a9...b3d1', label: '',
    description: 'Smart money added concentrated liquidity on Velodrome',
    tokens: ['OP', 'ETH'],
  },
]

// ── Cluster Data ──
export const clusterData = [
  { id: 'CL-001', name: 'DeFi Alpha', wallets: 24, totalValue: '$156M',
    activeChains: ['Ethereum', 'Arbitrum', 'Base'], topTokens: ['LINK', 'AAVE', 'UNI'],
    avgConviction: 89, lastActive: '1 min ago', signal: 'Accumulating', color: '#00d4aa',
    change24h: 12.4, volume24h: '$18.2M' },
  { id: 'CL-002', name: 'Meme War Room', wallets: 18, totalValue: '$42M',
    activeChains: ['Ethereum', 'Solana'], topTokens: ['PEPE', 'WIF', 'DOGE'],
    avgConviction: 76, lastActive: '5 min ago', signal: 'Trading', color: '#8b5cf6',
    change24h: -3.2, volume24h: '$8.7M' },
  { id: 'CL-003', name: 'Infra Investors', wallets: 31, totalValue: '$283M',
    activeChains: ['Ethereum', 'Polygon', 'Optimism'], topTokens: ['ETH', 'LINK', 'ARB'],
    avgConviction: 93, lastActive: '3 min ago', signal: 'Holding', color: '#f59e0b',
    change24h: 2.1, volume24h: '$5.4M' },
  { id: 'CL-004', name: 'Cross-Chain Arb', wallets: 15, totalValue: '$67M',
    activeChains: ['Arbitrum', 'Base', 'Optimism'], topTokens: ['USDC', 'USDT', 'DAI'],
    avgConviction: 71, lastActive: '< 1 min ago', signal: 'Arbitraging', color: '#ef4444',
    change24h: 5.8, volume24h: '$42.1M' },
  { id: 'CL-005', name: 'DeFi Yield Farmers', wallets: 42, totalValue: '$94M',
    activeChains: ['Ethereum', 'Arbitrum'], topTokens: ['wstETH', 'rETH', 'LDO'],
    avgConviction: 82, lastActive: '12 min ago', signal: 'Staking', color: '#06b6d4',
    change24h: 0.8, volume24h: '$3.2M' },
  { id: 'CL-006', name: 'Solana Maxis', wallets: 27, totalValue: '$198M',
    activeChains: ['Solana'], topTokens: ['SOL', 'JUP', 'PYTH'],
    avgConviction: 95, lastActive: '2 min ago', signal: 'Accumulating', color: '#14b8a6',
    change24h: 8.9, volume24h: '$24.6M' },
]

// ── Wallet Data ──
export const walletData = {
  default: {
    address: '0x7a3f...b9e2',
    ens: 'alpha-whale.eth',
    totalHolding: '$124.8M',
    topHoldings: [
      { token: 'LINK', amount: '2.84M', value: '$48.2M', change24h: 3.2, allocation: 38.6 },
      { token: 'AAVE', amount: '45,200', value: '$12.8M', change24h: -1.5, allocation: 10.3 },
      { token: 'UNI', amount: '320,000', value: '$8.4M', change24h: 5.7, allocation: 6.7 },
      { token: 'ETH', amount: '2,450', value: '$7.9M', change24h: 1.2, allocation: 6.3 },
      { token: 'ARB', amount: '1.2M', value: '$1.9M', change24h: -3.8, allocation: 1.5 },
    ],
    totalTransactions: 1284,
    firstSeen: 'Aug 15, 2024',
    lastActive: '2 min ago',
    profitLoss: '+$32.1M',
    profitLossPercent: 34.7,
    labels: ['Smart Whale', 'DeFi Alpha', 'Long-term Holder'],
    recentActivity: [
      { type: 'Buy', token: 'LINK', amount: '500,000', chain: 'Ethereum', time: '2 min ago', txHash: '0xab34...f9e2' },
      { type: 'Sell', token: 'ARB', amount: '200,000', chain: 'Arbitrum', time: '1 hour ago', txHash: '0xcd56...a3b1' },
      { type: 'Bridge', token: 'USDC', amount: '1,000,000', chain: 'Base', time: '3 hours ago', txHash: '0xef78...d4c5' },
      { type: 'Buy', token: 'UNI', amount: '120,000', chain: 'Ethereum', time: '6 hours ago', txHash: '0xgh90...b2e4' },
    ],
  }
}

// ── Top Movers ──
export const topMoversData = [
  { rank: 1, token: 'ARB', name: 'Arbitrum', price: '$1.60', change24h: -3.8, change7d: -12.4, volume: '$1.1B', signal: 'Distribute', conviction: 76, smartMoneyFlow: '-$5.6M', mcap: '$4.1B', walletCount: 3, walletTotal: '$1.20M' },
  { rank: 2, token: 'PENDLE', name: 'Pendle', price: '$4.82', change24h: 12.4, change7d: 28.7, volume: '$890M', signal: 'Strong Buy', conviction: 94, smartMoneyFlow: '+$18.2M', mcap: '$10.2B', walletCount: 2, walletTotal: '$480K' },
  { rank: 3, token: 'EIGEN', name: 'EigenLayer', price: '$3.12', change24h: 5.1, change7d: 15.3, volume: '$340M', signal: 'Buy', conviction: 91, smartMoneyFlow: '+$480K', mcap: '$890M', walletCount: 2, walletTotal: '$204K' },
  { rank: 4, token: 'TIA', name: 'Celestia', price: '$4.55', change24h: 2.3, change7d: 8.1, volume: '$520M', signal: 'Accumulate', conviction: 78, smartMoneyFlow: '+$8.4M', mcap: '$15.7B', walletCount: 1, walletTotal: '$155K' },
  { rank: 5, token: 'JTO', name: 'Jito', price: '$3.28', change24h: 8.9, change7d: 22.6, volume: '$240M', signal: 'Strong Buy', conviction: 88, smartMoneyFlow: '+$2.1M', mcap: '$680M', walletCount: 1, walletTotal: '$88K' },
  { rank: 6, token: 'LINK', name: 'Chainlink', price: '$16.82', change24h: 12.4, change7d: 28.7, volume: '$2.8B', signal: 'Strong Buy', conviction: 94, smartMoneyFlow: '+$48.2M', mcap: '$10.2B', walletCount: 5, walletTotal: '$48.2M' },
  { rank: 7, token: 'SOL', name: 'Solana', price: '$168.50', change24h: 4.2, change7d: 8.1, volume: '$6.4B', signal: 'Accumulate', conviction: 82, smartMoneyFlow: '+$15.3M', mcap: '$78.4B', walletCount: 8, walletTotal: '$15.3M' },
  { rank: 8, token: 'JUP', name: 'Jupiter', price: '$1.43', change24h: 6.7, change7d: 15.3, volume: '$890M', signal: 'Buy', conviction: 88, smartMoneyFlow: '+$22.1M', mcap: '$1.9B', walletCount: 12, walletTotal: '$22.1M' },
]

// ── Chain Data ──
export const chainData = [
  { name: 'Ethereum', activeClusters: 42, signals24h: 156, smartMoneyFlow: '+$184M', conviction: 87, color: '#627eea', icon: '⟠' },
  { name: 'Solana', activeClusters: 38, signals24h: 124, smartMoneyFlow: '+$96M', conviction: 91, color: '#14b8a6', icon: '◎' },
  { name: 'Arbitrum', activeClusters: 29, signals24h: 89, smartMoneyFlow: '+$42M', conviction: 79, color: '#2d374b', icon: '⬡' },
  { name: 'Base', activeClusters: 24, signals24h: 72, smartMoneyFlow: '+$38M', conviction: 83, color: '#0052ff', icon: '◈' },
  { name: 'BNB Chain', activeClusters: 16, signals24h: 52, smartMoneyFlow: '+$15M', conviction: 71, color: '#f0b90b', icon: '⬢' },
]

// ── Right Panel Data ──
export const rightPanelData = {
  topMovers: [
    { rank: 1, token: 'ARB', wallets: 3, total: '$1.20M', barPercent: 100, conviction: 87, signal: 'BUY' },
    { rank: 2, token: 'PENDLE', wallets: 2, total: '$480K', barPercent: 40, conviction: 74, signal: 'BUY' },
    { rank: 3, token: 'EIGEN', wallets: 2, total: '$204K', barPercent: 17, conviction: 91, signal: 'BUY' },
    { rank: 4, token: 'TIA', wallets: 1, total: '$155K', barPercent: 13, conviction: 78, signal: 'SELL' },
    { rank: 5, token: 'JTO', wallets: 1, total: '$88K', barPercent: 7, conviction: 82, signal: 'BUY' },
  ],
  telegramBot: {
    username: '@SmartMoneySignalBot',
    status: 'online',
    subscribers: 1,
    recentSignals: [
      { action: 'BUY', token: 'ARB', conviction: 87, cluster: true, wallets: 3, total: '$1.2M', chain: 'Arbitrum One' },
      { action: 'BUY', token: 'PENDLE', conviction: 74, cluster: false, wallets: 2, total: '$480K', chain: 'Ethereum' },
      { action: 'SELL', token: 'OP', conviction: 78, cluster: false, wallets: 1, total: '$204K', chain: 'Optimism' },
    ],
  },
}