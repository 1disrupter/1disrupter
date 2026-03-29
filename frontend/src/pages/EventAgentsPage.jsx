import { motion } from "framer-motion";
import {
  Eye, Activity, Cpu, Target, Zap, Clock, Play, Pause
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { ScrollArea } from "../components/ui/scroll-area";
import { PageHeader, StatsRow } from "../components/PlaceholderUI";
import { mockEventAgents } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";

const EventAgentsPage = () => {
  const { isDemoMode, demoEventAgents } = useDemoMode();
  const eventAgents = isDemoMode ? demoEventAgents : mockEventAgents;
  const stats = [
    { label: 'Active Monitors', value: '3', change: 'of 4 deployed', positive: true },
    { label: 'Events Detected', value: '47', change: 'Last 7 days', positive: true },
    { label: 'Avg Confidence', value: '85.8%', change: '+2.4%', positive: true },
    { label: 'Response Time', value: '<2s', change: 'Median latency', positive: true },
  ];

  const statusColors = {
    active: 'bg-[#00FF94]/15 text-[#00FF94]',
    watching: 'bg-[#FFB800]/15 text-[#FFB800]',
    paused: 'bg-zinc-600/15 text-zinc-400',
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="events-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader
          icon={Eye}
          title="Event Agents"
          description="Monitors that detect market-moving events and trigger automated responses"
          testId="events-header"
        />

        <StatsRow stats={stats} />

        {/* Event Agent Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {eventAgents.map((agent, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-colors" data-testid={`event-agent-${i}`}>
                <CardContent className="p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-[#00FF94] animate-pulse' : 'bg-zinc-600'}`} />
                      <div>
                        <h3 className="text-sm font-semibold text-zinc-200">{agent.name}</h3>
                        <p className="text-xs text-zinc-600">{agent.type}</p>
                      </div>
                    </div>
                    <Badge className={statusColors[agent.status]}>{agent.status}</Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30">
                      <p className="text-xs text-zinc-600 mb-1">Last Trigger</p>
                      <p className="text-xs font-mono text-zinc-400 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {agent.lastTrigger}
                      </p>
                    </div>
                    <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30">
                      <p className="text-xs text-zinc-600 mb-1">Confidence</p>
                      <p className="text-sm font-mono font-bold text-[#00FF94]">{agent.confidence}%</p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button disabled size="sm" variant="outline" className="flex-1 rounded-full border-zinc-800 text-xs">
                      <Pause className="w-3 h-3 mr-1" /> Pause
                    </Button>
                    <Button disabled size="sm" className="flex-1 rounded-full bg-[#7B61FF]/20 text-[#7B61FF]/60 text-xs">
                      View Log
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Recent Events Feed */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#7B61FF]" /> Event Feed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[200px]">
                <div className="space-y-2">
                  {[
                    { time: '14:32', event: 'Fed rate decision detected — no change', agent: 'Fed Rate Monitor', color: 'text-[#FFB800]' },
                    { time: '12:18', event: 'Large BTC withdrawal from Binance — 4,200 BTC', agent: 'Liquidation Scanner', color: 'text-[#00FF94]' },
                    { time: '09:45', event: 'ETH staking rate increased to 3.8%', agent: 'ETH Merge Tracker', color: 'text-[#7B61FF]' },
                    { time: '08:12', event: 'BTC hash rate new ATH — 620 EH/s', agent: 'BTC Halving Clock', color: 'text-zinc-400' },
                    { time: '06:30', event: 'Unusual options activity on ETH $2,200 calls', agent: 'Liquidation Scanner', color: 'text-[#00FF94]' },
                  ].map((e, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-lg hover:bg-white/[0.02] transition-colors">
                      <span className="text-xs font-mono text-zinc-600 w-12 shrink-0">{e.time}</span>
                      <div className="flex-1">
                        <p className="text-xs text-zinc-300">{e.event}</p>
                        <p className={`text-[10px] ${e.color} mt-0.5`}>{e.agent}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default EventAgentsPage;
