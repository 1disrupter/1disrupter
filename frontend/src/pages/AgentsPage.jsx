import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Activity, Brain, Target, Zap, Shield, Bot, Split,
  ArrowUpRight, ArrowDownRight, Sparkles, RefreshCw
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { ScrollArea } from "../components/ui/scroll-area";
import { Progress } from "../components/ui/progress";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import { API } from "../lib/constants";

const AgentsPage = () => {
  const [agents, setAgents] = useState([]);
  const [trades, setTrades] = useState([]);
  const [riskStatus, setRiskStatus] = useState(null);
  const [executionStats, setExecutionStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('bitcoin');

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/agents`),
      axios.get(`${API}/trades?limit=10`),
      axios.get(`${API}/risk/portfolio-status`),
      axios.get(`${API}/execution/stats`)
    ]).then(([agentsRes, tradesRes, riskRes, execRes]) => {
      setAgents(agentsRes.data);
      setTrades(tradesRes.data);
      setRiskStatus(riskRes.data);
      setExecutionStats(execRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const runAIAnalysis = async () => {
    setAnalysisLoading(true);
    try {
      const response = await axios.post(`${API}/ai/analyze`, { symbol: selectedSymbol, timeframe: "1d" });
      setAnalysisResult(response.data);
      toast.success("AI Analysis complete!");
    } catch (error) { toast.error("Analysis failed"); }
    setAnalysisLoading(false);
  };

  const getAgentIcon = (type) => ({ data: Activity, analysis: Brain, strategy: Target, execution: Zap, risk: Shield }[type] || Bot);
  const getAgentColor = (type) => ({ data: '#00FF94', analysis: '#7B61FF', strategy: '#FF6B6B', execution: '#FFB800', risk: '#00D4FF' }[type] || '#7B61FF');

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="agents-title">AI Trading Agents</h1>
          <p className="text-zinc-400 mt-1">Monitor and manage autonomous trading agents</p>
        </div>

        {/* Risk & Execution Stats */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {riskStatus && (
            <Card className="glass-card" data-testid="risk-status-card">
              <CardHeader><CardTitle className="flex items-center gap-2"><Shield className="w-5 h-5 text-[#00D4FF]" />Risk Status</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1"><span className="text-zinc-400">Drawdown</span><span className={riskStatus.current_drawdown > 4 ? 'text-red-400' : 'text-[#00FF94]'}>{riskStatus.current_drawdown}% / {riskStatus.max_drawdown_limit}%</span></div>
                    <Progress value={riskStatus.drawdown_utilization} className="h-2" />
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div><p className="text-sm text-zinc-500">Daily P&L</p><p className={`font-mono ${riskStatus.daily_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{riskStatus.daily_pnl >= 0 ? '+' : ''}{riskStatus.daily_pnl}%</p></div>
                    <div><p className="text-sm text-zinc-500">Risk Level</p><Badge className={riskStatus.risk_level === 'high' ? 'bg-red-500/20 text-red-400' : riskStatus.risk_level === 'medium' ? 'bg-[#FFB800]/20 text-[#FFB800]' : 'bg-[#00FF94]/20 text-[#00FF94]'}>{riskStatus.risk_level}</Badge></div>
                    <div><p className="text-sm text-zinc-500">Stop Losses</p><p className="font-mono">{riskStatus.active_stop_losses}</p></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {executionStats && (
            <Card className="glass-card" data-testid="execution-stats-card">
              <CardHeader><CardTitle className="flex items-center gap-2"><Split className="w-5 h-5 text-[#FFB800]" />Execution Optimization</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div><p className="text-sm text-zinc-500">Orders Today</p><p className="text-xl font-bold font-mono">{executionStats.total_orders_today}</p></div>
                  <div><p className="text-sm text-zinc-500">Avg Slippage</p><p className="text-xl font-bold font-mono text-[#00FF94]">{executionStats.avg_slippage}%</p></div>
                  <div><p className="text-sm text-zinc-500">Avg Gas Fee</p><p className="text-xl font-bold font-mono">${executionStats.avg_gas_fee}</p></div>
                  <div><p className="text-sm text-zinc-500">Best Price Rate</p><p className="text-xl font-bold font-mono text-[#7B61FF]">{executionStats.best_price_achieved}%</p></div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* AI Analysis */}
        <Card className="glass-card mb-8" data-testid="ai-analysis-section">
          <CardHeader><CardTitle className="flex items-center gap-2"><Sparkles className="w-5 h-5 text-[#7B61FF]" />AI Market Analysis</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-4">
              <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                <SelectTrigger className="w-full md:w-[200px] bg-[#050505] border-zinc-800" data-testid="analysis-symbol-select"><SelectValue placeholder="Select coin" /></SelectTrigger>
                <SelectContent className="bg-[#121212] border-zinc-800">
                  <SelectItem value="bitcoin">Bitcoin (BTC)</SelectItem>
                  <SelectItem value="ethereum">Ethereum (ETH)</SelectItem>
                  <SelectItem value="solana">Solana (SOL)</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={runAIAnalysis} disabled={analysisLoading} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="run-analysis-btn">
                {analysisLoading ? <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Analyzing...</> : <><Brain className="w-4 h-4 mr-2" />Run Analysis</>}
              </Button>
            </div>
            {analysisResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-6 p-4 rounded-xl bg-[#050505] border border-zinc-800" data-testid="analysis-result">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Badge className="bg-[#7B61FF]/20 text-[#7B61FF]">{analysisResult.symbol}</Badge>
                    <span className="font-mono text-lg">${analysisResult.price?.toLocaleString()}</span>
                    <span className={`text-sm ${analysisResult.change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{analysisResult.change_24h >= 0 ? '+' : ''}{analysisResult.change_24h?.toFixed(2)}%</span>
                  </div>
                </div>
                <p className="text-zinc-300 whitespace-pre-wrap">{analysisResult.analysis}</p>
              </motion.div>
            )}
          </CardContent>
        </Card>

        {/* Agents Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {loading ? Array(5).fill(0).map((_, i) => (<Card key={i} className="glass-card animate-pulse"><CardContent className="p-6 h-[200px]" /></Card>)) : agents.map((agent) => {
            const Icon = getAgentIcon(agent.type);
            const color = getAgentColor(agent.type);
            return (
              <Card key={agent.id} className="glass-card card-hover" data-testid={`agent-card-${agent.name}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}20` }}><Icon className="w-6 h-6" style={{ color }} /></div>
                    <Badge className={agent.status === 'active' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-zinc-700 text-zinc-400'}>{agent.status}</Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-1">{agent.name}</h3>
                  <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{agent.description}</p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div><p className="text-zinc-500">7D Perf</p><p className={`font-mono ${agent.performance_7d >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{agent.performance_7d >= 0 ? '+' : ''}{agent.performance_7d}%</p></div>
                    <div><p className="text-zinc-500">Allocation</p><p className="font-mono">{agent.capital_allocation}%</p></div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Recent Trades */}
        <Card className="glass-card" data-testid="recent-trades">
          <CardHeader><CardTitle className="flex items-center gap-2"><Activity className="w-5 h-5 text-[#00FF94]" />Recent Trades</CardTitle></CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              <div className="space-y-3">
                {trades.map((trade) => (
                  <div key={trade.id} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`trade-${trade.id}`}>
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${trade.side === 'buy' ? 'bg-[#00FF94]/20' : 'bg-red-400/20'}`}>
                        {trade.side === 'buy' ? <ArrowUpRight className="w-4 h-4 text-[#00FF94]" /> : <ArrowDownRight className="w-4 h-4 text-red-400" />}
                      </div>
                      <div><p className="font-medium">{trade.symbol}</p><p className="text-xs text-zinc-500">{trade.agent_id}</p></div>
                    </div>
                    <div className="text-right">
                      <p className="font-mono">${trade.price?.toLocaleString()}</p>
                      <p className={`text-xs ${trade.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{trade.pnl >= 0 ? '+' : ''}{trade.pnl?.toFixed(2)} P&L</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AgentsPage;
