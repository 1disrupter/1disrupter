/**
 * AlphaAI Performance Metrics Dashboard Component
 * - Paper vs Live trading side-by-side
 * - Equity curve charts (daily + trade-level)
 * - Sharpe ratio with benchmark
 * - Daily PnL breakdown
 * - Compliance labels and disclaimers
 */
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  AreaChart, Area, BarChart, Bar, ReferenceLine, Legend
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  TrendingUp, TrendingDown, AlertTriangle, Shield, Activity,
  DollarSign, Percent, Target, BarChart3, ChevronDown, ChevronUp,
  Info, AlertCircle, CheckCircle, XCircle, Calendar
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Compliance Badge Component
const ComplianceBadge = ({ mode, size = "default" }) => {
  const isLive = mode === "live";
  const baseClasses = size === "large" 
    ? "px-4 py-2 text-base font-bold"
    : "px-2 py-1 text-xs font-semibold";
  
  return (
    <Badge 
      className={`${baseClasses} ${isLive 
        ? 'bg-red-500/20 text-red-400 border border-red-500/50' 
        : 'bg-[#7B61FF]/20 text-[#7B61FF] border border-[#7B61FF]/50'
      }`}
      data-testid={`compliance-badge-${mode}`}
    >
      {isLive ? '⚠️ LIVE TRADING' : '📊 PAPER TRADING'}
    </Badge>
  );
};

