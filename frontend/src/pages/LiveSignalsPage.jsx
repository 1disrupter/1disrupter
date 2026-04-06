import { useState, useEffect, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import {
  Activity, ArrowUpRight, ArrowDownRight, Target, ShieldAlert,
  X, TrendingUp, TrendingDown, Clock, Zap
} from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useSystemMode } from "../contexts/DemoModeContext";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

const actionMeta = {
  LONG: { icon: ArrowUpRight, color: "#00FF94", bg: "rgba(0,255,148,0.08)", label: "LONG" },
  SHORT: { icon: ArrowDownRight, color: "#ef4444", bg: "rgba(239,68,68,0.08)", label: "SHORT" },
  CLOSE: { icon: X, color: "#7B61FF", bg: "rgba(123,97,255,0.08)", label: "CLOSE" },
  TAKE_PROFIT: { icon: Target, color: "#00FF94", bg: "rgba(0,255,148,0.08)", label: "TP HIT" },
  STOP_LOSS: { icon: ShieldAlert, color: "#FFB800", bg: "rgba(255,184,0,0.08)", label: "SL HIT" },
};

function timeAgo(ts) {
  if (!ts) return "";
  const diff = Math.floor((Date.now() - new Date(ts).getTime()) / 1000);
  if (diff < 10) return "just now";
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

const SignalRow = ({ signal, index }) => {
  const meta = actionMeta[signal.action] || actionMeta.LONG;
  const Icon = meta.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index < 10 ? index * 0.03 : 0 }}
      data-testid={`signal-row-${index}`}
    >
      <div className="flex items-center gap-4 px-5 py-3.5 border-b border-zinc-800/40 hover:bg-white/[0.015] transition-colors">
        {/* Action badge */}
        <div
          className="flex items-center justify-center w-9 h-9 rounded-lg shrink-0"
          style={{ background: meta.bg }}
        >
          <Icon className="w-4 h-4" style={{ color: meta.color }} />
        </div>

        {/* Main info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className="text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded"
              style={{ background: meta.bg, color: meta.color }}
            >
              {meta.label}
            </span>
            <span className="text-sm font-mono font-semibold text-zinc-100">
              {signal.asset || "—"}
            </span>
            {signal.confidence && (
              <span className="text-[10px] text-zinc-500 font-mono">
                {signal.confidence}%
              </span>
            )}
          </div>
          <p className="text-xs text-zinc-500 mt-0.5 truncate max-w-md">
            {signal.message}
          </p>
        </div>

        {/* Agent / Strategy */}
        <div className="hidden md:block text-right min-w-[120px]">
          <p className="text-[10px] text-[#7B61FF] font-medium truncate">
            {signal.strategy_name || signal.agent_id || "—"}
          </p>
        </div>

        {/* Price */}
        <div className="text-right min-w-[90px]">
          {signal.price ? (
            <p className="text-xs font-mono font-semibold text-zinc-200">
              ${Number(signal.price).toLocaleString(undefined, { maximumFractionDigits: 2 })}
            </p>
          ) : (
            <span className="text-[10px] text-zinc-700">—</span>
          )}
        </div>

        {/* Timestamp */}
        <div className="text-right min-w-[60px]">
          <span className="text-[10px] text-zinc-600 font-mono">
            {timeAgo(signal.timestamp)}
          </span>
        </div>
      </div>
    </motion.div>
  );
};

