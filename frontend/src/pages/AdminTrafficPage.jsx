import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  BarChart3, Users, Eye, Zap, Globe, Radio, Heart,
  TrendingUp, ShieldAlert, Activity, RefreshCw, Wifi,
  ArrowUpRight, Filter, ChevronLeft, ChevronRight
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import { toast } from "sonner";
import { API } from "../lib/constants";

const ADMIN_KEY = localStorage.getItem("adminKey") || "alphaai_admin_2026";
const RANGES = [
  { value: "24h", label: "Last 24h" },
  { value: "7d", label: "Last 7 days" },
  { value: "30d", label: "Last 30 days" },
];
const EVENT_TYPES = [
  "all", "page_view", "api_call", "strategy_view", "follow", "unfollow",
  "signal", "ws_connect", "ws_disconnect", "upgrade_prompt",
  "checkout_start", "checkout_success", "error",
];

const CHART_COLORS = {
  page_view: "#7B61FF",
  api_call: "#00FF94",
  ws_connect: "#3b82f6",
  strategy_view: "#FFB800",
  follow: "#ec4899",
  signal: "#8b5cf6",
  error: "#ef4444",
};

// ── KPI Card ───────────────────────────────────────────────────

const KpiCard = ({ icon: Icon, label, value, color = "#7B61FF", testId }) => (
  <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
    <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/40 transition-colors" data-testid={testId}>
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="p-2 rounded-lg" style={{ background: `${color}15` }}>
            <Icon className="w-4 h-4" style={{ color }} />
          </div>
        </div>
        <p className="text-xl font-bold font-mono tracking-tight">{typeof value === "number" ? value.toLocaleString() : value}</p>
        <p className="text-[10px] text-zinc-500 mt-1 uppercase tracking-wider">{label}</p>
      </CardContent>
    </Card>
  </motion.div>
);

// ── Conversion Funnel ──────────────────────────────────────────

const FunnelBar = ({ label, value, max, color }) => {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-zinc-400">{label}</span>
        <span className="font-mono font-bold" style={{ color }}>{value}</span>
      </div>
      <div className="h-2 rounded-full bg-zinc-800/50 overflow-hidden">
        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
};

// ── Event Type Badge ───────────────────────────────────────────

const typeBadgeConfig = {
  page_view: { color: "bg-[#7B61FF]/15 text-[#7B61FF]" },
  api_call: { color: "bg-[#00FF94]/15 text-[#00FF94]" },
  strategy_view: { color: "bg-[#FFB800]/15 text-[#FFB800]" },
  follow: { color: "bg-pink-500/15 text-pink-400" },
  unfollow: { color: "bg-zinc-700 text-zinc-400" },
  signal: { color: "bg-purple-500/15 text-purple-400" },
  ws_connect: { color: "bg-blue-500/15 text-blue-400" },
  ws_disconnect: { color: "bg-zinc-700 text-zinc-400" },
  upgrade_prompt: { color: "bg-[#FFB800]/15 text-[#FFB800]" },
  checkout_start: { color: "bg-[#00FF94]/15 text-[#00FF94]" },
  checkout_success: { color: "bg-[#00FF94]/15 text-[#00FF94]" },
  error: { color: "bg-red-500/15 text-red-400" },
};

// ── Main Page ──────────────────────────────────────────────────

