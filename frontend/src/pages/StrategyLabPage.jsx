import { motion } from "framer-motion";
import { FlaskConical, Sparkles, ArrowUpRight, TrendingUp, Rocket } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockStrategies } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";

const StrategyLabPage = () => {
  const { isDemoMode, demoStrategies } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;

  const { data: apiData, loading, error, refetch } = useApiData('/lab/strategies', { skip: isDemoMode, token });

  const strategies = isDemoMode ? demoStrategies : (apiData?.strategies || apiData || mockStrategies);
  const arr = Array.isArray(strategies) ? strategies : [];

  const countByStatus = (s) => arr.filter(x => x.status === s).length;
  const stats = [
    { label: 'Generated', value: String(countByStatus('generated') || arr.length), change: 'Strategies', positive: true },
    { label: 'Backtested', value: String(countByStatus('backtested')), change: 'Passed QA', positive: true },
    { label: 'In Sandbox', value: String(countByStatus('sandbox')), change: 'Paper testing', positive: true },
    { label: 'Live', value: String(countByStatus('live')), change: 'Ready to deploy', positive: true },
  ];

  const statusColors = { generated: 'bg-zinc-600/15 text-zinc-400', backtested: 'bg-[#7B61FF]/15 text-[#7B61FF]', sandbox: 'bg-[#FFB800]/15 text-[#FFB800]', live: 'bg-[#00FF94]/15 text-[#00FF94]' };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="strategy-lab-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader icon={FlaskConical} title="Strategy Lab" description="AI-generated strategies, backtesting, and autonomous deployment pipeline" testId="strategy-lab-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load strategies" onRetry={refetch} /> : (
          <>
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-5">
                  <p className="text-xs text-zinc-500 mb-4 uppercase tracking-wider">Strategy Pipeline</p>
                  <div className="flex items-center gap-2">
                    {['Generated', 'Backtested', 'Sandbox', 'Live'].map((stage, i) => (
                      <div key={i} className="flex items-center gap-2 flex-1">
                        <div className={`flex-1 h-2 rounded-full ${i < 2 ? 'bg-[#7B61FF]' : i === 2 ? 'bg-[#FFB800]/40' : 'bg-zinc-800'}`} />
                        {i < 3 && <ArrowUpRight className="w-3 h-3 text-zinc-600 shrink-0" />}
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-between mt-2 text-[10px] text-zinc-600 font-mono">
                    <span>Generated ({countByStatus('generated') || arr.length})</span><span>Backtested ({countByStatus('backtested')})</span><span>Sandbox ({countByStatus('sandbox')})</span><span>Live ({countByStatus('live')})</span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <StatsRow stats={stats} />

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-3"><CardTitle className="text-sm font-medium flex items-center gap-2"><TrendingUp className="w-4 h-4 text-[#00FF94]" /> Strategy Rankings</CardTitle></CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead><tr className="border-b border-zinc-800/50">{['Strategy', 'Type', 'Status', 'Sharpe', 'Return', 'Drawdown', 'Capital'].map(h => (<th key={h} className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">{h}</th>))}</tr></thead>
                      <tbody className="divide-y divide-zinc-800/30">
                        {arr.map((s, i) => (
                          <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                            <td className="px-4 py-4 text-sm font-medium text-zinc-200">{s.name}</td>
                            <td className="px-4 py-4 text-xs text-zinc-500">{s.type}</td>
                            <td className="px-4 py-4"><Badge className={statusColors[s.status] || 'bg-zinc-600/15 text-zinc-400'}>{s.status}</Badge></td>
                            <td className="px-4 py-4 text-sm font-mono text-zinc-300">{s.sharpe}</td>
                            <td className="px-4 py-4 text-sm font-mono text-[#00FF94]">{s.returnPct || s.return_pct || '--'}</td>
                            <td className="px-4 py-4 text-sm font-mono text-red-400">{s.drawdown || '--'}</td>
                            <td className="px-4 py-4 text-sm font-mono text-zinc-400">{s.capital || '--'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50 border-dashed">
                <CardContent className="p-6 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-300 mb-1">Generate New Strategy</h3>
                    <p className="text-xs text-zinc-600">AI will analyze market conditions and create an optimized trading strategy</p>
                  </div>
                  <Button disabled className="rounded-full bg-[#7B61FF]/20 text-[#7B61FF]/60 border border-[#7B61FF]/10"><Sparkles className="w-4 h-4 mr-2" /> Generate Strategy</Button>
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
