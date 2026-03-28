import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  ArrowUpRight, Sparkles, RefreshCw, Trophy, TestTube,
  Beaker, Rocket, StopCircle, FileCode
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import { API } from "../lib/constants";
import { formatCurrency } from "../lib/formatters";

const StrategyLabPage = () => {
  const [strategies, setStrategies] = useState([]);
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generateType, setGenerateType] = useState('momentum');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/lab/strategies`),
      axios.get(`${API}/lab/rankings`)
    ]).then(([strategiesRes, rankingsRes]) => {
      setStrategies(strategiesRes.data);
      setRankings(rankingsRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const generateStrategy = async () => {
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/lab/strategies/generate`, { strategy_type: generateType, risk_level: 'medium' });
      toast.success(`Strategy "${res.data.strategy.name}" generated!`);
      setStrategies([res.data.strategy, ...strategies]);
    } catch (error) { toast.error("Generation failed"); }
    setGenerating(false);
  };

  const backtestStrategy = async (strategyId) => {
    try {
      const res = await axios.post(`${API}/lab/strategies/${strategyId}/backtest`, { strategy_id: strategyId, initial_capital: 10000 });
      toast.success(`Backtest complete! Return: ${res.data.results.total_return}%`);
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'backtested', ...res.data.results } : s));
    } catch (error) { toast.error("Backtest failed"); }
  };

  const startSandbox = async (strategyId) => {
    try {
      await axios.post(`${API}/lab/strategies/${strategyId}/sandbox`);
      toast.success("Sandbox testing started!");
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'sandbox' } : s));
    } catch (error) { toast.error("Sandbox start failed"); }
  };

  const deployStrategy = async (strategyId) => {
    try {
      await axios.post(`${API}/lab/strategies/${strategyId}/deploy`, null, { params: { capital: 10000 } });
      toast.success("Strategy deployed live!");
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'live', is_active: true } : s));
    } catch (error) { toast.error(error.response?.data?.detail || "Deployment failed"); }
  };

  const stopStrategy = async (strategyId) => {
    try {
      await axios.post(`${API}/lab/strategies/${strategyId}/stop`);
      toast.success("Strategy stopped");
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'stopped', is_active: false } : s));
    } catch (error) { toast.error("Stop failed"); }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'bg-[#00FF94]/20 text-[#00FF94]';
      case 'sandbox': return 'bg-[#FFB800]/20 text-[#FFB800]';
      case 'backtested': return 'bg-[#7B61FF]/20 text-[#7B61FF]';
      case 'generated': return 'bg-zinc-700 text-zinc-400';
      default: return 'bg-zinc-700 text-zinc-400';
    }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="lab-title">AI Strategy Lab</h1>
            <p className="text-zinc-400 mt-1">Autonomous strategy generation, testing, and deployment</p>
          </div>
          <div className="flex gap-3">
            <Select value={generateType} onValueChange={setGenerateType}>
              <SelectTrigger className="w-[160px] bg-[#050505] border-zinc-800" data-testid="generate-type-select"><SelectValue /></SelectTrigger>
              <SelectContent className="bg-[#121212] border-zinc-800">
                <SelectItem value="momentum">Momentum</SelectItem>
                <SelectItem value="arbitrage">Arbitrage</SelectItem>
                <SelectItem value="yield">DeFi Yield</SelectItem>
                <SelectItem value="mean_reversion">Mean Reversion</SelectItem>
                <SelectItem value="funding">Funding Rate</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={generateStrategy} disabled={generating} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="generate-strategy-btn">
              {generating ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
              Generate Strategy
            </Button>
          </div>
        </div>

        {/* Strategy Pipeline */}
        <Card className="glass-card mb-8" data-testid="strategy-pipeline">
          <CardHeader><CardTitle>Strategy Pipeline</CardTitle><CardDescription>Strategies progress through: Generated → Backtested → Sandbox → Live</CardDescription></CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4 text-center">
              {['generated', 'backtested', 'sandbox', 'live'].map((stage, i) => {
                const count = strategies.filter(s => s.status === stage).length;
                return (
                  <div key={stage} className="p-4 rounded-xl bg-[#050505] border border-zinc-800">
                    <p className="text-2xl font-bold font-['JetBrains_Mono']">{count}</p>
                    <p className="text-sm text-zinc-500 capitalize">{stage}</p>
                    {i < 3 && <ArrowUpRight className="w-4 h-4 mx-auto mt-2 text-zinc-600" />}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Rankings Table */}
        <Card className="glass-card mb-8" data-testid="strategy-rankings">
          <CardHeader><CardTitle className="flex items-center gap-2"><Trophy className="w-5 h-5 text-[#FFB800]" />Strategy Rankings</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-zinc-800">
                    <th className="text-left p-3 text-zinc-500">Rank</th>
                    <th className="text-left p-3 text-zinc-500">Strategy</th>
                    <th className="text-left p-3 text-zinc-500">Type</th>
                    <th className="text-left p-3 text-zinc-500">Status</th>
                    <th className="text-right p-3 text-zinc-500">Sharpe</th>
                    <th className="text-right p-3 text-zinc-500">Return</th>
                    <th className="text-right p-3 text-zinc-500">Drawdown</th>
                    <th className="text-right p-3 text-zinc-500">Capital</th>
                  </tr>
                </thead>
                <tbody>
                  {rankings.slice(0, 10).map((s, i) => (
                    <tr key={s.id} className="border-b border-zinc-800/50" data-testid={`ranking-row-${i}`}>
                      <td className="p-3"><Badge variant="outline" className={i < 3 ? 'border-[#FFB800] text-[#FFB800]' : 'border-zinc-700'}>#{s.rank}</Badge></td>
                      <td className="p-3 font-medium">{s.name}</td>
                      <td className="p-3 text-zinc-400 capitalize">{s.type}</td>
                      <td className="p-3"><Badge className={getStatusColor(s.status)}>{s.status}</Badge></td>
                      <td className="p-3 text-right font-mono text-[#7B61FF]">{s.sharpe_ratio?.toFixed(2)}</td>
                      <td className={`p-3 text-right font-mono ${s.total_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{s.total_return >= 0 ? '+' : ''}{s.total_return}%</td>
                      <td className="p-3 text-right font-mono text-red-400">-{s.max_drawdown}%</td>
                      <td className="p-3 text-right font-mono">{formatCurrency(s.capital_allocated)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Strategy Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? Array(6).fill(0).map((_, i) => (<Card key={i} className="glass-card animate-pulse"><CardContent className="p-6 h-[250px]" /></Card>)) : (
            strategies.map((strategy) => (
              <Card key={strategy.id} className="glass-card card-hover" data-testid={`strategy-card-${strategy.id}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-10 h-10 rounded-xl bg-[#7B61FF]/20 flex items-center justify-center">
                      <FileCode className="w-5 h-5 text-[#7B61FF]" />
                    </div>
                    <Badge className={getStatusColor(strategy.status)}>{strategy.status}</Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-1">{strategy.name}</h3>
                  <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{strategy.description}</p>
                  
                  <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                    <div><p className="text-zinc-500">Sharpe</p><p className="font-mono text-[#7B61FF]">{strategy.sharpe_ratio?.toFixed(2) || '—'}</p></div>
                    <div><p className="text-zinc-500">Return</p><p className={`font-mono ${strategy.total_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{strategy.total_return ? `${strategy.total_return >= 0 ? '+' : ''}${strategy.total_return}%` : '—'}</p></div>
                  </div>

                  <div className="flex gap-2">
                    {strategy.status === 'generated' && (
                      <Button size="sm" onClick={() => backtestStrategy(strategy.id)} className="flex-1 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] hover:bg-[#7B61FF]/30" data-testid={`backtest-${strategy.id}`}>
                        <TestTube className="w-3 h-3 mr-1" />Backtest
                      </Button>
                    )}
                    {strategy.status === 'backtested' && (
                      <Button size="sm" onClick={() => startSandbox(strategy.id)} className="flex-1 rounded-full bg-[#FFB800]/20 text-[#FFB800] hover:bg-[#FFB800]/30" data-testid={`sandbox-${strategy.id}`}>
                        <Beaker className="w-3 h-3 mr-1" />Sandbox
                      </Button>
                    )}
                    {strategy.status === 'sandbox' && (
                      <Button size="sm" onClick={() => deployStrategy(strategy.id)} className="flex-1 rounded-full bg-[#00FF94]/20 text-[#00FF94] hover:bg-[#00FF94]/30" data-testid={`deploy-${strategy.id}`}>
                        <Rocket className="w-3 h-3 mr-1" />Deploy
                      </Button>
                    )}
                    {strategy.status === 'live' && (
                      <Button size="sm" onClick={() => stopStrategy(strategy.id)} variant="outline" className="flex-1 rounded-full border-red-500/30 text-red-400 hover:bg-red-500/10" data-testid={`stop-${strategy.id}`}>
                        <StopCircle className="w-3 h-3 mr-1" />Stop
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default StrategyLabPage;
