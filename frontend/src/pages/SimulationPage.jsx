import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Activity, AlertTriangle, ArrowUpRight, BarChart3, Bot,
  ChevronDown, CircleDot, Cpu, FileCode, Gauge,
  Play, Radio, RefreshCw, Rocket, Scale, ScrollText,
  Shield, Sparkles, StopCircle, Target, Terminal, TrendingUp, Zap
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Progress } from "../components/ui/progress";
import { ScrollArea } from "../components/ui/scroll-area";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from "../components/ui/dropdown-menu";
import { API } from "../lib/constants";
import { formatCurrency } from "../lib/formatters";

const SimulationPage = () => {
  const [simConfig, setSimConfig] = useState(null);
  const [simStats, setSimStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [cycleRunning, setCycleRunning] = useState(false);
  const [dailyReport, setDailyReport] = useState(null);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [activeTab, setActiveTab] = useState("control");
  
  // Enhanced simulation state
  const [acceleratedRunning, setAcceleratedRunning] = useState(false);
  const [stressTestRunning, setStressTestRunning] = useState(false);
  const [acceleratedResults, setAcceleratedResults] = useState(null);
  const [stressTestResults, setStressTestResults] = useState(null);
  const [agentPerformance, setAgentPerformance] = useState([]);
  const [daysToSimulate, setDaysToSimulate] = useState(30);

  const fetchData = async () => {
    try {
      const [configRes, statsRes, logsRes, interactionsRes] = await Promise.all([
        axios.get(`${API}/simulation/config`),
        axios.get(`${API}/simulation/stats`),
        axios.get(`${API}/simulation/logs?limit=30`),
        axios.get(`${API}/simulation/agent-interactions?limit=20`)
      ]);
      setSimConfig(configRes.data);
      setSimStats(statsRes.data);
      setLogs(logsRes.data);
      setInteractions(interactionsRes.data);
      setRunning(configRes.data?.is_running || false);
    } catch (error) {
      console.error("Error fetching simulation data:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const startSimulation = async () => {
    try {
      const res = await axios.post(`${API}/simulation/start`);
      toast.success(res.data.message);
      setRunning(true);
      fetchData();
    } catch (error) {
      toast.error("Failed to start simulation");
    }
  };

  const stopSimulation = async () => {
    try {
      const res = await axios.post(`${API}/simulation/stop`);
      toast.success(res.data.message);
      setRunning(false);
      fetchData();
    } catch (error) {
      toast.error("Failed to stop simulation");
    }
  };

  const runCycle = async () => {
    setCycleRunning(true);
    try {
      const res = await axios.post(`${API}/simulation/run-cycle`);
      toast.success(`Cycle complete! ${res.data.cycle_results?.length || 0} trades executed`);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.message || "Cycle failed");
    }
    setCycleRunning(false);
  };

  const autoDeployTop = async () => {
    try {
      const res = await axios.post(`${API}/lab/auto-deploy-top`);
      toast.success(res.data.message);
      fetchData();
    } catch (error) {
      toast.error("Auto-deploy failed");
    }
  };

  const rebalanceCapital = async () => {
    try {
      await axios.post(`${API}/capital/rebalance`);
      toast.success("Capital rebalanced!");
      fetchData();
    } catch (error) {
      toast.error("Rebalance failed");
    }
  };

  const generateDailyReport = async () => {
    try {
      const res = await axios.get(`${API}/reports/daily`);
      setDailyReport(res.data);
      toast.success("Daily report generated!");
    } catch (error) {
      toast.error("Report generation failed");
    }
  };

  const generateWeeklyReport = async () => {
    try {
      const res = await axios.get(`${API}/reports/weekly`);
      setWeeklyReport(res.data);
      toast.success("Weekly report generated!");
    } catch (error) {
      toast.error("Report generation failed");
    }
  };

  const switchMode = async (newMode) => {
    try {
      const res = await axios.post(`${API}/simulation/switch-mode?mode=${newMode}&live_capital=1000`);
      toast.success(res.data.message);
      if (res.data.warning) toast.warning(res.data.warning);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Mode switch failed");
    }
  };

  const addStrategies = async () => {
    try {
      const res = await axios.post(`${API}/strategies/add-batch?count=3`);
      toast.success(res.data.message);
      fetchData();
    } catch (error) {
      toast.error("Failed to add strategies");
    }
  };

  // Enhanced simulation functions
  const runAcceleratedSimulation = async () => {
    setAcceleratedRunning(true);
    try {
      // First configure with 100x speed
      await axios.post(`${API}/simulation/configure`, {
        time_acceleration: 100,
        start_date: "2025-01-01",
        end_date: "2025-12-31",
        initial_capital: 100000,
        stress_test_enabled: true
      });
      
      // Load historical data
      await axios.post(`${API}/simulation/load-historical-data?use_sample=true`);
      
      // Run accelerated simulation
      const res = await axios.post(`${API}/simulation/run-accelerated?days_to_simulate=${daysToSimulate}`);
      setAcceleratedResults(res.data);
      toast.success(`Simulated ${daysToSimulate} days at 100x speed!`);
      fetchData();
      
      // Fetch agent performance
      const perfRes = await axios.get(`${API}/simulation/agent-performance`);
      setAgentPerformance(perfRes.data.agents || []);
    } catch (error) {
      toast.error("Accelerated simulation failed");
      console.error(error);
    }
    setAcceleratedRunning(false);
  };

  const runStressTest = async (scenario) => {
    setStressTestRunning(true);
    try {
      const res = await axios.post(`${API}/simulation/stress-test?scenario_name=${encodeURIComponent(scenario)}`);
      setStressTestResults(res.data);
      toast.success(`Stress test complete: ${res.data.results?.survival_status}`);
      fetchData();
    } catch (error) {
      toast.error("Stress test failed");
    }
    setStressTestRunning(false);
  };

  const exportResults = async () => {
    try {
      const res = await axios.post(`${API}/simulation/export`, {
        formats: ["pdf", "csv"],
        include_trades: true,
        include_agent_performance: true
      });
      toast.success("Results exported successfully!");
    } catch (error) {
      toast.error("Export failed");
    }
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'trade': return Activity;
      case 'risk': return AlertTriangle;
      case 'allocation': return Scale;
      case 'strategy': return Target;
      case 'agent': return Bot;
      default: return Terminal;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'trade': return '#00FF94';
      case 'risk': return '#FF6B6B';
      case 'allocation': return '#7B61FF';
      case 'strategy': return '#FFB800';
      case 'agent': return '#00D4FF';
      default: return '#71717A';
    }
  };

  if (loading) return <div className="min-h-screen pt-24 px-4 flex items-center justify-center"><RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" /></div>;

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="simulation-title">MVP Simulation Control</h1>
            <p className="text-zinc-400 mt-1">Paper trading mode with full agent coordination</p>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={running ? 'bg-[#00FF94]/20 text-[#00FF94] animate-pulse' : 'bg-zinc-700 text-zinc-400'} data-testid="simulation-status">
              <CircleDot className="w-3 h-3 mr-1" />
              {running ? 'RUNNING' : 'STOPPED'}
            </Badge>
            {!running ? (
              <Button onClick={startSimulation} className="rounded-full bg-[#00FF94] text-black hover:bg-[#00FF94]/90" data-testid="start-simulation-btn">
                <Play className="w-4 h-4 mr-2" />Start Simulation
              </Button>
            ) : (
              <Button onClick={stopSimulation} variant="outline" className="rounded-full border-red-500/50 text-red-400 hover:bg-red-500/10" data-testid="stop-simulation-btn">
                <StopCircle className="w-4 h-4 mr-2" />Stop
              </Button>
            )}
          </div>
        </div>

        {/* Simulation Stats */}
        {simStats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
            <Card className="glass-card" data-testid="sim-capital">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Current Capital</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{formatCurrency(simStats.simulation?.current_capital || 10000)}</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-return">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Total Return</p>
                <p className={`text-xl font-bold font-['JetBrains_Mono'] ${simStats.simulation?.total_return_percent >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                  {simStats.simulation?.total_return_percent >= 0 ? '+' : ''}{simStats.simulation?.total_return_percent?.toFixed(2)}%
                </p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-trades">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Total Trades</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{simStats.trading?.total_trades || 0}</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-winrate">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Win Rate</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{simStats.trading?.win_rate?.toFixed(1) || 0}%</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-strategies">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Active Strategies</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{simStats.strategies?.active || 0}</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-risk-events">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Risk Events</p>
                <p className="text-xl font-bold font-['JetBrains_Mono'] text-[#FFB800]">{simStats.risk?.events_triggered || 0}</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Control Panel */}
        <Card className="glass-card mb-8 border-[#7B61FF]/30" data-testid="control-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Cpu className="w-5 h-5 text-[#7B61FF]" />Control Panel</CardTitle>
            <CardDescription>Execute simulation cycles, manage agents, and generate reports</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3 mb-4">
              <Button onClick={runCycle} disabled={!running || cycleRunning} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="run-cycle-btn">
                {cycleRunning ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                Run Trade Cycle
              </Button>
              <Button onClick={autoDeployTop} variant="outline" className="rounded-full border-[#00FF94]/50 text-[#00FF94] hover:bg-[#00FF94]/10" data-testid="auto-deploy-btn">
                <Rocket className="w-4 h-4 mr-2" />Auto-Deploy Top
              </Button>
              <Button onClick={addStrategies} variant="outline" className="rounded-full border-[#FFB800]/50 text-[#FFB800] hover:bg-[#FFB800]/10" data-testid="add-strategies-btn">
                <Sparkles className="w-4 h-4 mr-2" />Add New Strategies
              </Button>
              <Button onClick={rebalanceCapital} variant="outline" className="rounded-full border-zinc-700" data-testid="rebalance-capital-btn">
                <Scale className="w-4 h-4 mr-2" />Rebalance
              </Button>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button onClick={generateDailyReport} variant="outline" className="rounded-full border-zinc-700" data-testid="daily-report-btn">
                <FileCode className="w-4 h-4 mr-2" />Daily Report
              </Button>
              <Button onClick={generateWeeklyReport} variant="outline" className="rounded-full border-zinc-700" data-testid="weekly-report-btn">
                <ScrollText className="w-4 h-4 mr-2" />Weekly Report
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="rounded-full border-zinc-700" data-testid="mode-switch-btn">
                    <Radio className="w-4 h-4 mr-2" />
                    Mode: {simStats?.simulation?.mode?.toUpperCase() || 'PAPER'}
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="bg-[#121212] border-zinc-800">
                  <DropdownMenuItem onClick={() => switchMode('paper')} className={simStats?.simulation?.mode === 'paper' ? 'text-[#00FF94]' : ''}>
                    Paper Trading
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => switchMode('testnet')} className={simStats?.simulation?.mode === 'testnet' ? 'text-[#FFB800]' : ''}>
                    Testnet
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => switchMode('live')} className="text-red-400">
                    Live Trading ($1000)
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Simulation Panel */}
        <Card className="glass-card mb-8 border-[#FFB800]/30" data-testid="enhanced-simulation-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Gauge className="w-5 h-5 text-[#FFB800]" />Accelerated Simulation & Stress Testing</CardTitle>
            <CardDescription>Run 100x time-accelerated backtests and stress test scenarios</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Accelerated Simulation */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-[#FFB800]" />100x Time Acceleration
                </h3>
                <div className="flex items-center gap-3 mb-4">
                  <Input 
                    type="number" 
                    value={daysToSimulate} 
                    onChange={(e) => setDaysToSimulate(Number(e.target.value))}
                    className="w-24 bg-[#121212] border-zinc-700"
                    min={1}
                    max={365}
                  />
                  <span className="text-zinc-400">days to simulate</span>
                </div>
                <Button 
                  onClick={runAcceleratedSimulation} 
                  disabled={acceleratedRunning}
                  className="w-full rounded-full bg-[#FFB800] text-black hover:bg-[#FFB800]/90"
                  data-testid="run-accelerated-btn"
                >
                  {acceleratedRunning ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Rocket className="w-4 h-4 mr-2" />}
                  {acceleratedRunning ? 'Simulating...' : 'Run Accelerated Backtest'}
                </Button>
                
                {acceleratedResults && (
                  <div className="mt-4 p-3 rounded-lg bg-[#121212] border border-[#FFB800]/30">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-zinc-500">Days Simulated</p>
                        <p className="font-mono font-bold">{acceleratedResults.summary?.days_simulated}</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Total Trades</p>
                        <p className="font-mono font-bold">{acceleratedResults.summary?.total_trades}</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Final Capital</p>
                        <p className="font-mono font-bold text-[#00FF94]">${acceleratedResults.summary?.final_capital?.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Total Return</p>
                        <p className={`font-mono font-bold ${acceleratedResults.summary?.total_return_percent >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {acceleratedResults.summary?.total_return_percent >= 0 ? '+' : ''}{acceleratedResults.summary?.total_return_percent?.toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Win Rate</p>
                        <p className="font-mono font-bold">{acceleratedResults.summary?.win_rate}%</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Best Day P&L</p>
                        <p className="font-mono font-bold text-[#00FF94]">+${acceleratedResults.summary?.best_day?.day_pnl?.toFixed(2)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Stress Testing */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />Stress Test Scenarios
                </h3>
                <div className="space-y-2 mb-4">
                  <Button 
                    onClick={() => runStressTest('High Volatility BTC Drop')}
                    disabled={stressTestRunning}
                    variant="outline"
                    className="w-full justify-start rounded-lg border-zinc-700 hover:border-red-500/50"
                    data-testid="stress-btc-drop-btn"
                  >
                    <TrendingUp className="w-4 h-4 mr-2 text-red-400 rotate-180" />
                    BTC 30% Drop (24h)
                  </Button>
                  <Button 
                    onClick={() => runStressTest('ETH Flash Crash')}
                    disabled={stressTestRunning}
                    variant="outline"
                    className="w-full justify-start rounded-lg border-zinc-700 hover:border-red-500/50"
                    data-testid="stress-eth-crash-btn"
                  >
                    <Zap className="w-4 h-4 mr-2 text-red-400" />
                    ETH Flash Crash 50% (12h)
                  </Button>
                  <Button 
                    onClick={() => runStressTest('Market Panic Sell')}
                    disabled={stressTestRunning}
                    variant="outline"
                    className="w-full justify-start rounded-lg border-zinc-700 hover:border-red-500/50"
                    data-testid="stress-panic-btn"
                  >
                    <Activity className="w-4 h-4 mr-2 text-red-400" />
                    Market Panic Sell 40% (6h)
                  </Button>
                </div>
                
                {stressTestResults && (
                  <div className="p-3 rounded-lg bg-[#121212] border border-red-500/30">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-zinc-400">{stressTestResults.scenario}</span>
                      <Badge className={stressTestResults.results?.survival_status === 'SURVIVED' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                        {stressTestResults.results?.survival_status}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <p className="text-zinc-500">Max Drawdown</p>
                        <p className="font-mono font-bold text-red-400">-{stressTestResults.results?.max_drawdown_percent?.toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Final Capital</p>
                        <p className="font-mono font-bold">${stressTestResults.results?.final_capital?.toLocaleString()}</p>
                      </div>
                    </div>
                    {stressTestResults.results?.risk_actions_taken?.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Risk Actions Triggered:</p>
                        {stressTestResults.results.risk_actions_taken.map((action, i) => (
                          <p key={i} className="text-xs text-[#FFB800]">• {action}</p>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Agent Performance */}
            {agentPerformance.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Bot className="w-5 h-5 text-[#7B61FF]" />Agent Performance
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {agentPerformance.map((agent, i) => (
                    <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                      <p className="text-sm font-medium mb-1">{agent.name}</p>
                      <p className={`text-xl font-bold font-mono ${agent.performance_ytd >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                        {agent.performance_ytd >= 0 ? '+' : ''}{agent.performance_ytd}%
                      </p>
                      <p className="text-xs text-zinc-500">{agent.trades_executed || agent.strategies_deployed || 0} {agent.type === 'sandbox' ? 'strategies' : 'trades'}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Export Button */}
            <div className="mt-6 flex justify-end">
              <Button onClick={exportResults} variant="outline" className="rounded-full border-zinc-700" data-testid="export-results-btn">
                <FileCode className="w-4 h-4 mr-2" />Export Results (PDF/CSV)
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Performance Reports */}
        {(dailyReport || weeklyReport) && (
          <Card className="glass-card mb-8 border-[#00FF94]/30" data-testid="reports-panel">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-[#00FF94]" />Performance Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="daily" className="w-full">
                <TabsList className="bg-[#050505] mb-4">
                  <TabsTrigger value="daily" disabled={!dailyReport}>Daily</TabsTrigger>
                  <TabsTrigger value="weekly" disabled={!weeklyReport}>Weekly</TabsTrigger>
                </TabsList>
                
                {dailyReport && (
                  <TabsContent value="daily">
                    <div className="grid md:grid-cols-3 gap-4 mb-4">
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Daily P&L</p>
                        <p className={`text-2xl font-bold font-['JetBrains_Mono'] ${dailyReport.summary?.daily_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {dailyReport.summary?.daily_pnl >= 0 ? '+' : ''}${dailyReport.summary?.daily_pnl?.toFixed(2)}
                        </p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Win Rate</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{dailyReport.trading?.win_rate?.toFixed(1)}%</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Trades Today</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{dailyReport.trading?.total_trades}</p>
                      </div>
                    </div>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-sm text-zinc-400 mb-2">Best Trade</p>
                        <p className="text-lg font-bold text-[#00FF94] font-['JetBrains_Mono']">+${dailyReport.trading?.best_trade?.toFixed(2)}</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-sm text-zinc-400 mb-2">Worst Trade</p>
                        <p className="text-lg font-bold text-red-400 font-['JetBrains_Mono']">${dailyReport.trading?.worst_trade?.toFixed(2)}</p>
                      </div>
                    </div>
                  </TabsContent>
                )}
                
                {weeklyReport && (
                  <TabsContent value="weekly">
                    <div className="grid md:grid-cols-4 gap-4 mb-4">
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Weekly P&L</p>
                        <p className={`text-2xl font-bold font-['JetBrains_Mono'] ${weeklyReport.summary?.weekly_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {weeklyReport.summary?.weekly_pnl >= 0 ? '+' : ''}${weeklyReport.summary?.weekly_pnl?.toFixed(2)}
                        </p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Sharpe Ratio</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#7B61FF]">{weeklyReport.summary?.sharpe_ratio}</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Win Rate</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{weeklyReport.trading?.win_rate?.toFixed(1)}%</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Total Trades</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{weeklyReport.trading?.total_trades}</p>
                      </div>
                    </div>
                    <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                      <p className="text-sm text-zinc-400 mb-3">Daily Breakdown</p>
                      <div className="flex gap-2">
                        {weeklyReport.trading?.daily_breakdown?.slice(0, 7).map((day, i) => (
                          <div key={i} className="flex-1 text-center p-2 rounded bg-[#121212]">
                            <p className="text-xs text-zinc-500">{day.date?.slice(5)}</p>
                            <p className={`text-sm font-mono ${day.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                              {day.pnl >= 0 ? '+' : ''}{day.pnl}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                )}
              </Tabs>
            </CardContent>
          </Card>
        )}

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Simulation Logs */}
          <Card className="glass-card" data-testid="simulation-logs">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ScrollText className="w-5 h-5 text-[#00FF94]" />Simulation Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-2">
                  {logs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No logs yet. Start the simulation!</p>
                  ) : logs.map((log, i) => {
                    const Icon = getLogIcon(log.log_type);
                    const color = getLogColor(log.log_type);
                    return (
                      <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`log-${i}`}>
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ backgroundColor: `${color}20` }}>
                          <Icon className="w-4 h-4" style={{ color }} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs" style={{ borderColor: color, color }}>{log.log_type}</Badge>
                            {log.agent_name && <span className="text-xs text-zinc-500">{log.agent_name}</span>}
                          </div>
                          <p className="text-sm text-zinc-300 break-words">{log.message}</p>
                          <p className="text-xs text-zinc-600 mt-1">{new Date(log.timestamp).toLocaleTimeString()}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Agent Interactions */}
          <Card className="glass-card" data-testid="agent-interactions">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Bot className="w-5 h-5 text-[#7B61FF]" />Agent Interactions</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-2">
                  {interactions.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No interactions yet</p>
                  ) : interactions.map((interaction, i) => (
                    <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`interaction-${i}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-xs">{interaction.from_agent}</Badge>
                        <ArrowUpRight className="w-3 h-3 text-zinc-500" />
                        <Badge className="bg-[#00FF94]/20 text-[#00FF94] text-xs">{interaction.to_agent}</Badge>
                      </div>
                      <p className="text-xs text-zinc-400">
                        <span className="text-[#FFB800]">{interaction.interaction_type}</span>: {JSON.stringify(interaction.payload).slice(0, 80)}...
                      </p>
                      <p className="text-xs text-zinc-600 mt-1">{new Date(interaction.timestamp).toLocaleTimeString()}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Risk & Strategy Status */}
        <div className="grid lg:grid-cols-2 gap-6">
          <Card className="glass-card" data-testid="risk-status">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Shield className="w-5 h-5 text-[#FF6B6B]" />Risk Engine Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-zinc-400">Current Drawdown</span>
                    <span className={simStats?.risk?.current_drawdown > 4 ? 'text-red-400' : 'text-[#00FF94]'}>
                      {simStats?.risk?.current_drawdown?.toFixed(2) || 0}%
                    </span>
                  </div>
                  <Progress value={(simStats?.risk?.current_drawdown || 0) * 20} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-zinc-400">Daily P&L</span>
                    <span className={simStats?.risk?.daily_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}>
                      {simStats?.risk?.daily_pnl >= 0 ? '+' : ''}{simStats?.risk?.daily_pnl?.toFixed(2) || 0}%
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505]">
                  <span className="text-sm text-zinc-400">Auto-Stop Enabled</span>
                  <Badge className="bg-[#00FF94]/20 text-[#00FF94]">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505]">
                  <span className="text-sm text-zinc-400">Active Alerts</span>
                  <Badge className="bg-[#FFB800]/20 text-[#FFB800]">{simStats?.risk?.active_alerts || 0}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="strategy-status">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Target className="w-5 h-5 text-[#FFB800]" />Strategy Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-[#00FF94]">{simStats?.strategies?.live || 0}</p>
                  <p className="text-xs text-zinc-500">Live</p>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-[#FFB800]">{simStats?.strategies?.in_sandbox || 0}</p>
                  <p className="text-xs text-zinc-500">In Sandbox</p>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-zinc-400">{simStats?.strategies?.total || 0}</p>
                  <p className="text-xs text-zinc-500">Total</p>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-[#7B61FF]">{simStats?.strategies?.active || 0}</p>
                  <p className="text-xs text-zinc-500">Active</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Referral Page

export default SimulationPage;
