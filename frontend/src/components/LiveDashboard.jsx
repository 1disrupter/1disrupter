import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Activity, Bot, Target, TrendingUp, ArrowUpRight, ArrowDownRight,
  X, ShieldAlert, Zap, Hash
} from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

const actionMeta = {
  LONG: { icon: ArrowUpRight, color: "#00FF94", bg: "rgba(0,255,148,0.08)", label: "LONG" },
  SHORT: { icon: ArrowDownRight, color: "#ef4444", bg: "rgba(239,68,68,0.08)", label: "SHORT" },
  CLOSE: { icon: X, color: "#7B61FF", bg: "rgba(123,97,255,0.08)", label: "CLOSE" },
  TAKE_PROFIT: { icon: Target, color: "#00FF94", bg: "rgba(0,255,148,0.08)", label: "TP" },
  STOP_LOSS: { icon: ShieldAlert, color: "#FFB800", bg: "rgba(255,184,0,0.08)", label: "SL" },
};

function timeAgo(ts) {
  if (!ts) return "";
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 10) return "just now";
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

const MetricCard = ({ icon: Icon, label, value, sub, color }) => (
  <Card className="bg-[#0A0A0A] border-zinc-800/50">
    <CardContent className="p-5">
      <div className="flex items-center gap-2 mb-2">
        <Icon className="w-4 h-4" style={{ color }} />
        <span className="text-[10px] text-zinc-600 uppercase tracking-wider">{label}</span>
      </div>
      <p className="text-2xl font-bold font-mono text-zinc-100">{value}</p>
      {sub && <p className="text-[10px] text-zinc-600 mt-1">{sub}</p>}
    </CardContent>
  </Card>
);

const LiveDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchDash = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/dashboard/live`);
      setData(res.data);
    } catch { /* keep existing */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetchDash();
    const id = setInterval(fetchDash, 15000);
    return () => clearInterval(id);
  }, [fetchDash]);

  if (loading) {
    return (
      <div className="space-y-4" data-testid="dashboard-loading">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{[0,1,2,3].map(i => <div key={i} className="h-24 bg-[#0A0A0A] border border-zinc-800/40 rounded-xl animate-pulse" />)}</div>
        <div className="grid md:grid-cols-2 gap-4">{[0,1].map(i => <div key={i} className="h-48 bg-[#0A0A0A] border border-zinc-800/40 rounded-xl animate-pulse" />)}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-16" data-testid="dashboard-empty">
        <Activity className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
        <p className="text-sm text-zinc-500">No dashboard data available</p>
      </div>
    );
  }

  const { signals_24h, active_agents, win_rate, accuracy, total_pnl, recent_alerts = [], agents = [] } = data;
  const pnlPositive = total_pnl >= 0;

  return (
    <div className="space-y-6">
      {/* Metric cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard icon={Activity} label="Signals (24h)" value={signals_24h?.toLocaleString() ?? "0"} sub="Last 24 hours" color="#7B61FF" />
        <MetricCard icon={Bot} label="Active Agents" value={`${active_agents ?? 0}/4`} sub="Running now" color="#00FF94" />
        <MetricCard icon={Target} label="Win Rate" value={`${win_rate ?? 0}%`} sub="Confidence ≥ 70%" color={win_rate >= 60 ? "#00FF94" : "#FFB800"} />
        <MetricCard icon={TrendingUp} label="P&L" value={`${pnlPositive ? "+" : ""}$${Math.abs(total_pnl || 0).toLocaleString()}`} sub="Cumulative" color={pnlPositive ? "#00FF94" : "#FF6B6B"} />
      </div>

      {/* Two columns: agents + recent alerts */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Agents status */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-0">
              <div className="px-5 py-3 border-b border-zinc-800/40">
                <p className="text-xs font-medium text-zinc-400 flex items-center gap-2"><Bot className="w-3.5 h-3.5 text-[#7B61FF]" /> Agent Status</p>
              </div>
              <div data-testid="dashboard-agents">
                {agents.length === 0 ? (
                  <div className="py-8 text-center text-xs text-zinc-700">No agents registered</div>
                ) : agents.map((a, i) => (
                  <div key={a.id || i} className="flex items-center justify-between px-5 py-3 border-b border-zinc-800/30 last:border-0">
                    <div className="flex items-center gap-2.5">
                      <span className={`w-2 h-2 rounded-full ${a.status === "active" ? "bg-[#00FF94] animate-pulse" : "bg-zinc-600"}`} />
                      <span className="text-sm text-zinc-200">{a.name}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-[10px] font-mono text-zinc-500">
                      <Hash className="w-3 h-3" />
                      {a.total_signals ?? 0}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent alerts */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-0">
              <div className="px-5 py-3 border-b border-zinc-800/40">
                <p className="text-xs font-medium text-zinc-400 flex items-center gap-2"><Zap className="w-3.5 h-3.5 text-[#FFB800]" /> Recent Alerts</p>
              </div>
              <div data-testid="dashboard-recent-alerts">
                {recent_alerts.length === 0 ? (
                  <div className="py-8 text-center text-xs text-zinc-700">No recent alerts</div>
                ) : recent_alerts.map((a, i) => {
                  const meta = actionMeta[a.action] || actionMeta.LONG;
                  const Icon = meta.icon;
                  return (
                    <div key={`${a.timestamp}-${i}`} className="flex items-center gap-3 px-5 py-3 border-b border-zinc-800/30 last:border-0">
                      <div className="w-7 h-7 rounded-md flex items-center justify-center shrink-0" style={{ background: meta.bg }}>
                        <Icon className="w-3.5 h-3.5" style={{ color: meta.color }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                          <span className="text-[9px] font-bold px-1 py-0.5 rounded" style={{ background: meta.bg, color: meta.color }}>{meta.label}</span>
                          <span className="text-xs font-mono font-semibold text-zinc-200">{a.asset}</span>
                          {a.confidence != null && <span className="text-[10px] text-zinc-600">{a.confidence}%</span>}
                        </div>
                      </div>
                      <span className="text-[10px] text-zinc-600 font-mono shrink-0">{timeAgo(a.timestamp)}</span>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default LiveDashboard;
