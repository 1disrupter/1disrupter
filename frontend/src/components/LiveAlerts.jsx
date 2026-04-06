import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Radio, ArrowUpRight, ArrowDownRight, X, Target, ShieldAlert, Clock
} from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
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

const AlertRow = ({ alert, index }) => {
  const meta = actionMeta[alert.action] || actionMeta.LONG;
  const Icon = meta.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, delay: index < 12 ? index * 0.025 : 0 }}
    >
      <div className="flex items-center gap-4 px-5 py-3.5 border-b border-zinc-800/40 hover:bg-white/[0.015] transition-colors" data-testid={`live-alert-${index}`}>
        <div className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0" style={{ background: meta.bg }}>
          <Icon className="w-4 h-4" style={{ color: meta.color }} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold tracking-wider px-1.5 py-0.5 rounded" style={{ background: meta.bg, color: meta.color }}>{meta.label}</span>
            <span className="text-sm font-mono font-semibold text-zinc-100">{alert.asset}</span>
            {alert.confidence != null && <span className="text-[10px] text-zinc-500 font-mono">{alert.confidence}%</span>}
          </div>
          <p className="text-xs text-zinc-500 mt-0.5 truncate max-w-lg">{alert.message}</p>
        </div>
        <div className="hidden md:block text-right min-w-[110px]">
          <p className="text-[10px] text-[#7B61FF] font-medium truncate">{alert.strategy_name || alert.agent || ""}</p>
        </div>
        <div className="text-right min-w-[80px]">
          {alert.price ? <p className="text-xs font-mono font-semibold text-zinc-200">${Number(alert.price).toLocaleString(undefined, { maximumFractionDigits: 2 })}</p> : <span className="text-[10px] text-zinc-700">—</span>}
        </div>
        <div className="text-right min-w-[56px]">
          <span className="text-[10px] text-zinc-600 font-mono">{timeAgo(alert.timestamp)}</span>
        </div>
      </div>
    </motion.div>
  );
};

const LiveAlerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAlerts = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/alerts/live?limit=40`);
      setAlerts(res.data.alerts || []);
    } catch { /* keep existing */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetchAlerts();
    const id = setInterval(fetchAlerts, 12000);
    return () => clearInterval(id);
  }, [fetchAlerts]);

  if (loading) {
    return (
      <div className="space-y-3" data-testid="alerts-loading">
        {[0, 1, 2, 3, 4].map(i => <div key={i} className="h-16 bg-[#0A0A0A] border border-zinc-800/40 rounded-xl animate-pulse" />)}
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="text-center py-16" data-testid="alerts-empty">
        <Radio className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
        <p className="text-sm text-zinc-500">No alerts in the last 24 hours</p>
        <p className="text-xs text-zinc-700 mt-1">Waiting for agents to generate signals</p>
      </div>
    );
  }

  const longCount = alerts.filter(a => a.action === "LONG").length;
  const shortCount = alerts.filter(a => a.action === "SHORT").length;

  return (
    <div>
      {/* Stats */}
      <div className="flex items-center gap-4 mb-4 text-[10px] font-mono text-zinc-600">
        <span>{alerts.length} alerts</span>
        <span className="text-[#00FF94]">{longCount} long</span>
        <span className="text-red-400">{shortCount} short</span>
        <div className="ml-auto flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-[#00FF94] animate-pulse" />
          <span className="text-[#00FF94]">auto-refresh 12s</span>
        </div>
      </div>
      {/* Feed */}
      <Card className="bg-[#0A0A0A] border-zinc-800/50 overflow-hidden">
        <div className="flex items-center gap-4 px-5 py-2 border-b border-zinc-800/60 bg-zinc-900/30">
          <div className="w-9" />
          <div className="flex-1 text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Signal</div>
          <div className="hidden md:block min-w-[110px] text-right text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Agent</div>
          <div className="min-w-[80px] text-right text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Price</div>
          <div className="min-w-[56px] text-right text-[9px] text-zinc-600 uppercase tracking-widest font-medium">Time</div>
        </div>
        <CardContent className="p-0" data-testid="live-alert-feed">
          {alerts.map((a, i) => <AlertRow key={`${a.timestamp}-${i}`} alert={a} index={i} />)}
        </CardContent>
      </Card>
    </div>
  );
};

export default LiveAlerts;
