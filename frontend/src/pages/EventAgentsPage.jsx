import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Eye, Activity, Clock, Play, Pause, X, Zap, AlertTriangle, Calendar, TrendingUp } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockEventAgents } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";

const impactColor = { high: "bg-red-400/15 text-red-400", medium: "bg-yellow-400/15 text-yellow-400", low: "bg-[#00FF94]/15 text-[#00FF94]" };

const MOCK_EVENTS = [
  { name: "FOMC Rate Decision", date: "Mar 31, 2026", impact: "high", volatility: "+8.2%", description: "Federal Reserve interest rate announcement expected to hold at 4.25%" },
  { name: "BTC ETF Inflows Report", date: "Apr 1, 2026", impact: "high", volatility: "+5.1%", description: "Weekly ETF flow data release — previous week saw $1.2B net inflows" },
  { name: "US CPI Data", date: "Apr 3, 2026", impact: "high", volatility: "+6.5%", description: "Consumer Price Index month-over-month, expected 0.3%" },
  { name: "ETH Shanghai Upgrade", date: "Apr 5, 2026", impact: "medium", volatility: "+3.8%", description: "Network upgrade enabling validator withdrawal improvements" },
  { name: "Non-Farm Payrolls", date: "Apr 7, 2026", impact: "medium", volatility: "+4.2%", description: "US employment data, consensus 185K jobs added" },
  { name: "BOJ Policy Meeting", date: "Apr 10, 2026", impact: "low", volatility: "+2.1%", description: "Bank of Japan monetary policy update" },
];

const MOCK_LOG = [
  { time: "09:42:15", level: "info", message: "Agent monitoring FOMC event — T-24h countdown active" },
  { time: "09:41:02", level: "info", message: "Position sizing adjusted: BTC exposure reduced to 60% ahead of rate decision" },
  { time: "09:38:44", level: "warn", message: "Volatility spike detected: BTC 1h ATR exceeded 2.5x average" },
  { time: "09:35:11", level: "info", message: "Hedging order placed: SHORT BTC-PERP 0.05 BTC at $67,420" },
  { time: "09:30:00", level: "info", message: "Scheduled scan complete — 3 macro events within 7-day window" },
  { time: "09:22:18", level: "info", message: "News sentiment score for BTC: 0.72 (bullish)" },
  { time: "08:45:00", level: "info", message: "Daily briefing generated — 2 high-impact events this week" },
];

