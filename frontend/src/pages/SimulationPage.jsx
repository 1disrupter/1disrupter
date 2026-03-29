import { useState } from "react";
import { motion } from "framer-motion";
import {
  Radio, Play, StopCircle, Target, TrendingUp,
  BarChart3, Zap, Clock, Activity
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { PageHeader, StatsRow, MockTable, MiniChart } from "../components/PlaceholderUI";
import { mockSimulationResults, mockChartData } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";

const SimulationPage = () => {
  const { isDemoMode, demoSimulations, demoChart } = useDemoMode();
  const simResults = isDemoMode ? demoSimulations : mockSimulationResults;
  const chartData = isDemoMode ? demoChart : mockChartData;
  const [activeTab, setActiveTab] = useState("overview");

  const stats = [
    { label: 'Total Simulations', value: '24', change: '+3 this week', positive: true },
    { label: 'Avg Win Rate', value: '68.4%', change: '+2.1%', positive: true },
    { label: 'Best Sharpe', value: '2.10', change: 'SOL Breakout', positive: true },
    { label: 'Capital Deployed', value: '$25.0K', change: 'Paper mode', positive: true },
  ];

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

        <StatsRow stats={stats} />

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="bg-[#0A0A0A] border border-zinc-800/50">
            <TabsTrigger value="overview" data-testid="sim-tab-overview">Overview</TabsTrigger>
            <TabsTrigger value="backtest" data-testid="sim-tab-backtest">Backtest</TabsTrigger>
            <TabsTrigger value="paper" data-testid="sim-tab-paper">Paper Trading</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6 space-y-6">
            {/* Recent Simulations Table */}
            <MockTable
              headers={['Pair', 'Strategy', 'Trades', 'Win Rate', 'P&L', 'Sharpe']}
              rows={simResults.map(r => [r.pair, r.strategy, r.trades, r.winRate, r.pnl, r.sharpe])}
            />

            {/* Performance Chart Placeholder */}
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
                      { time: 'Mon', value: 0 }, { time: 'Tue', value: -200 }, { time: 'Wed', value: -450 },
                      { time: 'Thu', value: -180 }, { time: 'Fri', value: -80 }, { time: 'Sat', value: -320 }, { time: 'Sun', value: -50 }
                    ].map(d => ({ ...d, value: 500 + d.value }))} color="#ef4444" />
                    <div className="flex justify-between mt-3 text-xs text-zinc-600 font-mono">
                      <span>Mon</span><span>Wed</span><span>Fri</span><span>Sun</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </TabsContent>

          <TabsContent value="backtest" className="mt-6">
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-8 text-center">
                  <div className="p-4 rounded-2xl bg-[#7B61FF]/5 border border-[#7B61FF]/10 inline-block mb-4">
                    <Target className="w-8 h-8 text-[#7B61FF]/60" />
                  </div>
                  <h3 className="text-lg font-semibold font-['Outfit'] mb-2 text-zinc-300">Configure Backtest</h3>
                  <p className="text-sm text-zinc-600 max-w-md mx-auto mb-5">
                    Select a strategy, time range, and trading pair to begin backtesting against historical data.
                  </p>
                  <Button disabled className="rounded-full bg-[#7B61FF]/20 text-[#7B61FF]/60 border border-[#7B61FF]/10">
                    <Play className="w-4 h-4 mr-2" /> Run Backtest
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          </TabsContent>

          <TabsContent value="paper" className="mt-6">
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
              {/* Active Paper Positions */}
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
                          <Badge className={pos.side === 'LONG' ? 'bg-[#00FF94]/15 text-[#00FF94]' : 'bg-[#ef4444]/15 text-[#ef4444]'}>
                            {pos.side}
                          </Badge>
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
      </div>
    </div>
  );
};

export default SimulationPage;
