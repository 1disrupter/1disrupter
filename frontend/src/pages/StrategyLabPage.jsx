import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import { FlaskConical, Sparkles, ArrowUpRight, TrendingUp, Rocket, Loader2, X, Play, BarChart3 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockStrategies } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";
import { API } from "../lib/constants";

const statusColors = { generated: "bg-zinc-600/15 text-zinc-400", backtested: "bg-[#7B61FF]/15 text-[#7B61FF]", sandbox: "bg-[#FFB800]/15 text-[#FFB800]", live: "bg-[#00FF94]/15 text-[#00FF94]" };

const StrategyLabPage = () => {
  const { isDemoMode, demoStrategies } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;

  const { data: apiData, loading, error, refetch } = useApiData("/lab/strategies", { skip: isDemoMode, token });

  const strategies = isDemoMode ? demoStrategies : (apiData?.strategies || apiData || mockStrategies);
  const arr = Array.isArray(strategies) ? strategies : [];

  const [generating, setGenerating] = useState(false);
  const [genResult, setGenResult] = useState(null);
  const [backtesting, setBacktesting] = useState(null);
  const [backtestResult, setBacktestResult] = useState(null);
  const [selectedType, setSelectedType] = useState("momentum");

  const countByStatus = (s) => arr.filter(x => x.status === s).length;
  const stats = [
    { label: "Generated", value: String(countByStatus("generated") || arr.length), change: "Strategies", positive: true },
    { label: "Backtested", value: String(countByStatus("backtested")), change: "Passed QA", positive: true },
    { label: "In Sandbox", value: String(countByStatus("sandbox")), change: "Paper testing", positive: true },
    { label: "Live", value: String(countByStatus("live")), change: "Ready to deploy", positive: true },
  ];

  const generateStrategy = async () => {
    if (isDemoMode) {
      setGenerating(true);
      await new Promise(r => setTimeout(r, 1000));
      setGenResult({
        name: `Momentum Strategy #${Math.floor(Math.random() * 900 + 100)}`,
        type: selectedType,
        description: "AI-generated momentum trading strategy optimized for current market conditions",
        parameters: { lookback: 20, threshold: 2.5, risk_level: "medium" },
        status: "generated",
        id: `demo-${Date.now()}`
      });
      setGenerating(false);
      toast.success("Strategy generated!");
      return;
    }
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/lab/strategies/generate`, { strategy_type: selectedType, risk_level: "medium" });
      if (res.data?.success) {
        setGenResult(res.data.strategy);
        toast.success("Strategy generated!");
        refetch();
      }
    } catch (e) {
      toast.error("Failed to generate strategy");
    }
    setGenerating(false);
  };

  const runBacktest = async (strategyId) => {
    if (isDemoMode) {
      setBacktesting(strategyId);
      await new Promise(r => setTimeout(r, 1500));
      setBacktestResult({
        strategy_id: strategyId,
        period: "2024-01-01 to 2024-12-31",
        initial_capital: 100000,
        final_capital: 118500,
        total_return: 18.5,
        sharpe_ratio: 1.92,
        max_drawdown: 4.2,
        win_rate: 64.3,
        total_trades: 237,
        profit_factor: 1.82,
        equity_curve: Array.from({ length: 30 }, (_, i) => ({ day: i, value: 100000 + i * 617 + (Math.sin(i) * 1500) })),
        data_source: "mock",
      });
      setBacktesting(null);
      return;
    }
    setBacktesting(strategyId);
    try {
      const res = await axios.post(`${API}/lab/strategies/${strategyId}/backtest`, { initial_capital: 100000 });
      if (res.data?.success) {
        setBacktestResult(res.data.results);
        toast.success("Backtest complete!");
        refetch();
      }
    } catch (e) {
      toast.error("Market data unavailable — using fallback data");
    }
    setBacktesting(null);
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="strategy-lab-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader icon={FlaskConical} title="Strategy Lab" description="AI-generated strategies, backtesting, and autonomous deployment pipeline" testId="strategy-lab-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load strategies" onRetry={refetch} /> : (
          <>
            {/* Pipeline */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-5">
                  <p className="text-xs text-zinc-500 mb-4 uppercase tracking-wider">Strategy Pipeline</p>
                  <div className="flex items-center gap-2">
                    {["Generated", "Backtested", "Sandbox", "Live"].map((stage, i) => (
                      <div key={i} className="flex items-center gap-2 flex-1">
                        <div className={`flex-1 h-2 rounded-full ${i < 2 ? "bg-[#7B61FF]" : i === 2 ? "bg-[#FFB800]/40" : "bg-zinc-800"}`} />
                        {i < 3 && <ArrowUpRight className="w-3 h-3 text-zinc-600 shrink-0" />}
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-between mt-2 text-[10px] text-zinc-600 font-mono">
                    <span>Generated ({countByStatus("generated") || arr.length})</span><span>Backtested ({countByStatus("backtested")})</span><span>Sandbox ({countByStatus("sandbox")})</span><span>Live ({countByStatus("live")})</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <StatsRow stats={stats} />

            {/* Strategy Rankings Table */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-3"><CardTitle className="text-sm font-medium flex items-center gap-2"><TrendingUp className="w-4 h-4 text-[#00FF94]" /> Strategy Rankings</CardTitle></CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead><tr className="border-b border-zinc-800/50">{["Strategy", "Type", "Status", "Sharpe", "Return", "Drawdown", "Action"].map(h => (<th key={h} className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">{h}</th>))}</tr></thead>
                      <tbody className="divide-y divide-zinc-800/30">
                        {arr.map((s, i) => (
                          <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                            <td className="px-4 py-4 text-sm font-medium text-zinc-200">{s.name}</td>
                            <td className="px-4 py-4 text-xs text-zinc-500">{s.type}</td>
                            <td className="px-4 py-4"><Badge className={statusColors[s.status] || "bg-zinc-600/15 text-zinc-400"}>{s.status}</Badge></td>
                            <td className="px-4 py-4 text-sm font-mono text-zinc-300">{s.sharpe || s.sharpe_ratio || "--"}</td>
                            <td className="px-4 py-4 text-sm font-mono text-[#00FF94]">{s.returnPct || s.return_pct || s.total_return ? `${s.returnPct || s.return_pct || s.total_return}%` : "--"}</td>
                            <td className="px-4 py-4 text-sm font-mono text-red-400">{s.drawdown || s.max_drawdown ? `${s.drawdown || s.max_drawdown}%` : "--"}</td>
                            <td className="px-4 py-4">
                              {(s.status === "generated" || s.status === "backtested") && (
                                <Button size="sm" onClick={() => runBacktest(s.id)} disabled={backtesting === s.id} className="rounded-full bg-[#7B61FF]/20 text-[#7B61FF] hover:bg-[#7B61FF]/30 text-xs" data-testid={`backtest-${i}`}>
                                  {backtesting === s.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Play className="w-3 h-3 mr-1" />Backtest</>}
                                </Button>
                              )}
                              {s.status === "sandbox" && <Badge className="bg-[#FFB800]/10 text-[#FFB800] text-[10px]">Testing</Badge>}
                              {s.status === "live" && <Badge className="bg-[#00FF94]/10 text-[#00FF94] text-[10px]">Active</Badge>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Backtest Result */}
            <AnimatePresence>
              {backtestResult && (
                <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mb-8">
                  <Card className="bg-[#0A0A0A] border-[#7B61FF]/30" data-testid="backtest-result">
                    <CardHeader className="pb-3 border-b border-zinc-800/50">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium flex items-center gap-2"><BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Backtest Results</CardTitle>
                        <div className="flex items-center gap-2">
                          <Badge className={backtestResult.data_source === "coingecko" ? "bg-[#00FF94]/10 text-[#00FF94] text-[9px]" : "bg-zinc-700 text-zinc-400 text-[9px]"} data-testid="data-source-badge">
                            {backtestResult.data_source === "coingecko" ? "Data: CoinGecko" : "Demo Mode — Mock Data"}
                          </Badge>
                          <button onClick={() => setBacktestResult(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent className="p-5 space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {[
                          { label: "Total Return", value: `${backtestResult.total_return}%`, color: backtestResult.total_return >= 0 ? "text-[#00FF94]" : "text-red-400" },
                          { label: "Sharpe Ratio", value: backtestResult.sharpe_ratio, color: "text-white" },
                          { label: "Max Drawdown", value: `${backtestResult.max_drawdown}%`, color: "text-red-400" },
                          { label: "Win Rate", value: `${backtestResult.win_rate}%`, color: "text-white" },
                        ].map((m, i) => (
                          <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                            <p className="text-[10px] text-zinc-600 uppercase tracking-wider mb-1">{m.label}</p>
                            <p className={`text-lg font-bold font-mono ${m.color}`}>{m.value}</p>
                          </div>
                        ))}
                      </div>

                      {/* Equity Curve */}
                      {backtestResult.equity_curve?.length > 0 && (
                        <div>
                          <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1"><TrendingUp className="w-3 h-3" /> Equity Curve</p>
                          <div className="h-28 flex items-end gap-[2px]">
                            {backtestResult.equity_curve.map((pt, i) => {
                              const vals = backtestResult.equity_curve.map(p => p.value);
                              const mn = Math.min(...vals);
                              const mx = Math.max(...vals);
                              const pct = mx > mn ? ((pt.value - mn) / (mx - mn)) * 100 : 50;
                              return (
                                <div key={i} className="flex-1 rounded-t bg-[#00FF94]/50 hover:bg-[#00FF94]/70 transition-colors" style={{ height: `${Math.max(pct, 3)}%` }} title={`$${Math.round(pt.value).toLocaleString()}`} />
                              );
                            })}
                          </div>
                        </div>
                      )}

                      <div className="flex items-center justify-between text-xs text-zinc-600">
                        <span>Period: {backtestResult.period} | Trades: {backtestResult.total_trades}{backtestResult.profit_factor ? ` | PF: ${backtestResult.profit_factor}` : ""}</span>
                        <span>Capital: ${backtestResult.initial_capital?.toLocaleString()} → ${backtestResult.final_capital?.toLocaleString()}</span>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Generated Strategy Result */}
            <AnimatePresence>
              {genResult && (
                <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mb-8">
                  <Card className="bg-[#0A0A0A] border-[#00FF94]/30" data-testid="generated-strategy">
                    <CardHeader className="pb-3 border-b border-zinc-800/50">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium flex items-center gap-2"><Sparkles className="w-4 h-4 text-[#00FF94]" /> Generated: {genResult.name}</CardTitle>
                        <button onClick={() => setGenResult(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                      </div>
                    </CardHeader>
                    <CardContent className="p-5">
                      <p className="text-sm text-zinc-400 mb-3">{genResult.description}</p>
                      <div className="flex flex-wrap gap-2 mb-3">
                        <Badge className="bg-zinc-800 text-zinc-300">Type: {genResult.type}</Badge>
                        {genResult.parameters && Object.entries(genResult.parameters).map(([k, v]) => (
                          <Badge key={k} className="bg-zinc-800 text-zinc-400 font-mono">{k}: {v}</Badge>
                        ))}
                      </div>
                      <Button size="sm" onClick={() => runBacktest(genResult.id)} disabled={!!backtesting} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white text-xs" data-testid="backtest-generated">
                        <Play className="w-3 h-3 mr-1" /> Backtest This Strategy
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Generate New Strategy */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50 border-dashed">
                <CardContent className="p-6 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-300 mb-1">Generate New Strategy</h3>
                    <p className="text-xs text-zinc-600 mb-2">AI will analyze market conditions and create an optimized trading strategy</p>
                    <div className="flex gap-2">
                      {["momentum", "mean_reversion", "arbitrage", "yield", "funding"].map(t => (
                        <button key={t} onClick={() => setSelectedType(t)} className={`px-2.5 py-1 rounded-full text-[10px] font-medium transition-all ${selectedType === t ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-500 hover:bg-zinc-700"}`} data-testid={`type-${t}`}>{t.replace("_", " ")}</button>
                      ))}
                    </div>
                  </div>
                  <Button onClick={generateStrategy} disabled={generating} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white border border-[#7B61FF]/30" data-testid="generate-strategy-btn">
                    {generating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Sparkles className="w-4 h-4 mr-2" />} Generate Strategy
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
};

export default StrategyLabPage;
