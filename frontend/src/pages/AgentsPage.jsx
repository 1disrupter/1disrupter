import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Bot, Activity, Target, Zap, Shield, Brain, Sparkles, X, Settings, Clock } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockAgents } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";

const statusDot = { active: "bg-[#00FF94]", idle: "bg-yellow-400", offline: "bg-zinc-600" };
const ASSETS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "LINK/USDT"];
const TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1D"];
const RISK_LEVELS = ["conservative", "moderate", "aggressive"];
const FREQUENCIES = ["realtime", "5min", "15min", "1h", "4h"];

const AgentsPage = () => {
  const { isDemoMode, demoAgents } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;

  const { data: apiAgents, loading, error, refetch } = useApiData("/agents", { skip: isDemoMode, token });
  const agents = isDemoMode ? demoAgents : (apiAgents?.agents || apiAgents || mockAgents);
  const arr = Array.isArray(agents) ? agents : [];

  const [configModal, setConfigModal] = useState(null);
  const [signalsModal, setSignalsModal] = useState(null);
  const [configs, setConfigs] = useState({});

  const stats = [
    { label: "Active Agents", value: String(arr.filter(a => a.status === "active").length || arr.length), change: "Running", positive: true },
    { label: "Signals Today", value: String(arr.reduce((s, a) => s + (a.signals || a.signalCount || 0), 0) || 48), change: "Generated", positive: true },
    { label: "Avg Accuracy", value: `${Math.round(arr.reduce((s, a) => s + (a.accuracy || 0), 0) / (arr.length || 1)) || 87}%`, change: "Hit rate", positive: true },
    { label: "Total P&L", value: "+$2,847", change: "Today", positive: true },
  ];

  const openConfigure = (agent, idx) => {
    setConfigModal({ ...agent, idx, ...configs[idx] });
  };

  const saveConfig = (idx) => {
    setConfigs(prev => ({
      ...prev,
      [idx]: {
        asset: configModal.configAsset || "BTC/USDT",
        timeframe: configModal.configTimeframe || "1h",
        risk: configModal.configRisk || "moderate",
        frequency: configModal.configFrequency || "15min"
      }
    }));
    setConfigModal(null);
    toast.success("Agent configuration saved");
  };

  const openSignals = (agent, idx) => {
    const mockSignals = [
      { time: "2 min ago", type: "LONG", asset: agent.asset || "BTC/USDT", entry: "$67,250", confidence: 84, status: "active" },
      { time: "18 min ago", type: "SHORT", asset: agent.asset || "ETH/USDT", entry: "$3,420", confidence: 76, status: "closed" },
      { time: "1h ago", type: "LONG", asset: agent.asset || "SOL/USDT", entry: "$142.50", confidence: 91, status: "profit" },
      { time: "3h ago", type: "LONG", asset: agent.asset || "BTC/USDT", entry: "$66,800", confidence: 88, status: "profit" },
    ];
    setSignalsModal({ agent, signals: mockSignals });
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="agents-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader icon={Bot} title="AI Agents" description="Autonomous trading agents powered by advanced ML models" testId="agents-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load agents" onRetry={refetch} /> : (
          <>
            <StatsRow stats={stats} />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
              {arr.map((agent, i) => {
                const cfg = configs[i];
                return (
                  <motion.div key={i} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                    <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-all">
                      <CardContent className="p-5">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${statusDot[agent.status] || "bg-zinc-600"}`} />
                            <span className="text-sm font-medium text-zinc-200">{agent.name}</span>
                          </div>
                          <Badge className="bg-zinc-800 text-zinc-500 text-[10px]">{agent.type || "ML"}</Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div className="p-2 rounded bg-[#050505] border border-zinc-800/30">
                            <p className="text-[10px] text-zinc-600">Accuracy</p>
                            <p className="text-sm font-mono text-[#00FF94]">{agent.accuracy || 85}%</p>
                          </div>
                          <div className="p-2 rounded bg-[#050505] border border-zinc-800/30">
                            <p className="text-[10px] text-zinc-600">Signals</p>
                            <p className="text-sm font-mono text-white">{agent.signals || agent.signalCount || 12}</p>
                          </div>
                        </div>
                        {cfg && (
                          <div className="flex flex-wrap gap-1 mb-3">
                            <Badge className="bg-[#7B61FF]/10 text-[#7B61FF] text-[9px]">{cfg.asset}</Badge>
                            <Badge className="bg-zinc-800 text-zinc-400 text-[9px]">{cfg.timeframe}</Badge>
                            <Badge className="bg-zinc-800 text-zinc-400 text-[9px]">{cfg.risk}</Badge>
                          </div>
                        )}
                        <div className="flex gap-2">
                          <Button onClick={() => openConfigure(agent, i)} size="sm" variant="outline" className="flex-1 rounded-full border-zinc-800 hover:border-[#7B61FF]/50 text-xs cursor-pointer" data-testid={`configure-agent-${i}`}><Settings className="w-3 h-3 mr-1" /> Configure</Button>
                          <Button onClick={() => openSignals(agent, i)} size="sm" className="flex-1 rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white text-xs cursor-pointer" data-testid={`view-signals-${i}`}><Sparkles className="w-3 h-3 mr-1" /> View Signals</Button>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                );
              })}
            </div>

            {/* Deploy Agent CTA */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50 border-dashed">
                <CardContent className="p-6 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-300 mb-1">Deploy Custom Agent</h3>
                    <p className="text-xs text-zinc-600">Create and train a new agent with your custom parameters</p>
                  </div>
                  <Button onClick={() => toast.info("Custom agent deployment coming in v2.0")} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white border border-[#7B61FF]/30 cursor-pointer" data-testid="deploy-agent-btn"><Zap className="w-4 h-4 mr-2" /> Deploy Agent</Button>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}

        {/* Configure Modal */}
        <AnimatePresence>
          {configModal && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setConfigModal(null)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} onClick={e => e.stopPropagation()} className="w-full max-w-md mx-4">
                <Card className="bg-[#0A0A0A] border-zinc-800" data-testid="config-modal">
                  <CardHeader className="border-b border-zinc-800/50 pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium flex items-center gap-2"><Settings className="w-4 h-4 text-[#7B61FF]" /> Configure: {configModal.name}</CardTitle>
                      <button onClick={() => setConfigModal(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-5 space-y-4">
                    <div>
                      <label className="text-xs text-zinc-500 mb-2 block">Trading Pair</label>
                      <div className="flex flex-wrap gap-2">
                        {ASSETS.map(a => (<button key={a} onClick={() => setConfigModal(p => ({ ...p, configAsset: a }))} className={`px-3 py-1.5 rounded-full text-xs font-mono transition-all ${(configModal.configAsset || "BTC/USDT") === a ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`cfg-asset-${a}`}>{a}</button>))}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 mb-2 block">Timeframe</label>
                      <div className="flex flex-wrap gap-2">
                        {TIMEFRAMES.map(t => (<button key={t} onClick={() => setConfigModal(p => ({ ...p, configTimeframe: t }))} className={`px-3 py-1.5 rounded-full text-xs font-mono transition-all ${(configModal.configTimeframe || "1h") === t ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`cfg-tf-${t}`}>{t}</button>))}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 mb-2 block">Risk Level</label>
                      <div className="flex gap-2">
                        {RISK_LEVELS.map(r => (<button key={r} onClick={() => setConfigModal(p => ({ ...p, configRisk: r }))} className={`flex-1 px-3 py-2 rounded-lg text-xs capitalize transition-all ${(configModal.configRisk || "moderate") === r ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`cfg-risk-${r}`}>{r}</button>))}
                      </div>
                    </div>
                    <div>
                      <label className="text-xs text-zinc-500 mb-2 block">Signal Frequency</label>
                      <div className="flex flex-wrap gap-2">
                        {FREQUENCIES.map(f => (<button key={f} onClick={() => setConfigModal(p => ({ ...p, configFrequency: f }))} className={`px-3 py-1.5 rounded-full text-xs font-mono transition-all ${(configModal.configFrequency || "15min") === f ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`cfg-freq-${f}`}>{f}</button>))}
                      </div>
                    </div>
                    <Button onClick={() => saveConfig(configModal.idx)} className="w-full rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white mt-2" data-testid="save-config-btn">Save Configuration</Button>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Signals Modal */}
        <AnimatePresence>
          {signalsModal && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setSignalsModal(null)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} onClick={e => e.stopPropagation()} className="w-full max-w-lg mx-4">
                <Card className="bg-[#0A0A0A] border-zinc-800" data-testid="signals-modal">
                  <CardHeader className="border-b border-zinc-800/50 pb-3">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium flex items-center gap-2"><Activity className="w-4 h-4 text-[#00FF94]" /> Signals — {signalsModal.agent.name}</CardTitle>
                      <button onClick={() => setSignalsModal(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-5 space-y-3">
                    {signalsModal.signals.map((sig, i) => (
                      <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 flex items-center justify-between" data-testid={`signal-${i}`}>
                        <div>
                          <div className="flex items-center gap-2 mb-1">
                            <Badge className={sig.type === "LONG" ? "bg-[#00FF94]/15 text-[#00FF94]" : "bg-red-400/15 text-red-400"}>{sig.type}</Badge>
                            <span className="text-xs font-mono text-zinc-300">{sig.asset}</span>
                          </div>
                          <div className="flex items-center gap-3 text-[10px] text-zinc-600">
                            <span>Entry: {sig.entry}</span>
                            <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {sig.time}</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-mono text-white">{sig.confidence}%</p>
                          <Badge className={sig.status === "profit" ? "bg-[#00FF94]/10 text-[#00FF94] text-[9px]" : sig.status === "active" ? "bg-[#7B61FF]/10 text-[#7B61FF] text-[9px]" : "bg-zinc-700 text-zinc-400 text-[9px]"}>{sig.status}</Badge>
                        </div>
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

export default AgentsPage;
