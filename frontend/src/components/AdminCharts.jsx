import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Area, AreaChart, ComposedChart,
  Legend
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import {
  Users, DollarSign, TrendingUp, BarChart3, Eye, Cpu,
  Layers, Zap, Crown, Activity
} from "lucide-react";
import { Badge } from "../components/ui/badge";
import { API } from "../lib/constants";
import axios from "axios";

const ADMIN_KEY = localStorage.getItem("adminKey") || "alphaai_admin_2026";

const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#1a1a1a] border border-zinc-700 rounded-lg px-3 py-2 shadow-xl text-xs">
      <p className="text-zinc-400 mb-1">{label}</p>
      {payload.map((p, i) => (
        <p key={i} style={{ color: p.color }} className="font-mono">
          {p.name}: {typeof p.value === "number" && p.name.includes("$") ? `$${p.value.toFixed(2)}` : p.value}
        </p>
      ))}
    </div>
  );
};

/* ─────── Analytics Stat Cards with Range Filter ─────── */

const StatCard = ({ icon: Icon, label, value, color, bg, delay = 0 }) => (
  <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay, duration: 0.3 }}>
    <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/60 transition-all duration-300 group" data-testid={`stat-${label.toLowerCase().replace(/\s/g, "-")}`}>
      <CardContent className="p-4">
        <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center mb-2 group-hover:scale-110 transition-transform`}>
          <Icon className={`w-4 h-4 ${color}`} />
        </div>
        <p className="text-[11px] text-zinc-500 uppercase tracking-wider">{label}</p>
        <p className="text-xl font-bold font-['JetBrains_Mono'] text-zinc-100 mt-0.5">{typeof value === "number" ? value.toLocaleString() : value}</p>
      </CardContent>
    </Card>
  </motion.div>
);

export const AnalyticsFilteredCards = () => {
  const [range, setRange] = useState("7d");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/admin/analytics-filtered?admin_key=${ADMIN_KEY}&range=${range}`);
      setData(res.data);
    } catch { /* ignore */ }
    setLoading(false);
  }, [range]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const cards = data ? [
    { icon: Users, label: "Total Users", value: data.total_users, color: "text-[#7B61FF]", bg: "bg-[#7B61FF]/10" },
    { icon: Crown, label: "Pro Users", value: data.pro_users, color: "text-emerald-400", bg: "bg-emerald-400/10" },
    { icon: Zap, label: "Elite Users", value: data.elite_users, color: "text-amber-400", bg: "bg-amber-400/10" },
    { icon: Layers, label: "Active Subs", value: data.active_subscriptions, color: "text-sky-400", bg: "bg-sky-400/10" },
    { icon: Activity, label: "Signals", value: data.signals, color: "text-rose-400", bg: "bg-rose-400/10" },
    { icon: Eye, label: "Page Views", value: data.page_views, color: "text-[#7B61FF]", bg: "bg-[#7B61FF]/10" },
    { icon: Cpu, label: "API Calls", value: data.api_calls, color: "text-teal-400", bg: "bg-teal-400/10" },
  ] : [];

  return (
    <div className="space-y-4" data-testid="analytics-filtered-section">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-zinc-300">Platform Metrics</h3>
        <div className="flex items-center gap-2">
          {data?.demo_mode && <Badge className="bg-[#7B61FF]/15 text-[#7B61FF] text-[10px]">Demo</Badge>}
          <Select value={range} onValueChange={setRange}>
            <SelectTrigger className="w-28 h-8 text-xs bg-[#0A0A0A] border-zinc-800" data-testid="analytics-range-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="today">Today</SelectItem>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>
      <AnimatePresence mode="wait">
        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3" key="skeleton">
            {[...Array(7)].map((_, i) => (
              <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-4">
                  <div className="w-8 h-8 rounded-lg bg-zinc-800 animate-pulse mb-2" />
                  <div className="h-3 w-16 bg-zinc-800 rounded animate-pulse mb-2" />
                  <div className="h-6 w-10 bg-zinc-800 rounded animate-pulse" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <motion.div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3" key={range} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2 }}>
            {cards.map((c, i) => <StatCard key={c.label} {...c} delay={i * 0.03} />)}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

/* ─────── MRR & Subscription Trend Charts ─────── */

export const MRRTrendCharts = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/admin/mrr-trends?admin_key=${ADMIN_KEY}`)
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid md:grid-cols-2 gap-4">
        {[...Array(2)].map((_, i) => (
          <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-6"><div className="h-48 bg-zinc-900 rounded animate-pulse" /></CardContent>
          </Card>
        ))}
      </div>
    );
  }
  if (!data?.trends?.length) return null;

  const trends = data.trends.map(t => ({
    ...t,
    date: t.date.slice(5), // MM-DD
  }));

  return (
    <div className="space-y-4" data-testid="mrr-trends-section">
      <h3 className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
        <DollarSign className="w-4 h-4 text-emerald-400" /> Revenue & Subscription Trends
        {data.demo_mode && <Badge className="bg-[#7B61FF]/15 text-[#7B61FF] text-[10px]">Demo</Badge>}
      </h3>
      <div className="grid md:grid-cols-2 gap-4">
        {/* MRR Over Time */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-zinc-400 uppercase tracking-wider">MRR Over Time</CardTitle>
          </CardHeader>
          <CardContent className="pt-0" data-testid="mrr-chart">
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="mrrGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00FF94" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#00FF94" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 10 }} />
                <YAxis tick={{ fill: "#555", fontSize: 10 }} tickFormatter={v => `$${v}`} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="mrr" name="$ MRR" stroke="#00FF94" fill="url(#mrrGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* New Subs vs Cancellations */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-zinc-400 uppercase tracking-wider">Subscriptions vs Cancellations</CardTitle>
          </CardHeader>
          <CardContent className="pt-0" data-testid="subs-chart">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 10 }} />
                <YAxis tick={{ fill: "#555", fontSize: 10 }} allowDecimals={false} />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 10, color: "#666" }} />
                <Bar dataKey="new_subscriptions" name="New" fill="#7B61FF" radius={[2, 2, 0, 0]} />
                <Bar dataKey="cancellations" name="Canceled" fill="#ef4444" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Net Revenue */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-zinc-400 uppercase tracking-wider">Net Revenue (Daily)</CardTitle>
          </CardHeader>
          <CardContent className="pt-0" data-testid="net-revenue-chart">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 10 }} />
                <YAxis tick={{ fill: "#555", fontSize: 10 }} tickFormatter={v => `$${v}`} />
                <Tooltip content={<ChartTooltip />} />
                <Bar dataKey="net_revenue" name="$ Net Revenue" fill="#22d3ee" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Cumulative Revenue */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-zinc-400 uppercase tracking-wider">Cumulative Revenue</CardTitle>
          </CardHeader>
          <CardContent className="pt-0" data-testid="cumulative-revenue-chart">
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trends}>
                <defs>
                  <linearGradient id="cumGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#7B61FF" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#7B61FF" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 10 }} />
                <YAxis tick={{ fill: "#555", fontSize: 10 }} tickFormatter={v => `$${v}`} />
                <Tooltip content={<ChartTooltip />} />
                <Area type="monotone" dataKey="cumulative_revenue" name="$ Total Revenue" stroke="#7B61FF" fill="url(#cumGrad)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

/* ─────── Signal History Chart ─────── */

export const SignalHistoryChart = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/admin/signal-history?admin_key=${ADMIN_KEY}`)
      .then(r => setData(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <Card className="bg-[#0A0A0A] border-zinc-800/50">
        <CardContent className="p-6"><div className="h-48 bg-zinc-900 rounded animate-pulse" /></CardContent>
      </Card>
    );
  }
  if (!data?.signals?.length) {
    return (
      <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="signal-history-empty">
        <CardContent className="py-12 text-center">
          <Activity className="w-8 h-8 text-zinc-700 mx-auto mb-2" />
          <p className="text-zinc-500 text-sm">No signal data available</p>
        </CardContent>
      </Card>
    );
  }

  const signals = data.signals.map(s => ({ ...s, date: s.date.slice(5) }));

  return (
    <div className="space-y-4" data-testid="signal-history-section">
      <h3 className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-rose-400" /> Signal Volume (30d)
        {data.demo_mode && <Badge className="bg-[#7B61FF]/15 text-[#7B61FF] text-[10px]">Demo</Badge>}
      </h3>
      <Card className="bg-[#0A0A0A] border-zinc-800/50">
        <CardContent className="pt-4" data-testid="signal-history-chart">
          <ResponsiveContainer width="100%" height={220}>
            <ComposedChart data={signals}>
              <CartesianGrid strokeDasharray="3 3" stroke="#222" />
              <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 10 }} />
              <YAxis tick={{ fill: "#555", fontSize: 10 }} allowDecimals={false} />
              <Tooltip content={<ChartTooltip />} />
              <Legend wrapperStyle={{ fontSize: 10, color: "#666" }} />
              <Bar dataKey="count" name="Daily Signals" fill="#f43f5e" opacity={0.7} radius={[2, 2, 0, 0]} />
              <Line type="monotone" dataKey="ma7" name="7d Avg" stroke="#facc15" strokeWidth={2} dot={false} />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};