const LiveSignalsPage = () => {
  const { mode, isDemo, isLive } = useSystemMode();
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, long: 0, short: 0 });
  const pollRef = useRef(null);

  const fetchSignals = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/alerts/live?limit=50`);
      const alerts = res.data.alerts || [];
      setSignals(alerts);
      setStats({
        total: alerts.length,
        long: alerts.filter(a => a.action === "LONG").length,
        short: alerts.filter(a => a.action === "SHORT").length,
      });
    } catch {
      // keep existing
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSignals();
    const interval = isDemo ? 12000 : 8000;
    pollRef.current = setInterval(fetchSignals, interval);
    return () => clearInterval(pollRef.current);
  }, [fetchSignals, isDemo]);

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="live-signals-page">
      <div className="max-w-5xl mx-auto">

        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/20">
              <Activity className="w-6 h-6 text-[#7B61FF]" />
            </div>
            <div>
              <h1 className="text-2xl font-bold font-['Outfit'] text-zinc-100" data-testid="live-signals-title">
                Live Signals
              </h1>
              <p className="text-sm text-zinc-500 mt-0.5">
                {isLive
                  ? "Real-time trading signals from AI agents"
                  : "Simulated signal feed — demo mode active"}
              </p>
            </div>
          </div>

          <Badge
            className={`text-[10px] font-mono px-3 py-1.5 ${
              isLive
                ? "bg-[#00FF94]/10 text-[#00FF94] border border-[#00FF94]/20"
                : "bg-[#7B61FF]/10 text-[#7B61FF] border border-[#7B61FF]/20"
            }`}
            data-testid="signals-mode-badge"
          >
            <span className={`w-1.5 h-1.5 rounded-full mr-1.5 inline-block ${
              isLive ? "bg-[#00FF94] animate-pulse" : "bg-[#7B61FF]"
            }`} />
            {isLive ? "LIVE" : "DEMO"}
          </Badge>
        </div>

        {/* Stats bar */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            { label: "Total Signals", value: stats.total, icon: Activity, color: "#7B61FF" },
            { label: "Long", value: stats.long, icon: TrendingUp, color: "#00FF94" },
            { label: "Short", value: stats.short, icon: TrendingDown, color: "#ef4444" },
          ].map((s) => (
            <Card key={s.label} className="bg-[#0A0A0A] border-zinc-800/50">
              <CardContent className="p-4 flex items-center gap-3">
                <s.icon className="w-4 h-4" style={{ color: s.color }} />
                <div>
                  <p className="text-[10px] text-zinc-600 uppercase tracking-wider">{s.label}</p>
                  <p className="text-lg font-bold font-mono text-zinc-100">{s.value}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Signal feed */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50 overflow-hidden">
          {/* Table header */}
          <div className="flex items-center gap-4 px-5 py-2.5 border-b border-zinc-800/60 bg-zinc-900/30">
            <div className="w-9" />
            <div className="flex-1 text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Signal</div>
            <div className="hidden md:block min-w-[120px] text-right text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Agent</div>
            <div className="min-w-[90px] text-right text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Price</div>
            <div className="min-w-[60px] text-right text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Time</div>
          </div>

          <CardContent className="p-0">
            {loading && signals.length === 0 ? (
              <div className="py-20 text-center" data-testid="signals-loading">
                <div className="w-8 h-8 border-2 border-[#7B61FF]/30 border-t-[#7B61FF] rounded-full animate-spin mx-auto mb-4" />
                <p className="text-sm text-zinc-600">Loading signals...</p>
              </div>
            ) : signals.length === 0 ? (
              <div className="py-20 text-center" data-testid="signals-empty">
                <Activity className="w-10 h-10 text-zinc-800 mx-auto mb-3" />
                <p className="text-sm text-zinc-500">No signals yet</p>
                <p className="text-xs text-zinc-700 mt-1">
                  {isLive ? "Waiting for agents to generate signals..." : "Demo signals will appear shortly"}
                </p>
              </div>
            ) : (
              <div data-testid="signal-feed">
                {signals.map((signal, i) => (
                  <SignalRow key={`${signal.timestamp}-${i}`} signal={signal} index={i} />
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer info */}
        <div className="flex items-center justify-between mt-4 px-1">
          <div className="flex items-center gap-2">
            {isLive && (
              <>
                <span className="w-1.5 h-1.5 rounded-full bg-[#00FF94] animate-pulse" />
                <span className="text-[10px] text-[#00FF94] font-mono">streaming</span>
              </>
            )}
          </div>
          <p className="text-[10px] text-zinc-700 flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Auto-refresh every {isDemo ? "12" : "8"}s
          </p>
        </div>
      </div>
    </div>
  );
};

export default LiveSignalsPage;