const AdminTrafficPage = () => {
  const [range, setRange] = useState("24h");
  const [summary, setSummary] = useState(null);
  const [timeseries, setTimeseries] = useState([]);
  const [events, setEvents] = useState([]);
  const [eventsTotal, setEventsTotal] = useState(0);
  const [eventsPage, setEventsPage] = useState(1);
  const [eventsPages, setEventsPages] = useState(1);
  const [eventFilter, setEventFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = `admin_key=${ADMIN_KEY}&range=${range}`;
      const [sumRes, tsRes] = await Promise.all([
        fetch(`${API}/admin/traffic/summary?${params}`),
        fetch(`${API}/admin/traffic/timeseries?${params}`),
      ]);
      if (!sumRes.ok || !tsRes.ok) throw new Error("Failed to load traffic data");
      const [sumData, tsData] = await Promise.all([sumRes.json(), tsRes.json()]);
      setSummary(sumData);
      setTimeseries(tsData.series || []);
    } catch (e) {
      setError(e.message);
      toast.error("Failed to load traffic analytics");
    } finally {
      setLoading(false);
    }
  }, [range]);

  const fetchEvents = useCallback(async () => {
    try {
      const typeParam = eventFilter !== "all" ? `&type=${eventFilter}` : "";
      const res = await fetch(`${API}/admin/traffic/events?admin_key=${ADMIN_KEY}&page=${eventsPage}&limit=20${typeParam}`);
      if (res.ok) {
        const data = await res.json();
        setEvents(data.events || []);
        setEventsTotal(data.total || 0);
        setEventsPages(data.pages || 1);
      }
    } catch {
      // silent
    }
  }, [eventsPage, eventFilter]);

  useEffect(() => { fetchAll(); }, [fetchAll]);
  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  // Auto-refresh every 30s
  useEffect(() => {
    const iv = setInterval(() => { fetchAll(); fetchEvents(); }, 30000);
    return () => clearInterval(iv);
  }, [fetchAll, fetchEvents]);

  const s = summary || {};
  const funnelMax = Math.max(s.upgrade_prompts || 0, 1);
  const convRate = s.upgrade_prompts > 0 ? ((s.checkout_successes || 0) / s.upgrade_prompts * 100).toFixed(1) : "0.0";

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="admin-traffic-page">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold font-['Outfit'] flex items-center gap-3" data-testid="traffic-title">
                <div className="p-2.5 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/20">
                  <Activity className="w-6 h-6 text-[#7B61FF]" />
                </div>
                Traffic Analytics
              </h1>
              <p className="text-sm text-zinc-500 mt-2 ml-14">Real-time user activity, API calls, and conversion tracking</p>
            </div>
            <div className="flex items-center gap-3">
              <Select value={range} onValueChange={setRange}>
                <SelectTrigger className="w-[140px] bg-[#0A0A0A] border-zinc-800 text-xs h-8" data-testid="range-select">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-[#0A0A0A] border-zinc-800">
                  {RANGES.map(r => <SelectItem key={r.value} value={r.value} className="text-xs">{r.label}</SelectItem>)}
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm" onClick={() => { fetchAll(); fetchEvents(); }} className="rounded-full border-zinc-800 h-8 px-3 text-xs" data-testid="refresh-btn">
                <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> Refresh
              </Button>
            </div>
          </div>
        </motion.div>

        {error && (
          <Card className="bg-red-500/5 border-red-500/20 mb-6">
            <CardContent className="p-4 text-center text-sm text-red-400">{error}</CardContent>
          </Card>
        )}

        {loading && !summary ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-6 h-6 border-2 border-[#7B61FF] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            {/* ── Section 1: Traffic Overview KPIs ──────────── */}
            <section className="mb-8" data-testid="traffic-overview">
              <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">Traffic Overview</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                <KpiCard icon={Globe} label="Total Events" value={s.total_events || 0} color="#7B61FF" testId="kpi-total-events" />
                <KpiCard icon={Users} label="Unique Users" value={s.unique_users || 0} color="#00FF94" testId="kpi-unique-users" />
                <KpiCard icon={Eye} label="Page Views" value={s.page_views || 0} color="#3b82f6" testId="kpi-page-views" />
                <KpiCard icon={Zap} label="API Calls" value={s.api_calls || 0} color="#FFB800" testId="kpi-api-calls" />
                <KpiCard icon={Wifi} label="WS Connections" value={s.ws_connections || 0} color="#8b5cf6" testId="kpi-ws-connections" />
                <KpiCard icon={Radio} label="Demo Sessions" value={s.demo_sessions || 0} color="#ec4899" testId="kpi-demo-sessions" />
              </div>
            </section>

            {/* ── Section 2: Activity Charts ────────────────── */}
            <section className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="activity-charts">
              {/* Page Views + API Calls Chart */}
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold text-zinc-300">Page Views & API Calls</CardTitle>
                </CardHeader>
                <CardContent className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={timeseries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                      <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#555" }} />
                      <YAxis tick={{ fontSize: 10, fill: "#555" }} />
                      <Tooltip contentStyle={{ background: "#111", border: "1px solid #333", borderRadius: 8, fontSize: 11 }} />
                      <Area type="monotone" dataKey="page_view" stroke="#7B61FF" fill="#7B61FF" fillOpacity={0.15} name="Page Views" />
                      <Area type="monotone" dataKey="api_call" stroke="#00FF94" fill="#00FF94" fillOpacity={0.1} name="API Calls" />
                    </AreaChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Strategy Interactions Chart */}
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold text-zinc-300">Strategy Interactions</CardTitle>
                </CardHeader>
                <CardContent className="h-56">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={timeseries}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                      <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#555" }} />
                      <YAxis tick={{ fontSize: 10, fill: "#555" }} />
                      <Tooltip contentStyle={{ background: "#111", border: "1px solid #333", borderRadius: 8, fontSize: 11 }} />
                      <Bar dataKey="strategy_view" fill="#FFB800" name="Views" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="follow" fill="#ec4899" name="Follows" radius={[3, 3, 0, 0]} />
                      <Bar dataKey="signal" fill="#8b5cf6" name="Signals" radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </section>

            {/* ── Section 3: Conversion Funnel + System Health ─ */}
            <section className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Conversion Funnel */}
              <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="conversion-funnel">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-[#00FF94]" />
                    Conversion Funnel
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <FunnelBar label="Upgrade Prompts" value={s.upgrade_prompts || 0} max={funnelMax} color="#FFB800" />
                  <FunnelBar label="Checkout Starts" value={s.checkout_starts || 0} max={funnelMax} color="#7B61FF" />
                  <FunnelBar label="Checkout Successes" value={s.checkout_successes || 0} max={funnelMax} color="#00FF94" />
                  <div className="pt-2 border-t border-zinc-800/50 flex items-center justify-between">
                    <span className="text-xs text-zinc-500">Conversion Rate</span>
                    <span className="text-sm font-bold font-mono text-[#00FF94]" data-testid="conversion-rate">{convRate}%</span>
                  </div>
                </CardContent>
              </Card>

              {/* System Health */}
              <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="system-health">
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
                    <ShieldAlert className="w-4 h-4 text-[#FFB800]" />
                    System Health
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div>
                      <p className="text-lg font-bold font-mono">{s.avg_latency_ms || 0}<span className="text-[10px] text-zinc-600 ml-0.5">ms</span></p>
                      <p className="text-[10px] text-zinc-500 uppercase">Avg Latency</p>
                    </div>
                    <div>
                      <p className="text-lg font-bold font-mono">{s.p95_latency_ms || 0}<span className="text-[10px] text-zinc-600 ml-0.5">ms</span></p>
                      <p className="text-[10px] text-zinc-500 uppercase">P95 Latency</p>
                    </div>
                    <div>
                      <p className="text-lg font-bold font-mono text-red-400">{s.errors || 0}</p>
                      <p className="text-[10px] text-zinc-500 uppercase">Errors</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4 text-center pt-2 border-t border-zinc-800/50">
                    <div>
                      <p className="text-lg font-bold font-mono">{s.ws_connections || 0}</p>
                      <p className="text-[10px] text-zinc-500 uppercase">WS Connects</p>
                    </div>
                    <div>
                      <p className="text-lg font-bold font-mono text-zinc-500">{s.ws_disconnections || 0}</p>
                      <p className="text-[10px] text-zinc-500 uppercase">WS Disconnects</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </section>

            {/* ── Section 4: Strategy Activity Cards ────────── */}
            <section className="mb-8" data-testid="strategy-activity">
              <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">Strategy Activity</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <KpiCard icon={Eye} label="Strategy Views" value={s.strategy_views || 0} color="#FFB800" testId="kpi-strategy-views" />
                <KpiCard icon={Heart} label="Follows" value={s.follows || 0} color="#ec4899" testId="kpi-follows" />
                <KpiCard icon={ArrowUpRight} label="Unfollows" value={s.unfollows || 0} color="#ef4444" testId="kpi-unfollows" />
                <KpiCard icon={Radio} label="Signals Delivered" value={s.signals_delivered || 0} color="#8b5cf6" testId="kpi-signals" />
              </div>
            </section>

            {/* ── Section 5: Raw Event Table ────────────────── */}
            <section data-testid="event-table">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Raw Events</h2>
                <div className="flex items-center gap-2">
                  <Filter className="w-3.5 h-3.5 text-zinc-600" />
                  <Select value={eventFilter} onValueChange={(v) => { setEventFilter(v); setEventsPage(1); }}>
                    <SelectTrigger className="w-[150px] bg-[#0A0A0A] border-zinc-800 text-xs h-7" data-testid="event-type-filter">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent className="bg-[#0A0A0A] border-zinc-800">
                      {EVENT_TYPES.map(t => <SelectItem key={t} value={t} className="text-xs">{t === "all" ? "All Types" : t}</SelectItem>)}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Card className="bg-[#0A0A0A] border-zinc-800/50 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-zinc-800/50 text-zinc-600 uppercase">
                        <th className="text-left px-4 py-3 font-medium">Type</th>
                        <th className="text-left px-4 py-3 font-medium">User</th>
                        <th className="text-left px-4 py-3 font-medium">Metadata</th>
                        <th className="text-left px-4 py-3 font-medium">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/30">
                      {events.length === 0 ? (
                        <tr><td colSpan={4} className="text-center py-8 text-zinc-600">No events found</td></tr>
                      ) : events.map((ev, i) => {
                        const badgeCfg = typeBadgeConfig[ev.type] || { color: "bg-zinc-700 text-zinc-400" };
                        return (
                          <tr key={ev.id || i} className="hover:bg-white/[0.01] transition-colors" data-testid={`event-row-${i}`}>
                            <td className="px-4 py-2.5">
                              <Badge className={`${badgeCfg.color} text-[9px]`}>{ev.type}</Badge>
                            </td>
                            <td className="px-4 py-2.5 text-zinc-400 font-mono">
                              {ev.user_id ? ev.user_id.slice(0, 8) + "..." : <span className="text-zinc-700">anon</span>}
                            </td>
                            <td className="px-4 py-2.5 text-zinc-500 max-w-[300px] truncate">
                              {ev.metadata ? Object.entries(ev.metadata).filter(([k]) => k !== "demo").map(([k, v]) => `${k}=${v}`).join(", ") : "-"}
                            </td>
                            <td className="px-4 py-2.5 text-zinc-600 whitespace-nowrap">
                              {ev.timestamp ? new Date(ev.timestamp).toLocaleString() : "-"}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>

                {/* Pagination */}
                {eventsPages > 1 && (
                  <div className="flex items-center justify-between px-4 py-3 border-t border-zinc-800/50">
                    <span className="text-[10px] text-zinc-600">{eventsTotal} total events</span>
                    <div className="flex items-center gap-2">
                      <Button variant="outline" size="sm" disabled={eventsPage <= 1} onClick={() => setEventsPage(p => p - 1)} className="h-7 w-7 p-0 border-zinc-800" data-testid="events-prev">
                        <ChevronLeft className="w-3.5 h-3.5" />
                      </Button>
                      <span className="text-[10px] text-zinc-500">{eventsPage} / {eventsPages}</span>
                      <Button variant="outline" size="sm" disabled={eventsPage >= eventsPages} onClick={() => setEventsPage(p => p + 1)} className="h-7 w-7 p-0 border-zinc-800" data-testid="events-next">
                        <ChevronRight className="w-3.5 h-3.5" />
                      </Button>
                    </div>
                  </div>
                )}
              </Card>
            </section>
          </>
        )}
      </div>
    </div>
  );
};

export default AdminTrafficPage;
