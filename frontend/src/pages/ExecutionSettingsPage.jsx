import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import { Settings, Zap, Shield, Activity, Loader2, CheckCircle, XCircle, Clock } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { useAuth } from "../contexts/AuthContext";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STATUS_ICON = { success: CheckCircle, failed: XCircle, pending: Clock, skipped: Clock };
const STATUS_COLOR = { success: "text-[#00FF94]", failed: "text-red-400", pending: "text-amber-400", skipped: "text-zinc-500" };

const ExecutionSettingsPage = () => {
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const navigate = useNavigate();

  const [config, setConfig] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state
  const [mode, setMode] = useState("paper");
  const [posSize, setPosSize] = useState("0.001");
  const [enabled, setEnabled] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [cfgRes, logsRes] = await Promise.all([
        axios.get(`${API}/execution/configs/me`, { headers }),
        axios.get(`${API}/execution/logs?limit=20`, { headers }),
      ]);
      const cfg = cfgRes.data;
      setConfig(cfg);
      setMode(cfg.execution_mode || "paper");
      setPosSize(String(cfg.base_position_size || 0.001));
      setEnabled(cfg.is_enabled || false);
      setLogs(logsRes.data.logs || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    if (!token) { navigate("/login"); return; }
    fetchData();
  }, [token, fetchData, navigate]);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await axios.post(`${API}/execution/configs/me`, {
        execution_mode: mode,
        base_position_size: parseFloat(posSize) || 0.001,
        is_enabled: enabled,
      }, { headers: { ...headers, "Content-Type": "application/json" } });
      setConfig(res.data);
      toast.success("Settings saved!");
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to save");
    }
    setSaving(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4">
        <div className="max-w-3xl mx-auto space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="h-24 bg-zinc-900 rounded-lg animate-pulse" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="execution-settings-page">
      <div className="max-w-3xl mx-auto space-y-6">
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
          <h1 className="text-2xl font-bold font-['Outfit'] text-white" data-testid="execution-settings-title">Execution Settings</h1>
          <p className="text-sm text-zinc-500 mt-1">Configure auto-execution for your strategy subscriptions</p>
        </motion.div>

        {/* Config Card */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="config-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                <Settings className="w-4 h-4 text-[#7B61FF]" /> Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {/* Enable toggle */}
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-200 font-medium">Auto-Execution</p>
                  <p className="text-xs text-zinc-600">Automatically execute signals from subscribed strategies</p>
                </div>
                <button
                  onClick={() => setEnabled(!enabled)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${enabled ? "bg-[#7B61FF]" : "bg-zinc-800"}`}
                  data-testid="execution-toggle"
                >
                  <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition-transform ${enabled ? "translate-x-6" : "translate-x-0.5"}`} />
                </button>
              </div>

              {/* Execution mode */}
              <div>
                <label className="text-xs text-zinc-500 uppercase tracking-wider mb-2 block">Execution Mode</label>
                <div className="flex gap-2">
                  {[
                    { value: "paper", label: "Paper", desc: "Simulated orders", icon: Shield },
                    { value: "testnet", label: "Testnet", desc: "Binance Testnet", icon: Zap },
                  ].map(opt => (
                    <button
                      key={opt.value}
                      onClick={() => setMode(opt.value)}
                      className={`flex-1 p-3 rounded-lg border text-left transition-colors ${mode === opt.value ? "border-[#7B61FF]/50 bg-[#7B61FF]/5" : "border-zinc-800 bg-[#050505] hover:border-zinc-700"}`}
                      data-testid={`mode-${opt.value}`}
                    >
                      <opt.icon className={`w-4 h-4 mb-1 ${mode === opt.value ? "text-[#7B61FF]" : "text-zinc-600"}`} />
                      <p className="text-sm font-medium text-zinc-200">{opt.label}</p>
                      <p className="text-[10px] text-zinc-600">{opt.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Position size */}
              <div>
                <label className="text-xs text-zinc-500 uppercase tracking-wider mb-1.5 block">Base Position Size</label>
                <Input
                  type="number"
                  step="0.001"
                  min="0.001"
                  max="10"
                  value={posSize}
                  onChange={e => setPosSize(e.target.value)}
                  className="bg-[#050505] border-zinc-800 text-sm w-48 font-mono"
                  data-testid="position-size-input"
                />
                <p className="text-[10px] text-zinc-600 mt-1">Amount per trade (e.g., 0.01 BTC)</p>
              </div>

              {/* Save */}
              <div className="pt-2">
                <Button onClick={handleSave} disabled={saving} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-sm" data-testid="save-config-btn">
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : "Save Settings"}
                </Button>
                {config?.exists && (
                  <span className="text-[10px] text-zinc-600 ml-3">
                    Last updated: {config.updated_at ? new Date(config.updated_at).toLocaleString() : "—"}
                  </span>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Status */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-4">
              <div className="flex items-center gap-4 flex-wrap">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${enabled ? "bg-[#00FF94] animate-pulse" : "bg-zinc-700"}`} />
                  <span className="text-xs text-zinc-400">{enabled ? "Active" : "Disabled"}</span>
                </div>
                <Badge className="bg-zinc-800 text-zinc-400 text-[10px]">{mode === "paper" ? "Paper Trading" : "Testnet Trading"}</Badge>
                <span className="text-[10px] text-zinc-600 font-mono">Size: {posSize}</span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Executions */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="execution-logs-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                <Activity className="w-4 h-4 text-[#7B61FF]" /> Recent Executions ({logs.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {logs.length === 0 ? (
                <p className="text-zinc-600 text-xs py-6 text-center">No executions yet. Subscribe to strategies and enable auto-execution.</p>
              ) : (
                <div className="space-y-2">
                  {logs.map((l, i) => {
                    const Icon = STATUS_ICON[l.status] || Clock;
                    const color = STATUS_COLOR[l.status] || "text-zinc-500";
                    return (
                      <div key={l.id} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800/20" data-testid={`log-row-${i}`}>
                        <div className="flex items-center gap-3">
                          <Icon className={`w-4 h-4 ${color}`} />
                          <div>
                            <span className="text-xs font-mono text-zinc-300">
                              {l.request_payload?.side} {l.request_payload?.quantity} {l.request_payload?.symbol}
                            </span>
                            <p className="text-[10px] text-zinc-600">
                              {l.execution_mode} | {l.strategy_id === "manual_test" ? "test order" : l.strategy_id?.substring(0, 8)}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={`text-[10px] ${l.status === "success" ? "bg-[#00FF94]/15 text-[#00FF94]" : l.status === "failed" ? "bg-red-400/15 text-red-400" : "bg-zinc-800 text-zinc-400"}`}>
                            {l.status}
                          </Badge>
                          <p className="text-[9px] text-zinc-700 mt-0.5">{l.created_at ? new Date(l.created_at).toLocaleString() : ""}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default ExecutionSettingsPage;
