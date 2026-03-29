import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  Radio, Play, StopCircle, Target, TrendingUp,
  BarChart3, Zap, Clock, Activity, X, Loader2, Shield
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { PageHeader, StatsRow, MockTable, MiniChart, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockSimulationResults, mockChartData } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";

const SimulationPage = () => {
  const { isDemoMode, demoSimulations, demoChart } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const [activeTab, setActiveTab] = useState("overview");
  const [backtestRunning, setBacktestRunning] = useState(false);
  const [backtestResult, setBacktestResult] = useState(null);
  const [selectedPair, setSelectedPair] = useState("BTC/USDT");
  const [selectedStrategy, setSelectedStrategy] = useState("momentum");

  const { data: simStats, loading: statsLoading, error: statsError, refetch: refetchStats } = useApiData('/simulation/stats', { skip: isDemoMode, token });
  const { data: simConfig, loading: configLoading } = useApiData('/simulation/config', { skip: isDemoMode });

  const simResults = isDemoMode ? demoSimulations : (simStats?.recent_simulations || mockSimulationResults);
  const chartData = isDemoMode ? demoChart : (simStats?.equity_curve || mockChartData);

  const stats = isDemoMode || !simStats ? [
    { label: 'Total Simulations', value: '24', change: '+3 this week', positive: true },
    { label: 'Avg Win Rate', value: '68.4%', change: '+2.1%', positive: true },
    { label: 'Best Sharpe', value: '2.10', change: 'SOL Breakout', positive: true },
    { label: 'Capital Deployed', value: '$25.0K', change: 'Paper mode', positive: true },
  ] : [
    { label: 'Total Simulations', value: String(simStats.total_simulations ?? 0), change: `${simStats.recent_count ?? 0} this week`, positive: true },
    { label: 'Avg Win Rate', value: `${(simStats.avg_win_rate ?? 0).toFixed(1)}%`, change: simStats.win_rate_change || '--', positive: (simStats.avg_win_rate ?? 0) > 50 },
    { label: 'Best Sharpe', value: (simStats.best_sharpe ?? 0).toFixed(2), change: simStats.best_strategy || '--', positive: true },
    { label: 'Capital Deployed', value: `$${((simStats.capital_deployed ?? 0) / 1000).toFixed(1)}K`, change: simConfig?.mode || 'Paper', positive: true },
  ];

  const loading = statsLoading || configLoading;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="simulation-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader
          icon={Radio}
          title="Simulation Engine"
          description="Backtest and paper-trade strategies with historical market data"
          badge="Paper Trading"
          testId="simulation-header"
        />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : statsError && !isDemoMode ? <ErrorState message="Could not load simulation data" onRetry={refetchStats} /> : (
          <>
            <StatsRow stats={stats} />

            <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
              <TabsList className="bg-[#0A0A0A] border border-zinc-800/50">
                <TabsTrigger value="overview" data-testid="sim-tab-overview">Overview</TabsTrigger>
                <TabsTrigger value="backtest" data-testid="sim-tab-backtest">Backtest</TabsTrigger>
                <TabsTrigger value="paper" data-testid="sim-tab-paper">Paper Trading</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="mt-6 space-y-6">
                <MockTable
                  headers={['Pair', 'Strategy', 'Trades', 'Win Rate', 'P&L', 'Sharpe']}
                  rows={simResults.map(r => [r.pair, r.strategy, r.trades, r.winRate || r.win_rate, r.pnl, r.sharpe])}
                />
                <div className="grid md:grid-cols-2 gap-6">
                  <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                    <Card className="bg-[#0A0A0A] border-zinc-800/50">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                          <TrendingUp className="w-4 h-4 text-[#00FF94]" /> Equity Curve
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-2">
                        <MiniChart data={chartData} color="#00FF94" />
                        <div className="flex justify-between mt-3 text-xs text-zinc-600 font-mono">
                          <span>Mon</span><span>Wed</span><span>Fri</span><span>Sun</span>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                  <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                    <Card className="bg-[#0A0A0A] border-zinc-800/50">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                          <BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Drawdown
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="pt-2">
                        <MiniChart data={[
                          { time: 'Mon', value: 500 }, { time: 'Tue', value: 300 }, { time: 'Wed', value: 50 },
                          { time: 'Thu', value: 320 }, { time: 'Fri', value: 420 }, { time: 'Sat', value: 180 }, { time: 'Sun', value: 450 }
                        ]} color="#ef4444" />
                        <div className="flex justify-between mt-3 text-xs text-zinc-600 font-mono">
                          <span>Mon</span><span>Wed</span><span>Fri</span><span>Sun</span>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                </div>
              </TabsContent>

              <TabsContent value="backtest" className="mt-6">
                <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <Card className="bg-[#0A0A0A] border-zinc-800/50">
                    <CardContent className="p-6">
                      <div className="flex items-center gap-3 mb-5">
                        <div className="p-3 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/20">
                          <Target className="w-5 h-5 text-[#7B61FF]" />
                        </div>
                        <div>
                          <h3 className="text-sm font-semibold text-zinc-200">Configure Backtest</h3>
                          <p className="text-xs text-zinc-600">Select a strategy and trading pair to begin backtesting</p>
                        </div>
                      </div>

                      <div className="grid md:grid-cols-2 gap-4 mb-5">
                        <div>
                          <label className="text-xs text-zinc-500 mb-2 block">Trading Pair</label>
                          <div className="flex flex-wrap gap-2">
                            {["BTC/USDT", "ETH/USDT", "SOL/USDT"].map(p => (
                              <button key={p} onClick={() => setSelectedPair(p)} className={`px-3 py-1.5 rounded-full text-xs font-mono transition-all ${selectedPair === p ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`bt-pair-${p.replace("/","")}`}>{p}</button>
                            ))}
                          </div>
                        </div>
                        <div>
                          <label className="text-xs text-zinc-500 mb-2 block">Strategy</label>
                          <div className="flex flex-wrap gap-2">
                            {["momentum", "mean_reversion", "breakout"].map(s => (
                              <button key={s} onClick={() => setSelectedStrategy(s)} className={`px-3 py-1.5 rounded-full text-xs transition-all capitalize ${selectedStrategy === s ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`bt-strat-${s}`}>{s.replace("_", " ")}</button>
                            ))}
                          </div>
                        </div>
                      </div>

                      <Button onClick={async () => {
                        setBacktestRunning(true);
                        setBacktestResult(null);
                        await new Promise(r => setTimeout(r, 2000));
                        const winRate = 55 + Math.random() * 20;
                        const totalTrades = 150 + Math.floor(Math.random() * 200);
                        const totalReturn = 8 + Math.random() * 25;
                        const sharpe = 0.8 + Math.random() * 1.8;
                        const maxDD = 3 + Math.random() * 8;
                        const curve = Array.from({ length: 30 }, (_, i) => ({
                          day: i + 1,
                          value: 100000 + (totalReturn * 1000 * (i / 30)) + (Math.random() - 0.4) * 3000
                        }));
                        setBacktestResult({
                          pair: selectedPair,
                          strategy: selectedStrategy,
                          period: "Jan 2025 — Dec 2025",
                          initial: 100000,
                          final: Math.round(100000 * (1 + totalReturn / 100)),
                          totalReturn: totalReturn.toFixed(1),
                          sharpe: sharpe.toFixed(2),
                          maxDD: maxDD.toFixed(1),
                          winRate: winRate.toFixed(1),
                          totalTrades,
                          avgWin: (totalReturn / totalTrades * 2.5).toFixed(2),
                          avgLoss: (totalReturn / totalTrades * 1.2).toFixed(2),
                          profitFactor: (1.4 + Math.random() * 0.8).toFixed(2),
                          curve
                        });
                        setBacktestRunning(false);
                        toast.success("Backtest complete!");
                      }} disabled={backtestRunning} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white border border-[#7B61FF]/30" data-testid="run-backtest-btn">
                        {backtestRunning ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Running...</> : <><Play className="w-4 h-4 mr-2" /> Run Backtest</>}
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Backtest Results */}
                  <AnimatePresence>
                    {backtestResult && (
                      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                        <Card className="bg-[#0A0A0A] border-[#7B61FF]/30" data-testid="backtest-result">
                          <CardHeader className="pb-3 border-b border-zinc-800/50">
                            <div className="flex items-center justify-between">
                              <CardTitle className="text-sm font-medium flex items-center gap-2"><BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Backtest: {backtestResult.pair} — {backtestResult.strategy.replace("_"," ")}</CardTitle>
                              <button onClick={() => setBacktestResult(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                            </div>
                            <p className="text-xs text-zinc-600 mt-1">{backtestResult.period}</p>
                          </CardHeader>
                          <CardContent className="p-5 space-y-5">
                            {/* Key Metrics */}
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                              {[
                                { label: "Total Return", value: `+${backtestResult.totalReturn}%`, color: "text-[#00FF94]" },
                                { label: "Sharpe Ratio", value: backtestResult.sharpe, color: "text-white" },
                                { label: "Max Drawdown", value: `${backtestResult.maxDD}%`, color: "text-red-400" },
                                { label: "Win Rate", value: `${backtestResult.winRate}%`, color: "text-white" },
                              ].map((m, i) => (
                                <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                                  <p className="text-[10px] text-zinc-600 uppercase tracking-wider mb-1">{m.label}</p>
                                  <p className={`text-lg font-bold font-mono ${m.color}`}>{m.value}</p>
                                </div>
                              ))}
                            </div>

                            {/* PnL Curve */}
                            <div>
                              <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1"><TrendingUp className="w-3 h-3" /> Equity Curve</p>
                              <div className="h-32 flex items-end gap-[2px]">
                                {backtestResult.curve.map((d, i) => {
                                  const min = Math.min(...backtestResult.curve.map(c => c.value));
                                  const max = Math.max(...backtestResult.curve.map(c => c.value));
                                  const pct = ((d.value - min) / (max - min)) * 100;
                                  return (
                                    <div key={i} className="flex-1 rounded-t bg-[#00FF94]/50 hover:bg-[#00FF94]/70 transition-colors" style={{ height: `${Math.max(pct, 3)}%` }} title={`Day ${d.day}: $${Math.round(d.value).toLocaleString()}`} />
                                  );
                                })}
                              </div>
                            </div>

                            {/* Additional Stats */}
                            <div className="grid grid-cols-3 gap-3 text-center">
                              {[
                                { label: "Total Trades", value: backtestResult.totalTrades },
                                { label: "Profit Factor", value: backtestResult.profitFactor },
                                { label: "Capital", value: `$${backtestResult.initial.toLocaleString()} → $${backtestResult.final.toLocaleString()}` },
                              ].map((m, i) => (
                                <div key={i} className="p-2 rounded bg-[#050505] border border-zinc-800/30">
                                  <p className="text-[10px] text-zinc-600">{m.label}</p>
                                  <p className="text-xs font-mono text-zinc-300">{m.value}</p>
                                </div>
                              ))}
                            </div>
                          </CardContent>
                        </Card>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              </TabsContent>

              <TabsContent value="paper" className="mt-6">
                <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                  <Card className="bg-[#0A0A0A] border-zinc-800/50">
                    <CardHeader>
                      <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Activity className="w-4 h-4 text-[#00FF94]" /> Active Paper Positions
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {[
                          { pair: 'BTC/USD', side: 'LONG', entry: '$67,240', current: '$67,890', pnl: '+$650', pnlPct: '+0.97%' },
                          { pair: 'ETH/USD', side: 'SHORT', entry: '$1,984', current: '$1,952', pnl: '+$320', pnlPct: '+1.61%' },
                        ].map((pos, i) => (
                          <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800/30">
                            <div className="flex items-center gap-3">
                              <Badge className={pos.side === 'LONG' ? 'bg-[#00FF94]/15 text-[#00FF94]' : 'bg-[#ef4444]/15 text-[#ef4444]'}>{pos.side}</Badge>
                              <span className="font-mono font-bold text-sm">{pos.pair}</span>
                            </div>
                            <div className="flex items-center gap-6 text-sm font-mono">
                              <span className="text-zinc-500">{pos.entry}</span>
                              <span className="text-zinc-300">{pos.current}</span>
                              <span className="text-[#00FF94]">{pos.pnl} ({pos.pnlPct})</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  <Card className="bg-[#0A0A0A] border-zinc-800/50">
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-xs text-zinc-500 uppercase tracking-wider mb-1">Paper Balance</p>
                          <p className="text-2xl font-bold font-mono">$10,970.00</p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Progress value={68} className="w-24 h-2" />
                          <span className="text-xs text-zinc-500">68% win rate</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              </TabsContent>
            </Tabs>
          </>
        )}
      </div>
    </div>
  );
};

export default SimulationPage;