// Disclaimer Component
const ComplianceDisclaimer = ({ mode, expanded = false }) => {
  const [isExpanded, setIsExpanded] = useState(expanded);
  const isLive = mode === "live";
  
  const shortDisclaimer = isLive 
    ? "Real funds at risk. Past performance does not guarantee future results."
    : "Simulated results. No real funds involved.";
  
  const riskWarnings = isLive ? [
    "Real funds are at risk",
    "Cryptocurrency is highly volatile", 
    "Past performance ≠ future results",
    "Not financial advice",
    "You may lose your entire investment"
  ] : [
    "Simulated results only",
    "Does not reflect real market conditions",
    "No slippage or market impact included",
    "For educational purposes"
  ];

  return (
    <div 
      className={`rounded-lg border ${isLive ? 'bg-red-500/5 border-red-500/20' : 'bg-[#7B61FF]/5 border-[#7B61FF]/20'} p-3`}
      data-testid={`disclaimer-${mode}`}
    >
      <div className="flex items-start gap-2">
        <AlertTriangle className={`w-4 h-4 mt-0.5 ${isLive ? 'text-red-400' : 'text-[#7B61FF]'}`} />
        <div className="flex-1">
          <p className="text-sm text-zinc-300">{shortDisclaimer}</p>
          
          <button 
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs text-zinc-500 hover:text-zinc-300 mt-1 flex items-center gap-1"
          >
            {isExpanded ? 'Show less' : 'Read full disclaimer'}
            {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          
          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="overflow-hidden"
              >
                <div className="mt-3 pt-3 border-t border-zinc-800">
                  <p className="text-xs text-zinc-400 mb-2">Risk Warnings:</p>
                  <ul className="space-y-1">
                    {riskWarnings.map((warning, i) => (
                      <li key={i} className="flex items-center gap-2 text-xs text-zinc-500">
                        <AlertCircle className="w-3 h-3" />
                        {warning}
                      </li>
                    ))}
                  </ul>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

// Performance Summary Card
const PerformanceSummaryCard = ({ data, mode }) => {
  if (!data) return null;
  
  const isPositive = data.total_return_pct >= 0;
  
  return (
    <Card className="glass-card" data-testid={`summary-card-${mode}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            {mode === 'paper' ? <Activity className="w-5 h-5 text-[#7B61FF]" /> : <DollarSign className="w-5 h-5 text-red-400" />}
            {mode === 'paper' ? 'Paper Trading' : 'Live Trading'}
          </CardTitle>
          <ComplianceBadge mode={mode} />
        </div>
      </CardHeader>
      <CardContent>
        {/* Main Return */}
        <div className="text-center mb-4 py-4 rounded-lg bg-[#050505] border border-zinc-800">
          <p className="text-sm text-zinc-500 mb-1">Total Return</p>
          <p className={`text-4xl font-bold font-['JetBrains_Mono'] ${isPositive ? 'text-[#00FF94]' : 'text-red-400'}`}>
            {isPositive ? '+' : ''}{data.total_return_pct}%
          </p>
          <p className="text-sm text-zinc-500 mt-1">
            ${data.starting_equity.toLocaleString()} → ${data.current_equity.toLocaleString()}
          </p>
        </div>
        
        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
            <p className="text-xs text-zinc-500">Win Rate</p>
            <p className="text-xl font-bold font-['JetBrains_Mono']">{data.win_rate}%</p>
            <p className="text-xs text-zinc-600">{data.winning_trades}W / {data.losing_trades}L</p>
          </div>
          <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
            <p className="text-xs text-zinc-500">Sharpe Ratio</p>
            <p className={`text-xl font-bold font-['JetBrains_Mono'] ${data.sharpe_ratio >= 1 ? 'text-[#00FF94]' : data.sharpe_ratio >= 0 ? 'text-yellow-400' : 'text-red-400'}`}>
              {data.sharpe_ratio}
            </p>
            <p className="text-xs text-zinc-600">{data.sharpe_ratio >= 1 ? 'Good' : data.sharpe_ratio >= 0 ? 'Fair' : 'Poor'}</p>
          </div>
          <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
            <p className="text-xs text-zinc-500">Max Drawdown</p>
            <p className="text-xl font-bold font-['JetBrains_Mono'] text-yellow-400">-{data.max_drawdown}%</p>
          </div>
          <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
            <p className="text-xs text-zinc-500">Profit Factor</p>
            <p className={`text-xl font-bold font-['JetBrains_Mono'] ${data.profit_factor >= 1.5 ? 'text-[#00FF94]' : 'text-zinc-300'}`}>
              {data.profit_factor}x
            </p>
          </div>
        </div>
        
        {/* Best/Worst Days */}
        {(data.best_day || data.worst_day) && (
          <div className="mt-3 pt-3 border-t border-zinc-800 grid grid-cols-2 gap-3">
            {data.best_day && (
              <div className="flex items-center gap-2 text-xs">
                <CheckCircle className="w-4 h-4 text-[#00FF94]" />
                <span className="text-zinc-500">Best:</span>
                <span className="text-[#00FF94] font-mono">+${data.best_day.pnl}</span>
              </div>
            )}
            {data.worst_day && (
              <div className="flex items-center gap-2 text-xs">
                <XCircle className="w-4 h-4 text-red-400" />
                <span className="text-zinc-500">Worst:</span>
                <span className="text-red-400 font-mono">${data.worst_day.pnl}</span>
              </div>
            )}
          </div>
        )}
        
        {/* Disclaimer */}
        <div className="mt-4">
          <ComplianceDisclaimer mode={mode} />
        </div>
      </CardContent>
    </Card>
  );
};

// Equity Curve Chart
const EquityCurveChart = ({ data, mode, type = "daily" }) => {
  if (!data || !data.equity_curve || data.equity_curve.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-zinc-500">
        No data available
      </div>
    );
  }
  
  const chartData = type === "daily" 
    ? data.equity_curve.map(d => ({
        date: d.date,
        equity: d.equity,
        pnl: d.daily_pnl
      }))
    : data.trade_equity?.map((d, i) => ({
        index: i + 1,
        equity: d.equity_after,
        pnl: d.pnl,
        symbol: d.symbol
      })) || [];

  return (
    <Card className="glass-card" data-testid={`equity-chart-${mode}-${type}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <TrendingUp className="w-4 h-4 text-[#00FF94]" />
            {type === "daily" ? "Daily Equity Curve" : "Trade-by-Trade Equity"}
          </CardTitle>
          <ComplianceBadge mode={mode} size="small" />
        </div>
        <CardDescription>
          {type === "daily" 
            ? `${data.period_days} day performance` 
            : `Last ${chartData.length} trades`}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id={`gradient-${mode}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={mode === 'paper' ? '#7B61FF' : '#00FF94'} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={mode === 'paper' ? '#7B61FF' : '#00FF94'} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis 
                dataKey={type === "daily" ? "date" : "index"} 
                stroke="#71717a" 
                tick={{ fill: '#71717a', fontSize: 10 }}
                tickFormatter={type === "daily" ? (v) => v.slice(5) : undefined}
              />
              <YAxis 
                stroke="#71717a" 
                tick={{ fill: '#71717a', fontSize: 10 }}
                tickFormatter={(v) => `$${v.toLocaleString()}`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#0a0a0a', 
                  border: '1px solid #27272a',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value, name) => [
                  name === 'equity' ? `$${value.toLocaleString()}` : `$${value.toFixed(2)}`,
                  name === 'equity' ? 'Equity' : 'P&L'
                ]}
              />
              <ReferenceLine y={data.starting_equity} stroke="#52525b" strokeDasharray="5 5" />
              <Area 
                type="monotone" 
                dataKey="equity" 
                stroke={mode === 'paper' ? '#7B61FF' : '#00FF94'} 
                fill={`url(#gradient-${mode})`}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary Stats */}
        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <div className="p-2 rounded-lg bg-[#050505]">
            <p className="text-xs text-zinc-500">Start</p>
            <p className="text-sm font-mono">${data.starting_equity?.toLocaleString()}</p>
          </div>
          <div className="p-2 rounded-lg bg-[#050505]">
            <p className="text-xs text-zinc-500">End</p>
            <p className="text-sm font-mono">${data.ending_equity?.toLocaleString()}</p>
          </div>
          <div className="p-2 rounded-lg bg-[#050505]">
            <p className="text-xs text-zinc-500">Return</p>
            <p className={`text-sm font-mono ${data.total_return_pct >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
              {data.total_return_pct >= 0 ? '+' : ''}{data.total_return_pct}%
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Sharpe Metrics Card with Benchmark
const SharpeMetricsCard = ({ data, mode }) => {
  if (!data || !data.metrics) return null;
  
  const { metrics } = data;
  const benchmark = metrics.benchmark_comparison;
  
  return (
    <Card className="glass-card" data-testid={`sharpe-card-${mode}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Target className="w-4 h-4 text-[#FFB800]" />
            Risk-Adjusted Returns
          </CardTitle>
          <ComplianceBadge mode={mode} size="small" />
        </div>
      </CardHeader>
      <CardContent>
        {/* Main Metrics */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800 text-center">
            <p className="text-xs text-zinc-500 mb-1">Sharpe Ratio</p>
            <p className={`text-3xl font-bold font-['JetBrains_Mono'] ${
              metrics.sharpe_ratio >= 2 ? 'text-[#00FF94]' : 
              metrics.sharpe_ratio >= 1 ? 'text-blue-400' : 
              metrics.sharpe_ratio >= 0 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {metrics.sharpe_ratio}
            </p>
            <p className="text-xs text-zinc-600 mt-1">
              {metrics.sharpe_ratio >= 2 ? 'Excellent' : 
               metrics.sharpe_ratio >= 1 ? 'Good' : 
               metrics.sharpe_ratio >= 0 ? 'Fair' : 'Poor'}
            </p>
          </div>
          <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800 text-center">
            <p className="text-xs text-zinc-500 mb-1">Sortino Ratio</p>
            <p className={`text-3xl font-bold font-['JetBrains_Mono'] ${metrics.sortino_ratio >= 1 ? 'text-[#00FF94]' : 'text-zinc-300'}`}>
              {metrics.sortino_ratio}
            </p>
            <p className="text-xs text-zinc-600 mt-1">Downside-adjusted</p>
          </div>
        </div>
        
        {/* Additional Metrics */}
        <div className="grid grid-cols-3 gap-2 mb-4">
          <div className="p-2 rounded-lg bg-[#050505] text-center">
            <p className="text-xs text-zinc-500">Ann. Return</p>
            <p className={`text-sm font-mono ${metrics.annualized_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
              {metrics.annualized_return >= 0 ? '+' : ''}{metrics.annualized_return}%
            </p>
          </div>
          <div className="p-2 rounded-lg bg-[#050505] text-center">
            <p className="text-xs text-zinc-500">Volatility</p>
            <p className="text-sm font-mono text-yellow-400">{metrics.annualized_volatility}%</p>
          </div>
          <div className="p-2 rounded-lg bg-[#050505] text-center">
            <p className="text-xs text-zinc-500">Calmar</p>
            <p className="text-sm font-mono">{metrics.calmar_ratio}</p>
          </div>
        </div>
        
        {/* Benchmark Comparison */}
        {benchmark && (
          <div className="p-3 rounded-lg bg-gradient-to-r from-[#FFB800]/5 to-transparent border border-[#FFB800]/20">
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#FFB800]" />
                vs {benchmark.name}
              </p>
              {benchmark.outperforming ? (
                <Badge className="bg-[#00FF94]/20 text-[#00FF94] text-xs">Outperforming</Badge>
              ) : (
                <Badge className="bg-red-400/20 text-red-400 text-xs">Underperforming</Badge>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <p className="text-zinc-500">Benchmark Sharpe</p>
                <p className="font-mono">{benchmark.sharpe_ratio}</p>
              </div>
              <div>
                <p className="text-zinc-500">Alpha</p>
                <p className={`font-mono ${benchmark.alpha >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                  {benchmark.alpha >= 0 ? '+' : ''}{benchmark.alpha}%
                </p>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Daily PnL Chart
const DailyPnLChart = ({ data, mode }) => {
  if (!data || !data.daily_pnl || data.daily_pnl.length === 0) {
    return null;
  }
  
  const chartData = data.daily_pnl.map(d => ({
    date: d.date,
    pnl: d.total_pnl,
    trades: d.trade_count,
    color: d.total_pnl >= 0 ? '#00FF94' : '#ef4444'
  }));

  return (
    <Card className="glass-card" data-testid={`daily-pnl-chart-${mode}`}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-base">
            <Calendar className="w-4 h-4 text-blue-400" />
            Daily P&L
          </CardTitle>
          <div className="flex items-center gap-2">
            <span className="text-xs text-zinc-500">
              {data.profitable_days} profit / {data.losing_days} loss days
            </span>
            <ComplianceBadge mode={mode} size="small" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-48">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
              <XAxis 
                dataKey="date" 
                stroke="#71717a" 
                tick={{ fill: '#71717a', fontSize: 10 }}
                tickFormatter={(v) => v.slice(5)}
              />
              <YAxis 
                stroke="#71717a" 
                tick={{ fill: '#71717a', fontSize: 10 }}
                tickFormatter={(v) => `$${v}`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#0a0a0a', 
                  border: '1px solid #27272a',
                  borderRadius: '8px',
                  color: '#fff'
                }}
                formatter={(value) => [`$${value.toFixed(2)}`, 'P&L']}
              />
              <ReferenceLine y={0} stroke="#52525b" />
              <Bar 
                dataKey="pnl" 
                fill="#00FF94"
                radius={[4, 4, 0, 0]}
              >
                {chartData.map((entry, index) => (
                  <rect key={index} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary */}
        <div className="mt-4 grid grid-cols-3 gap-2 text-center">
          <div className="p-2 rounded-lg bg-[#050505]">
            <p className="text-xs text-zinc-500">Total P&L</p>
            <p className={`text-sm font-mono ${data.total_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
              ${data.total_pnl.toLocaleString()}
            </p>
          </div>
          <div className="p-2 rounded-lg bg-[#050505]">
            <p className="text-xs text-zinc-500">Avg Daily</p>
            <p className={`text-sm font-mono ${data.avg_daily_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
              ${data.avg_daily_pnl.toFixed(2)}
            </p>
          </div>
          <div className="p-2 rounded-lg bg-[#050505]">
            <p className="text-xs text-zinc-500">Win Rate</p>
            <p className="text-sm font-mono">{data.win_day_rate}%</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Main Performance Metrics Component
export const PerformanceMetrics = ({ walletAddress, className = "" }) => {
  const [activeTab, setActiveTab] = useState("overview");
  const [paperSummary, setPaperSummary] = useState(null);
  const [liveSummary, setLiveSummary] = useState(null);
  const [paperEquity, setPaperEquity] = useState(null);
  const [liveEquity, setLiveEquity] = useState(null);
  const [paperTradeEquity, setPaperTradeEquity] = useState(null);
  const [liveTradeEquity, setLiveTradeEquity] = useState(null);
  const [paperSharpe, setPaperSharpe] = useState(null);
  const [liveSharpe, setLiveSharpe] = useState(null);
  const [paperDailyPnL, setPaperDailyPnL] = useState(null);
  const [liveDailyPnL, setLiveDailyPnL] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const fetchAllData = useCallback(async () => {
    if (!walletAddress) return;
    
    setLoading(true);
    const wallet = walletAddress || 'demo_user';
    
    try {
      // Fetch all data in parallel
      const [
        paperSumRes,
        liveSumRes,
        paperEqRes,
        liveEqRes,
        paperTradeEqRes,
        liveTradeEqRes,
        paperSharpeRes,
        liveSharpeRes,
        paperPnLRes,
        livePnLRes
      ] = await Promise.allSettled([
        axios.get(`${API}/metrics/summary?wallet_address=${wallet}&mode=paper&days=${days}`),
        axios.get(`${API}/metrics/summary?wallet_address=${wallet}&mode=live&days=${days}`),
        axios.get(`${API}/metrics/equity-curve/daily?wallet_address=${wallet}&mode=paper&days=${days}`),
        axios.get(`${API}/metrics/equity-curve/daily?wallet_address=${wallet}&mode=live&days=${days}`),
        axios.get(`${API}/metrics/equity-curve/trades?wallet_address=${wallet}&mode=paper&limit=50`),
        axios.get(`${API}/metrics/equity-curve/trades?wallet_address=${wallet}&mode=live&limit=50`),
        axios.get(`${API}/metrics/sharpe?wallet_address=${wallet}&mode=paper&days=${days}&include_benchmark=true`),
        axios.get(`${API}/metrics/sharpe?wallet_address=${wallet}&mode=live&days=${days}&include_benchmark=true`),
        axios.get(`${API}/metrics/daily-pnl?wallet_address=${wallet}&mode=paper&days=${days}`),
        axios.get(`${API}/metrics/daily-pnl?wallet_address=${wallet}&mode=live&days=${days}`)
      ]);
      
      if (paperSumRes.status === 'fulfilled') setPaperSummary(paperSumRes.value.data);
      if (liveSumRes.status === 'fulfilled') setLiveSummary(liveSumRes.value.data);
      if (paperEqRes.status === 'fulfilled') setPaperEquity(paperEqRes.value.data);
      if (liveEqRes.status === 'fulfilled') setLiveEquity(liveEqRes.value.data);
      if (paperTradeEqRes.status === 'fulfilled') setPaperTradeEquity(paperTradeEqRes.value.data);
      if (liveTradeEqRes.status === 'fulfilled') setLiveTradeEquity(liveTradeEqRes.value.data);
      if (paperSharpeRes.status === 'fulfilled') setPaperSharpe(paperSharpeRes.value.data);
      if (liveSharpeRes.status === 'fulfilled') setLiveSharpe(liveSharpeRes.value.data);
      if (paperPnLRes.status === 'fulfilled') setPaperDailyPnL(paperPnLRes.value.data);
      if (livePnLRes.status === 'fulfilled') setLiveDailyPnL(livePnLRes.value.data);
      
    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
    
    setLoading(false);
  }, [walletAddress, days]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  if (loading) {
    return (
      <div className={`space-y-4 ${className}`}>
        <div className="h-64 rounded-xl bg-zinc-900/50 animate-pulse" />
        <div className="grid grid-cols-2 gap-4">
          <div className="h-48 rounded-xl bg-zinc-900/50 animate-pulse" />
          <div className="h-48 rounded-xl bg-zinc-900/50 animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`} data-testid="performance-metrics">
      {/* Header with Period Selector */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <BarChart3 className="w-6 h-6 text-[#7B61FF]" />
          Performance Metrics
        </h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-500">Period:</span>
          {[7, 30, 90].map(d => (
            <Button
              key={d}
              variant={days === d ? "default" : "outline"}
              size="sm"
              onClick={() => setDays(d)}
              className={days === d ? "bg-[#7B61FF]" : "border-zinc-700"}
            >
              {d}D
            </Button>
          ))}
        </div>
      </div>

      {/* Tabs Navigation */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-zinc-900/50">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="equity">Equity Curves</TabsTrigger>
          <TabsTrigger value="risk">Risk Metrics</TabsTrigger>
          <TabsTrigger value="daily">Daily P&L</TabsTrigger>
        </TabsList>

        {/* Overview Tab - Side by Side Comparison */}
        <TabsContent value="overview" className="mt-4">
          <div className="grid md:grid-cols-2 gap-6">
            <PerformanceSummaryCard data={paperSummary} mode="paper" />
            <PerformanceSummaryCard data={liveSummary} mode="live" />
          </div>
        </TabsContent>

        {/* Equity Curves Tab */}
        <TabsContent value="equity" className="mt-4 space-y-6">
          {/* Daily Equity */}
          <div className="grid md:grid-cols-2 gap-6">
            <EquityCurveChart data={paperEquity} mode="paper" type="daily" />
            <EquityCurveChart data={liveEquity} mode="live" type="daily" />
          </div>
          
          {/* Trade-Level Equity */}
          <div className="grid md:grid-cols-2 gap-6">
            <EquityCurveChart data={paperTradeEquity} mode="paper" type="trade" />
            <EquityCurveChart data={liveTradeEquity} mode="live" type="trade" />
          </div>
        </TabsContent>

        {/* Risk Metrics Tab */}
        <TabsContent value="risk" className="mt-4">
          <div className="grid md:grid-cols-2 gap-6">
            <SharpeMetricsCard data={paperSharpe} mode="paper" />
            <SharpeMetricsCard data={liveSharpe} mode="live" />
          </div>
        </TabsContent>

        {/* Daily P&L Tab */}
        <TabsContent value="daily" className="mt-4">
          <div className="grid md:grid-cols-2 gap-6">
            <DailyPnLChart data={paperDailyPnL} mode="paper" />
            <DailyPnLChart data={liveDailyPnL} mode="live" />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PerformanceMetrics;
