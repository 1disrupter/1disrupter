import { motion } from "framer-motion";
import { Bot, Activity, Target, Zap, Shield, Brain, Sparkles } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Progress } from "../components/ui/progress";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockAgents } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";

const AgentsPage = () => {
  const { isDemoMode, demoAgents } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;

  const { data: apiAgents, loading, error, refetch } = useApiData('/agents', { skip: isDemoMode, token });

  const agents = isDemoMode ? demoAgents : (apiAgents?.agents || apiAgents || mockAgents);

  const stats = [
    { label: 'Active Agents', value: String(Array.isArray(agents) ? agents.filter(a => a.status === 'running' || a.status === 'active').length : 0), change: `of ${Array.isArray(agents) ? agents.length : 0} deployed`, positive: true },
    { label: 'Signals Today', value: String(Array.isArray(agents) ? agents.reduce((s, a) => s + (a.signals || 0), 0) : 0), change: 'Combined', positive: true },
    { label: 'Avg Accuracy', value: `${Array.isArray(agents) && agents.length ? (agents.reduce((s, a) => s + (a.accuracy || 0), 0) / agents.length).toFixed(1) : 0}%`, change: 'All agents', positive: true },
    { label: 'Uptime', value: '99.8%', change: 'Last 30 days', positive: true },
  ];

  const statusColors = {
    running: 'bg-[#00FF94]/15 text-[#00FF94]',
    active: 'bg-[#00FF94]/15 text-[#00FF94]',
    paused: 'bg-[#FFB800]/15 text-[#FFB800]',
    stopped: 'bg-red-400/15 text-red-400',
  };

  const typeIcons = { Technical: Target, NLP: Brain, 'On-chain': Shield, Statistical: Activity };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="agents-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader icon={Bot} title="AI Agents" description="Autonomous trading agents scanning markets 24/7 for alpha" testId="agents-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load agents" onRetry={refetch} /> : (
          <>
            <StatsRow stats={stats} />

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {(Array.isArray(agents) ? agents : []).map((agent, i) => {
                const TypeIcon = typeIcons[agent.type] || Activity;
                return (
                  <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
                    <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-colors" data-testid={`agent-card-${i}`}>
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-2 rounded-lg bg-[#7B61FF]/10"><TypeIcon className="w-5 h-5 text-[#7B61FF]" /></div>
                            <div>
                              <CardTitle className="text-base font-['Outfit']">{agent.name}</CardTitle>
                              <p className="text-xs text-zinc-600">{agent.type} Analysis</p>
                            </div>
                          </div>
                          <Badge className={statusColors[agent.status] || 'bg-zinc-600/15 text-zinc-400'}>{agent.status}</Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4 mb-4">
                          <div>
                            <p className="text-xs text-zinc-500 mb-1">Accuracy</p>
                            <div className="flex items-center gap-2">
                              <Progress value={agent.accuracy} className="h-2 flex-1" />
                              <span className="text-xs font-mono text-zinc-300">{agent.accuracy}%</span>
                            </div>
                          </div>
                          <div>
                            <p className="text-xs text-zinc-500 mb-1">Signals Generated</p>
                            <p className="text-sm font-mono font-bold">{agent.signals}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button disabled size="sm" variant="outline" className="flex-1 rounded-full border-zinc-800 text-xs">Configure</Button>
                          <Button disabled size="sm" className="flex-1 rounded-full bg-[#7B61FF]/20 text-[#7B61FF]/60 text-xs"><Sparkles className="w-3 h-3 mr-1" /> View Signals</Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50 border-dashed">
                <CardContent className="p-6 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-300 mb-1">Deploy Custom Agent</h3>
                    <p className="text-xs text-zinc-600">Create a new AI agent with custom parameters and strategies</p>
                  </div>
                  <Button disabled className="rounded-full bg-[#7B61FF]/20 text-[#7B61FF]/60 border border-[#7B61FF]/10"><Zap className="w-4 h-4 mr-2" /> Deploy Agent</Button>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
};

export default AgentsPage;
