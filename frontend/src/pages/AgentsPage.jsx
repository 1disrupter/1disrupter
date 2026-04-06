import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Activity, TrendingUp, Zap, BarChart3, Shield, ArrowUpRight, ArrowDownRight, MinusCircle, Settings, Eye, X, ChevronRight, Wifi } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { useSystemMode } from '../contexts/DemoModeContext';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL;

const agentIcons = {
  'technical': TrendingUp,
  'nlp': Zap,
  'on-chain': Activity,
  'statistical': BarChart3,
};

const typeColors = {
  'technical': '#7B61FF',
  'nlp': '#00FF94',
  'on-chain': '#FFB800',
  'statistical': '#FF6B6B',
};

const signalColors = { BUY: '#00FF94', SELL: '#FF6B6B', HOLD: '#FFB800' };
const signalIcons = { BUY: ArrowUpRight, SELL: ArrowDownRight, HOLD: MinusCircle };

const AgentsPage = () => {
  const { mode, isDemo, isLive } = useSystemMode();
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentSignals, setAgentSignals] = useState([]);
  const [signalsLoading, setSignalsLoading] = useState(false);
  const [configAgent, setConfigAgent] = useState(null);
  const [configForm, setConfigForm] = useState({});

  // Fetch agents
  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await axios.get(`${API}/api/agents`);
        setAgents(res.data.agents || []);
      } catch (e) {
        console.error('Failed to fetch agents:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
    const interval = setInterval(fetchAgents, 30000);
    return () => clearInterval(interval);
  }, []);

  // Fetch signals for selected agent
  const openSignals = useCallback(async (agent) => {
    setSelectedAgent(agent);
    setSignalsLoading(true);
    try {
      const res = await axios.get(`${API}/api/agents/${agent.id}/signals?limit=20`);
      setAgentSignals(res.data.signals || []);
    } catch (e) {
      console.error('Failed to fetch signals:', e);
      setAgentSignals([]);
    } finally {
      setSignalsLoading(false);
    }
  }, []);

  const openConfig = useCallback((agent) => {
    setConfigAgent(agent);
    setConfigForm(agent.config || { risk_level: 'moderate', timeframe: '1h', signal_frequency: '15min' });
  }, []);

  const saveConfig = useCallback(async () => {
    if (!configAgent) return;
    try {
      await axios.put(`${API}/api/agents/${configAgent.id}/config`, configForm);
      setConfigAgent(null);
    } catch (e) {
      console.error('Config save error:', e);
    }
  }, [configAgent, configForm]);

  return (
    <div className="min-h-screen bg-[#050505] text-white p-6 md:p-8" data-testid="agents-page">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Bot className="w-6 h-6 text-[#7B61FF]" />
          <h1 className="text-2xl md:text-3xl font-bold">Trading Agents</h1>
          {isDemo ? (
            <Badge className="bg-[#7B61FF]/10 text-[#7B61FF] text-[10px] font-mono border border-[#7B61FF]/20" data-testid="agents-demo-badge">DEMO</Badge>
          ) : (
            <Badge className="bg-[#00FF94]/10 text-[#00FF94] text-[10px] font-mono border border-[#00FF94]/20 flex items-center gap-1" data-testid="agents-live-badge">
              <span className="w-1.5 h-1.5 rounded-full bg-[#00FF94] animate-pulse" /> LIVE
            </Badge>
          )}
        </div>
        <p className="text-sm text-zinc-500">
          {isDemo
            ? 'Viewing demo agent data — enable live mode in admin panel for real signals'
            : '4 AI agents analyzing markets in real time — generating live trading signals'}
        </p>
      </div>

      {/* Agent Grid */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="bg-[#0A0A0A] border border-zinc-800 rounded-xl h-48 animate-pulse" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents.map((agent, idx) => {
            const Icon = agentIcons[agent.type] || Bot;
            const color = typeColors[agent.type] || '#7B61FF';
            return (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.08 }}
              >
                <Card className="bg-[#0A0A0A] border-zinc-800 hover:border-zinc-700 transition-colors" data-testid={`agent-card-${agent.id}`}>
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg flex items-center justify-center"
                          style={{ backgroundColor: `${color}15`, border: `1px solid ${color}30` }}>
                          <Icon className="w-5 h-5" style={{ color }} />
                        </div>
                        <div>
                          <CardTitle className="text-base font-semibold text-white">{agent.name}</CardTitle>
                          <p className="text-xs text-zinc-500 mt-0.5">{agent.type}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-1.5">
                        <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-[#00FF94]' : 'bg-zinc-600'}`} />
                        <span className="text-[10px] text-zinc-500 font-mono uppercase">{agent.status}</span>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-xs text-zinc-500 mb-4 leading-relaxed">{agent.description}</p>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-3 mb-4">
                      <div className="text-center">
                        <p className="text-lg font-bold font-['JetBrains_Mono']" style={{ color }}>{agent.accuracy || 0}%</p>
                        <p className="text-[10px] text-zinc-600">Accuracy</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold font-['JetBrains_Mono'] text-white">{agent.signals || 0}</p>
                        <p className="text-[10px] text-zinc-600">Today</p>
                      </div>
                      <div className="text-center">
                        <p className="text-lg font-bold font-['JetBrains_Mono'] text-white">{agent.total_signals || 0}</p>
                        <p className="text-[10px] text-zinc-600">Total</p>
                      </div>
                    </div>

                    {/* Assets */}
                    <div className="flex flex-wrap gap-1.5 mb-4">
                      {(agent.assets || []).map(a => (
                        <span key={a} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-zinc-900 text-zinc-400 border border-zinc-800">{a}</span>
                      ))}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2">
                      <button
                        onClick={() => openSignals(agent)}
                        className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-600 transition-colors text-xs text-zinc-300 font-medium"
                        data-testid={`view-signals-${agent.id}`}
                      >
                        <Eye className="w-3 h-3" /> View Signals
                      </button>
                      <button
                        onClick={() => openConfig(agent)}
                        className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg bg-zinc-900 border border-zinc-800 hover:border-zinc-600 transition-colors text-xs text-zinc-300 font-medium"
                        data-testid={`configure-${agent.id}`}
                      >
                        <Settings className="w-3 h-3" /> Configure
                      </button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* Signals Modal */}
      <AnimatePresence>
        {selectedAgent && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => setSelectedAgent(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0A0A0A] border border-zinc-800 rounded-xl w-full max-w-lg max-h-[80vh] overflow-hidden"
              onClick={e => e.stopPropagation()}
              data-testid="signals-modal"
            >
              <div className="flex items-center justify-between p-4 border-b border-zinc-800">
                <div>
                  <h3 className="text-sm font-semibold text-white">{selectedAgent.name} Signals</h3>
                  <p className="text-[10px] text-zinc-500 mt-0.5">{agentSignals.length} recent signals</p>
                </div>
                <button onClick={() => setSelectedAgent(null)} className="text-zinc-500 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="overflow-y-auto max-h-[60vh] p-4 space-y-2">
                {signalsLoading ? (
                  <div className="text-center py-8 text-zinc-600 text-xs">Loading signals...</div>
                ) : agentSignals.length === 0 ? (
                  <div className="text-center py-8 text-zinc-600 text-xs">No signals generated yet — agent is scanning markets</div>
                ) : (
                  agentSignals.map((sig, i) => {
                    const SIcon = signalIcons[sig.signal_type] || MinusCircle;
                    const sColor = signalColors[sig.signal_type] || '#FFB800';
                    return (
                      <div key={sig.id || i} className="flex items-center gap-3 p-3 rounded-lg bg-[#050505] border border-zinc-800/50" data-testid={`signal-item-${i}`}>
                        <div className="w-8 h-8 rounded-md flex items-center justify-center shrink-0"
                          style={{ backgroundColor: `${sColor}15`, border: `1px solid ${sColor}30` }}>
                          <SIcon className="w-4 h-4" style={{ color: sColor }} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-semibold text-white">{sig.symbol}</span>
                            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded"
                              style={{ color: sColor, backgroundColor: `${sColor}10` }}>
                              {sig.signal_type}
                            </span>
                            <span className="text-[10px] text-zinc-500 font-mono">{sig.confidence}%</span>
                          </div>
                          <p className="text-[10px] text-zinc-500 truncate mt-0.5">{sig.analysis}</p>
                        </div>
                        <div className="text-right shrink-0">
                          <p className="text-xs text-zinc-400 font-mono">${Number(sig.price_at_signal || 0).toLocaleString()}</p>
                          <p className="text-[10px] text-zinc-600">{sig.generated_at ? new Date(sig.generated_at).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}) : ''}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Config Modal */}
      <AnimatePresence>
        {configAgent && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4"
            onClick={() => setConfigAgent(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }}
              className="bg-[#0A0A0A] border border-zinc-800 rounded-xl w-full max-w-sm"
              onClick={e => e.stopPropagation()}
              data-testid="config-modal"
            >
              <div className="flex items-center justify-between p-4 border-b border-zinc-800">
                <h3 className="text-sm font-semibold text-white">Configure {configAgent.name}</h3>
                <button onClick={() => setConfigAgent(null)} className="text-zinc-500 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>
              <div className="p-4 space-y-4">
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">Risk Level</label>
                  <select value={configForm.risk_level || 'moderate'}
                    onChange={e => setConfigForm(prev => ({ ...prev, risk_level: e.target.value }))}
                    className="w-full bg-[#050505] border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white"
                    data-testid="config-risk-level">
                    <option value="conservative">Conservative</option>
                    <option value="moderate">Moderate</option>
                    <option value="aggressive">Aggressive</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">Timeframe</label>
                  <select value={configForm.timeframe || '1h'}
                    onChange={e => setConfigForm(prev => ({ ...prev, timeframe: e.target.value }))}
                    className="w-full bg-[#050505] border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white"
                    data-testid="config-timeframe">
                    <option value="15m">15 minutes</option>
                    <option value="1h">1 hour</option>
                    <option value="4h">4 hours</option>
                    <option value="1d">Daily</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs text-zinc-500 mb-1 block">Signal Frequency</label>
                  <select value={configForm.signal_frequency || '15min'}
                    onChange={e => setConfigForm(prev => ({ ...prev, signal_frequency: e.target.value }))}
                    className="w-full bg-[#050505] border border-zinc-800 rounded-lg px-3 py-2 text-sm text-white"
                    data-testid="config-frequency">
                    <option value="5min">Every 5 min</option>
                    <option value="15min">Every 15 min</option>
                    <option value="1h">Every hour</option>
                  </select>
                </div>
                <button onClick={saveConfig}
                  className="w-full py-2.5 rounded-lg bg-[#7B61FF] hover:bg-[#6B51EF] text-white text-sm font-semibold transition-colors"
                  data-testid="save-config-btn">
                  Save Configuration
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AgentsPage;
