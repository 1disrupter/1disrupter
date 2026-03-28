// Static mock data for placeholder UI across all dashboard pages
// Used as fallback when backend data isn't available

export const mockSignals = [
  { id: 1, symbol: 'BTC/USD', side: 'BUY', confidence: 87, price: '$67,240', time: '2 min ago', status: 'active' },
  { id: 2, symbol: 'ETH/USD', side: 'SELL', confidence: 74, price: '$1,984', time: '8 min ago', status: 'active' },
  { id: 3, symbol: 'SOL/USD', side: 'BUY', confidence: 69, price: '$82.10', time: '15 min ago', status: 'closed' },
  { id: 4, symbol: 'AVAX/USD', side: 'BUY', confidence: 81, price: '$24.50', time: '22 min ago', status: 'closed' },
];

export const mockPortfolioStats = [
  { label: 'Portfolio Value', value: '$12,480.00', change: '+4.2%', positive: true },
  { label: 'Today\'s P&L', value: '+$340.20', change: '+2.8%', positive: true },
  { label: 'Win Rate', value: '68%', change: '+3%', positive: true },
  { label: 'Open Positions', value: '3', change: '', positive: true },
];

export const mockLeaderboard = [
  { rank: 1, name: 'CryptoWhale', pnl: '+$48,200', winRate: '76%', trades: 342, badge: 'elite' },
  { rank: 2, name: 'AlphaTrader', pnl: '+$32,100', winRate: '71%', trades: 289, badge: 'pro' },
  { rank: 3, name: 'SolanaSniper', pnl: '+$28,400', winRate: '69%', trades: 412, badge: 'pro' },
  { rank: 4, name: 'ETH_Maximalist', pnl: '+$21,800', winRate: '65%', trades: 198, badge: 'pro' },
  { rank: 5, name: 'DeFi_Wizard', pnl: '+$18,600', winRate: '63%', trades: 267, badge: 'free' },
];

export const mockAgents = [
  { name: 'Momentum Scanner', type: 'Technical', status: 'running', accuracy: 72, signals: 48 },
  { name: 'Sentiment Analyzer', type: 'NLP', status: 'running', accuracy: 68, signals: 31 },
  { name: 'Whale Tracker', type: 'On-chain', status: 'paused', accuracy: 81, signals: 12 },
  { name: 'Volatility Engine', type: 'Statistical', status: 'running', accuracy: 65, signals: 57 },
];

export const mockStrategies = [
  { name: 'RSI Divergence Pro', type: 'Momentum', status: 'backtested', sharpe: 1.82, returnPct: '+24.3%', drawdown: '-8.1%', capital: '$5,000' },
  { name: 'MACD Crossover v3', type: 'Trend', status: 'sandbox', sharpe: 1.45, returnPct: '+18.7%', drawdown: '-12.4%', capital: '$3,200' },
  { name: 'Bollinger Breakout', type: 'Mean Reversion', status: 'generated', sharpe: 2.10, returnPct: '+31.6%', drawdown: '-5.2%', capital: '$8,000' },
];

export const mockMarketplaceItems = [
  { name: 'Smart DCA Bot', creator: 'CryptoWhale', price: '$19/mo', rating: 4.8, users: 1240, category: 'Trading Bot' },
  { name: 'Sentiment Alert Pro', creator: 'AlphaLab', price: '$9/mo', rating: 4.5, users: 890, category: 'Signal Plugin' },
  { name: 'Portfolio Rebalancer', creator: 'DeFi_Wizard', price: '$29/mo', rating: 4.9, users: 620, category: 'Portfolio Tool' },
  { name: 'Whale Watch Alerts', creator: 'OnChainPro', price: '$14/mo', rating: 4.6, users: 1850, category: 'On-chain' },
];

export const mockEventAgents = [
  { name: 'Fed Rate Monitor', type: 'Macro', status: 'active', lastTrigger: '2 hours ago', confidence: 85 },
  { name: 'ETH Merge Tracker', type: 'Protocol', status: 'active', lastTrigger: '6 hours ago', confidence: 92 },
  { name: 'BTC Halving Clock', type: 'Cycle', status: 'watching', lastTrigger: '1 day ago', confidence: 78 },
  { name: 'Liquidation Scanner', type: 'DeFi', status: 'active', lastTrigger: '18 min ago', confidence: 88 },
];

export const mockResearchQueries = [
  { query: 'Bitcoin support levels after $65k rejection', time: '3 min ago', tokens: 1240, status: 'complete' },
  { query: 'Ethereum gas fee trend analysis Q1 2026', time: '12 min ago', tokens: 890, status: 'complete' },
  { query: 'SOL vs AVAX ecosystem growth comparison', time: '1 hour ago', tokens: 2100, status: 'complete' },
];

export const mockSimulationResults = [
  { pair: 'BTC/USD', strategy: 'Momentum', trades: 48, winRate: '71%', pnl: '+$2,840', sharpe: 1.92 },
  { pair: 'ETH/USD', strategy: 'Mean Reversion', trades: 62, winRate: '64%', pnl: '+$1,620', sharpe: 1.45 },
  { pair: 'SOL/USD', strategy: 'Breakout', trades: 35, winRate: '74%', pnl: '+$1,180', sharpe: 2.10 },
];

export const mockCopyTraders = [
  { name: 'CryptoWhale', winRate: '76%', pnl: '+$48.2K', followers: 342, tier: 'elite', monthlyReturn: '+12.4%' },
  { name: 'AlphaTrader', winRate: '71%', pnl: '+$32.1K', followers: 189, tier: 'pro', monthlyReturn: '+8.7%' },
  { name: 'SolanaSniper', winRate: '69%', pnl: '+$28.4K', followers: 267, tier: 'pro', monthlyReturn: '+10.2%' },
];

export const mockChartData = [
  { time: 'Mon', value: 10200 },
  { time: 'Tue', value: 10800 },
  { time: 'Wed', value: 10450 },
  { time: 'Thu', value: 11200 },
  { time: 'Fri', value: 11800 },
  { time: 'Sat', value: 11600 },
  { time: 'Sun', value: 12480 },
];