const EventAgentsPage = () => {
  const { isDemoMode, demoEventAgents } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;

  const { data: apiData, loading, error, refetch } = useApiData("/agents/event-agents", { skip: isDemoMode, token });
  const eventAgents = isDemoMode ? demoEventAgents : (apiData?.event_agents || apiData || mockEventAgents);
  const arr = Array.isArray(eventAgents) ? eventAgents : [];

  const [pausedAgents, setPausedAgents] = useState({});
  const [logModal, setLogModal] = useState(null);
  const [eventsModal, setEventsModal] = useState(false);

  const togglePause = (idx) => {
    setPausedAgents(prev => {
      const newState = { ...prev, [idx]: !prev[idx] };
      toast.success(newState[idx] ? "Agent paused" : "Agent resumed");
      return newState;
    });
  };

  const stats = [
    { label: "Active Watchers", value: String(arr.filter((_, i) => !pausedAgents[i]).length || arr.length), change: "Monitoring", positive: true },
    { label: "Events Tracked", value: "24", change: "This week", positive: true },
    { label: "Alerts Sent", value: "8", change: "Today", positive: true },
    { label: "Accuracy", value: "92%", change: "Event prediction", positive: true },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="event-agents-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader icon={Eye} title="Event Agents" description="Monitors macro events, news catalysts, and on-chain anomalies" testId="event-agents-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load event agents" onRetry={refetch} /> : (
          <>
            <StatsRow stats={stats} />

            {/* Upcoming Events Card */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium flex items-center gap-2"><Calendar className="w-4 h-4 text-[#FFB800]" /> Upcoming Macro Events</CardTitle>
                    <Button size="sm" variant="outline" onClick={() => setEventsModal(true)} className="rounded-full text-xs border-zinc-800 hover:border-[#7B61FF]/50" data-testid="view-all-events-btn">View All</Button>
                  </div>
                </CardHeader>
                <CardContent className="p-5 pt-0">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {MOCK_EVENTS.slice(0, 3).map((ev, i) => (
                      <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-xs font-medium text-zinc-300">{ev.name}</p>
                          <Badge className={impactColor[ev.impact]}>{ev.impact}</Badge>
                        </div>
                        <p className="text-[10px] text-zinc-600 mb-1">{ev.date}</p>
                        <p className="text-[10px] text-zinc-500">Expected volatility: <span className="text-yellow-400 font-mono">{ev.volatility}</span></p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Agent Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
              {arr.map((agent, i) => {
                const paused = pausedAgents[i];
                return (
                  <motion.div key={i} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                    <Card className={`bg-[#0A0A0A] border-zinc-800/50 transition-all ${paused ? "opacity-60" : "hover:border-zinc-700/50"}`}>
                      <CardContent className="p-5">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${paused ? "bg-zinc-600" : "bg-[#00FF94] animate-pulse"}`} />
                            <span className="text-sm font-medium text-zinc-200">{agent.name}</span>
                          </div>
                          <Badge className={paused ? "bg-zinc-700 text-zinc-500" : "bg-[#00FF94]/10 text-[#00FF94]"} >{paused ? "paused" : "active"}</Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div className="p-2 rounded bg-[#050505] border border-zinc-800/30">
                            <p className="text-[10px] text-zinc-600">Events Caught</p>
                            <p className="text-sm font-mono text-white">{agent.events_caught || agent.eventsCaught || 14}</p>
                          </div>
                          <div className="p-2 rounded bg-[#050505] border border-zinc-800/30">
                            <p className="text-[10px] text-zinc-600">Last Alert</p>
                            <p className="text-sm font-mono text-zinc-400">{agent.last_alert || "2h ago"}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={() => togglePause(i)} size="sm" variant="outline" className={`flex-1 rounded-full border-zinc-800 text-xs cursor-pointer ${paused ? "hover:border-[#00FF94]/50" : "hover:border-yellow-400/50"}`} data-testid={`pause-agent-${i}`}>
                            {paused ? <><Play className="w-3 h-3 mr-1" /> Resume</> : <><Pause className="w-3 h-3 mr-1" /> Pause</>}
                          </Button>
                          <Button onClick={() => setLogModal(agent)} size="sm" className="flex-1 rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white text-xs cursor-pointer" data-testid={`view-log-${i}`}>View Log</Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>
          </>
        )}

        {/* Log Modal */}
        <AnimatePresence>
          {logModal && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setLogModal(null)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} onClick={e => e.stopPropagation()} className="w-full max-w-lg mx-4">
                <Card className="bg-[#0A0A0A] border-zinc-800" data-testid="log-modal">
                  <CardHeader className="border-b border-zinc-800/50 pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium flex items-center gap-2"><Activity className="w-4 h-4 text-[#00FF94]" /> Event Log — {logModal.name}</CardTitle>
                      <button onClick={() => setLogModal(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4">
                    <div className="space-y-2 font-mono text-xs">
                      {MOCK_LOG.map((entry, i) => (
                        <div key={i} className="flex gap-3 p-2 rounded bg-[#050505]" data-testid={`log-entry-${i}`}>
                          <span className="text-zinc-600 shrink-0">{entry.time}</span>
                          <span className={entry.level === "warn" ? "text-yellow-400" : "text-zinc-400"}>{entry.level === "warn" && <AlertTriangle className="w-3 h-3 inline mr-1" />}{entry.message}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* All Events Modal */}
        <AnimatePresence>
          {eventsModal && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setEventsModal(false)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} onClick={e => e.stopPropagation()} className="w-full max-w-2xl mx-4">
                <Card className="bg-[#0A0A0A] border-zinc-800" data-testid="events-modal">
                  <CardHeader className="border-b border-zinc-800/50 pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium flex items-center gap-2"><Calendar className="w-4 h-4 text-[#FFB800]" /> Upcoming Macro Events</CardTitle>
                      <button onClick={() => setEventsModal(false)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-5 space-y-3">
                    {MOCK_EVENTS.map((ev, i) => (
                      <div key={i} className="p-4 rounded-lg bg-[#050505] border border-zinc-800/30" data-testid={`event-${i}`}>
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="text-sm font-medium text-zinc-200">{ev.name}</p>
                            <p className="text-xs text-zinc-600">{ev.date}</p>
                          </div>
                          <div className="text-right">
                            <Badge className={impactColor[ev.impact]}>{ev.impact} impact</Badge>
                            <p className="text-xs font-mono text-yellow-400 mt-1">{ev.volatility} vol</p>
                          </div>
                        </div>
                        <p className="text-xs text-zinc-500">{ev.description}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default EventAgentsPage;
