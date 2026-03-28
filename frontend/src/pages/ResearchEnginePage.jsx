import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Activity, Beaker, FileCode, LineChart, Play, RefreshCw,
  Rocket, ScrollText, Target
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { API } from "../lib/constants";

const ResearchEnginePage = () => {
  const [running, setRunning] = useState(false);
  const [simResults, setSimResults] = useState(null);
  const [wfResults, setWfResults] = useState(null);
  const [report, setReport] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [targetMonths, setTargetMonths] = useState(6);

  useEffect(() => {
    axios.get(`${API}/research/metrics`).then(res => setMetrics(res.data)).catch(console.error);
  }, []);

  const runSimulation = async () => {
    setRunning(true);
    try {
      const res = await axios.post(`${API}/research/run-simulation?target_months=${targetMonths}&speed_multiplier=500&initial_capital=100000`);
      setSimResults(res.data);
      toast.success(`Simulation complete: ${res.data.metrics?.total_return}% return`);
    } catch (error) {
      toast.error("Simulation failed");
    }
    setRunning(false);
  };

  const runWalkForward = async () => {
    setRunning(true);
    try {
      const res = await axios.post(`${API}/research/walk-forward-test?training_days=90&testing_days=30&num_windows=6`);
      setWfResults(res.data);
      toast.success(`Walk-forward complete: ${res.data.recommendation}`);
    } catch (error) {
      toast.error("Walk-forward test failed");
    }
    setRunning(false);
  };

  const generateReport = async () => {
    try {
      const res = await axios.post(`${API}/research/generate-investor-report`);
      setReport(res.data.report);
      toast.success("Investor report generated!");
    } catch (error) {
      toast.error("Report generation failed");
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 font-['Outfit']">Research Engine</h1>
              <p className="text-zinc-400">500x Accelerated Simulation • Walk-Forward Validation • Investor Reports</p>
            </div>
            <Badge className="bg-[#00FF94]/20 text-[#00FF94]">v1.0</Badge>
          </div>
        </motion.div>

        {/* Control Panel */}
        <Card className="glass-card mb-6 border-[#7B61FF]/30" data-testid="research-control-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Beaker className="w-5 h-5 text-[#7B61FF]" />
              Research Controls
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              {/* Simulation Control */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <Rocket className="w-4 h-4 text-[#FFB800]" />
                  500x Accelerated Simulation
                </h4>
                <div className="flex items-center gap-2 mb-3">
                  <Input 
                    type="number" 
                    value={targetMonths}
                    onChange={e => setTargetMonths(Number(e.target.value))}
                    className="w-20 bg-[#121212] border-zinc-700"
                    min={1}
                    max={12}
                  />
                  <span className="text-sm text-zinc-400">months</span>
                </div>
                <Button 
                  onClick={runSimulation} 
                  disabled={running}
                  className="w-full rounded-full bg-[#FFB800] text-black hover:bg-[#FFB800]/90"
                  data-testid="run-research-sim-btn"
                >
                  {running ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                  Run Simulation
                </Button>
              </div>

              {/* Walk-Forward Control */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-[#00FF94]" />
                  Walk-Forward Validation
                </h4>
                <p className="text-xs text-zinc-500 mb-3">90 days training • 30 days testing • 6 windows</p>
                <Button 
                  onClick={runWalkForward} 
                  disabled={running}
                  className="w-full rounded-full bg-[#00FF94] text-black hover:bg-[#00FF94]/90"
                  data-testid="run-walk-forward-btn"
                >
                  {running ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Target className="w-4 h-4 mr-2" />}
                  Run Walk-Forward
                </Button>
              </div>

              {/* Report Generation */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-[#7B61FF]" />
                  Investor Report
                </h4>
                <p className="text-xs text-zinc-500 mb-3">PDF/JSON • Performance • Risk Metrics</p>
                <Button 
                  onClick={generateReport} 
                  disabled={!simResults}
                  variant="outline"
                  className="w-full rounded-full border-[#7B61FF]/50 text-[#7B61FF]"
                  data-testid="generate-report-btn"
                >
                  <ScrollText className="w-4 h-4 mr-2" />
                  Generate Report
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Grid */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Simulation Results */}
          {simResults && (
            <Card className="glass-card" data-testid="simulation-results">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="w-5 h-5 text-[#FFB800]" />
                  Simulation Results
                </CardTitle>
                <CardDescription>{simResults.summary?.period} at {simResults.summary?.speed}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Total Return</p>
                    <p className={`text-2xl font-bold font-mono ${simResults.metrics?.total_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {simResults.metrics?.total_return >= 0 ? '+' : ''}{simResults.metrics?.total_return}%
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Sharpe Ratio</p>
                    <p className="text-2xl font-bold font-mono text-[#7B61FF]">{simResults.metrics?.sharpe_ratio}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Max Drawdown</p>
                    <p className="text-2xl font-bold font-mono text-red-400">-{simResults.metrics?.max_drawdown}%</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Win Rate</p>
                    <p className="text-2xl font-bold font-mono">{simResults.metrics?.win_rate}%</p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="text-center">
                    <p className="text-zinc-500">Trades</p>
                    <p className="font-mono font-bold">{simResults.metrics?.total_trades}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-zinc-500">Profit Factor</p>
                    <p className="font-mono font-bold">{simResults.metrics?.profit_factor}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-zinc-500">Final Capital</p>
                    <p className="font-mono font-bold text-[#00FF94]">${simResults.summary?.final_capital?.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Walk-Forward Results */}
          {wfResults && (
            <Card className="glass-card" data-testid="walk-forward-results">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-[#00FF94]" />
                    Walk-Forward Validation
                  </CardTitle>
                  <Badge className={wfResults.recommendation === 'ROBUST' ? 'bg-[#00FF94]/20 text-[#00FF94]' : wfResults.recommendation === 'NEEDS_REVIEW' ? 'bg-[#FFB800]/20 text-[#FFB800]' : 'bg-red-400/20 text-red-400'}>
                    {wfResults.recommendation}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Robustness Score</p>
                    <p className="text-2xl font-bold font-mono text-[#00FF94]">{wfResults.summary?.robustness_score}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Profitable Windows</p>
                    <p className="text-2xl font-bold font-mono">{wfResults.summary?.profitable_windows}/6</p>
                  </div>
                </div>
                <ScrollArea className="h-[150px]">
                  <div className="space-y-2">
                    {wfResults.windows?.map((w, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                        <span className="text-sm">Window {w.window_id}</span>
                        <div className="flex items-center gap-4">
                          <span className="text-xs text-zinc-500">Train: {w.training_return}%</span>
                          <span className={`text-xs font-mono ${w.testing_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                            Test: {w.testing_return >= 0 ? '+' : ''}{w.testing_return}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Investor Report Preview */}
        {report && (
          <Card className="glass-card mt-6" data-testid="investor-report-preview">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <ScrollText className="w-5 h-5 text-[#7B61FF]" />
                  Investor Report
                </CardTitle>
                <span className="text-xs text-zinc-500">{new Date(report.generated_at).toLocaleString()}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 rounded-lg bg-gradient-to-br from-[#00FF94]/20 to-transparent border border-[#00FF94]/30 text-center">
                  <p className="text-xs text-zinc-400">Total Return</p>
                  <p className="text-3xl font-bold font-mono text-[#00FF94]">+{report.executive_summary?.total_return}%</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-[#7B61FF]/20 to-transparent border border-[#7B61FF]/30 text-center">
                  <p className="text-xs text-zinc-400">Sharpe Ratio</p>
                  <p className="text-3xl font-bold font-mono text-[#7B61FF]">{report.executive_summary?.sharpe_ratio}</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-red-400/20 to-transparent border border-red-400/30 text-center">
                  <p className="text-xs text-zinc-400">Max Drawdown</p>
                  <p className="text-3xl font-bold font-mono text-red-400">-{report.executive_summary?.max_drawdown}%</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-[#FFB800]/20 to-transparent border border-[#FFB800]/30 text-center">
                  <p className="text-xs text-zinc-400">Win Rate</p>
                  <p className="text-3xl font-bold font-mono text-[#FFB800]">{report.executive_summary?.win_rate}%</p>
                </div>
              </div>
              
              {/* Strategy Breakdown */}
              <h4 className="font-semibold mb-3">Strategy Performance</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {report.strategy_breakdown?.map((s, i) => (
                  <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm font-medium mb-1">{s.name}</p>
                    <p className={`text-lg font-mono font-bold ${s.return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {s.return >= 0 ? '+' : ''}{s.return}%
                    </p>
                    <p className="text-xs text-zinc-500">Sharpe: {s.sharpe}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

// Simulation Control Page

export default ResearchEnginePage;
