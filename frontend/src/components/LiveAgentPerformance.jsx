import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Bot, TrendingUp, Zap, Activity, BarChart3, Target, Hash, Award } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

const typeConfig = {
  technical: { icon: TrendingUp, color: "#7B61FF", label: "Technical" },
  nlp: { icon: Zap, color: "#00FF94", label: "NLP" },
  "on-chain": { icon: Activity, color: "#FFB800", label: "On-Chain" },
  statistical: { icon: BarChart3, color: "#FF6B6B", label: "Statistical" },
};

const AgentCard = ({ agent, index }) => {
  const cfg = typeConfig[agent.type] || typeConfig.technical;
  const Icon = cfg.icon;
  const pnl = agent.total_pnl || 0;
  const pnlPositive = pnl >= 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.07 }}
      data-testid={`agent-perf-card-${agent.id}`}
    >
      <Card className="bg-[#0A0A0A] border-zinc-800/60 hover:border-zinc-700/60 transition-colors">
        <CardContent className="p-5">
          {/* Top row: icon + name + status */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
                style={{ background: `${cfg.color}12`, border: `1px solid ${cfg.color}25` }}
              >
                <Icon className="w-5 h-5" style={{ color: cfg.color }} />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-zinc-100">{agent.name}</h3>
                <span className="text-[10px] text-zinc-600 font-mono uppercase">{cfg.label}</span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  agent.status === "active" ? "bg-[#00FF94] animate-pulse" : "bg-zinc-600"
                }`}
              />
              <span className="text-[10px] text-zinc-500 font-mono">
                {agent.status === "active" ? "RUNNING" : "IDLE"}
              </span>
            </div>
          </div>

          {/* Metrics grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <Metric
              icon={Target}
              label="Accuracy"
              value={`${agent.accuracy ?? 0}%`}
              color={agent.accuracy >= 70 ? "#00FF94" : agent.accuracy >= 50 ? "#FFB800" : "#FF6B6B"}
            />
            <Metric
              icon={Award}
              label="Win Rate"
              value={`${agent.win_rate ?? 0}%`}
              color={agent.win_rate >= 60 ? "#00FF94" : "#FFB800"}
            />
            <Metric
              icon={TrendingUp}
              label="P&L"
              value={`${pnlPositive ? "+" : ""}$${Math.abs(pnl).toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
              color={pnlPositive ? "#00FF94" : "#FF6B6B"}
            />
            <Metric
              icon={Hash}
              label="Trades"
              value={`${agent.signals_today ?? 0} / ${agent.total_signals ?? 0}`}
              sublabel="today / total"
              color="#7B61FF"
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const Metric = ({ icon: Icon, label, value, sublabel, color }) => (
  <div className="rounded-lg bg-zinc-900/50 border border-zinc-800/40 p-3">
    <div className="flex items-center gap-1.5 mb-1">
      <Icon className="w-3 h-3" style={{ color }} />
      <span className="text-[9px] text-zinc-600 uppercase tracking-wider">{label}</span>
    </div>
    <p className="text-base font-bold font-mono" style={{ color }}>
      {value}
    </p>
    {sublabel && <p className="text-[8px] text-zinc-700 mt-0.5">{sublabel}</p>}
  </div>
);

const LiveAgentPerformance = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchPerformance = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/agents/performance`);
      setAgents(res.data.agents || []);
    } catch {
      // keep existing
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPerformance();
    const interval = setInterval(fetchPerformance, 15000);
    return () => clearInterval(interval);
  }, [fetchPerformance]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="agents-loading">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="bg-[#0A0A0A] border border-zinc-800/40 rounded-xl h-44 animate-pulse" />
        ))}
      </div>
    );
  }

  if (agents.length === 0) {
    return (
      <div className="text-center py-16" data-testid="agents-empty">
        <Bot className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
        <p className="text-sm text-zinc-500">No agent performance data yet</p>
        <p className="text-xs text-zinc-700 mt-1">Agents are initializing — data will appear shortly</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4" data-testid="live-agent-grid">
      {agents.map((agent, i) => (
        <AgentCard key={agent.id} agent={agent} index={i} />
      ))}
    </div>
  );
};

export default LiveAgentPerformance;
