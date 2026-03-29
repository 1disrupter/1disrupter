import { useState, useEffect, useCallback, useRef } from "react";
import { motion } from "framer-motion";
import {
  BarChart3, Users, Eye, Zap, Globe, Radio, Heart,
  TrendingUp, ShieldAlert, Activity, RefreshCw, Wifi, WifiOff,
  ArrowUpRight, Filter, ChevronLeft, ChevronRight, Pause, Play,
  Trash2, Terminal, AlertTriangle, BellRing, Volume2, VolumeX
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
import { API, BACKEND_URL } from "../lib/constants";

const ADMIN_KEY = localStorage.getItem("adminKey") || "alphaai_admin_2026";
const RANGES = [
  { value: "24h", label: "Last 24h" },
  { value: "7d", label: "Last 7 days" },
  { value: "30d", label: "Last 30 days" },
];
const EVENT_TYPES = [
  "all", "alerts_only", "page_view", "api_call", "strategy_view", "follow", "unfollow",
  "signal", "ws_connect", "ws_disconnect", "upgrade_prompt",
  "checkout_start", "checkout_success", "error",
];

const MAX_LIVE_EVENTS = 200;
const RECONNECT_BASE_DELAY = 2000;
const MAX_RECONNECT_ATTEMPTS = 8;
const ALERT_PIN_DURATION = 10000; // 10 seconds

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

// ── Conversion Funnel Bar ──────────────────────────────────────

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

// ── Event Type Badge Config ────────────────────────────────────

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
  alert: { color: "bg-red-500/20 text-red-400" },
};

// ── Live Event Feed Line ───────────────────────────────────────

const LiveEventLine = ({ ev, isPinned }) => {
  const isAlert = ev.type === "alert";
  const cfg = typeBadgeConfig[ev.type] || { color: "bg-zinc-700 text-zinc-400" };
  const ts = ev.timestamp ? new Date(ev.timestamp) : new Date();
  const time = ts.toLocaleTimeString("en-US", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" });

  const meta = ev.metadata || {};
  const parts = [];
  if (isAlert) {
    parts.push(meta.alert_type?.replace(/_/g, " ")?.toUpperCase() || "ALERT");
    if (meta.message) parts.push(meta.message);
  } else {
    if (meta.path) parts.push(meta.path);
    if (meta.endpoint) parts.push(meta.endpoint);
    if (meta.strategy_id) parts.push(`strategy:${String(meta.strategy_id).slice(0, 8)}`);
    if (meta.action) parts.push(meta.action);
    if (meta.feature) parts.push(meta.feature);
    if (meta.message) parts.push(String(meta.message).slice(0, 60));
  }
  const desc = parts.join(" — ") || ev.type;

  return (
    <div
      className={`flex items-center gap-2 px-3 py-1 text-[11px] font-mono transition-colors group ${
        isAlert
          ? "bg-red-500/[0.06] border-l-2 border-red-500/40 hover:bg-red-500/[0.1]"
          : "hover:bg-white/[0.02]"
      } ${isPinned ? "bg-red-500/[0.08]" : ""}`}
      data-testid={isAlert ? "live-alert-line" : "live-event-line"}
    >
      {isAlert && <AlertTriangle className="w-3 h-3 text-red-400 shrink-0 animate-pulse" />}
      <span className="text-zinc-700 shrink-0 w-16">[{time}]</span>
      <Badge className={`${cfg.color} text-[8px] px-1.5 py-0 h-4 shrink-0 ${isAlert ? "font-bold" : ""}`}>
        {isAlert ? `ALERT` : ev.type}
      </Badge>
      <span className={`truncate flex-1 ${isAlert ? "text-red-300 font-semibold" : "text-zinc-400"}`}>{desc}</span>
      <span className="text-zinc-700 shrink-0">
        {ev.user_id ? `user:${ev.user_id.slice(0, 6)}` : "sys"}
      </span>
      {meta.demo && <span className="text-[8px] text-pink-500/60 shrink-0">demo</span>}
    </div>
  );
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

  // Live stream state
  const [liveEvents, setLiveEvents] = useState([]);
  const [pinnedAlerts, setPinnedAlerts] = useState([]); // alerts pinned to top
  const [liveStatus, setLiveStatus] = useState("disconnected");
  const [livePaused, setLivePaused] = useState(false);
  const [liveTypeFilter, setLiveTypeFilter] = useState("all");
  const [liveDemoFilter, setLiveDemoFilter] = useState("all");
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [activeAlerts, setActiveAlerts] = useState([]);
  const [contractStatus, setContractStatus] = useState(null);
  const wsRef = useRef(null);
  const reconnectCount = useRef(0);
  const reconnectTimer = useRef(null);
  const feedRef = useRef(null);
  const pausedRef = useRef(false);

  useEffect(() => { pausedRef.current = livePaused; }, [livePaused]);

  // ── Data fetching ────────────────────────────────────────────

  const fetchAll = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = `admin_key=${ADMIN_KEY}&range=${range}`;
      const [sumRes, tsRes, alertsRes, contractRes] = await Promise.all([
        fetch(`${API}/admin/traffic/summary?${params}`),
        fetch(`${API}/admin/traffic/timeseries?${params}`),
        fetch(`${API}/admin/traffic/active-alerts?${params}`),
        fetch(`${API}/admin/contract/status?admin_key=${ADMIN_KEY}`),
      ]);
      if (!sumRes.ok || !tsRes.ok) throw new Error("Failed to load traffic data");
      const [sumData, tsData] = await Promise.all([sumRes.json(), tsRes.json()]);
      setSummary(sumData);
      setTimeseries(tsData.series || []);
      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setActiveAlerts(alertsData.active_alerts || []);
      }
      if (contractRes.ok) {
        const cData = await contractRes.json();
        setContractStatus(cData);
      }
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

  useEffect(() => {
    const iv = setInterval(() => { fetchAll(); fetchEvents(); }, 30000);
    return () => clearInterval(iv);
  }, [fetchAll, fetchEvents]);

  // ── Live Event Stream WebSocket ──────────────────────────────

  useEffect(() => {
    const wsUrl = BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://");
    const fullUrl = `${wsUrl}/api/ws/admin/events?admin_key=${ADMIN_KEY}`;

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;
      setLiveStatus("reconnecting");

      const ws = new WebSocket(fullUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setLiveStatus("connected");
        reconnectCount.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "connected" || data.type === "pong" || data.type === "heartbeat") return;

          const isAlert = data.type === "alert";

          if (!pausedRef.current) {
            setLiveEvents((prev) => [...prev, data].slice(-MAX_LIVE_EVENTS));
          }

          // Pin alerts to top for ALERT_PIN_DURATION
          if (isAlert) {
            const pinId = data.id || Date.now();
            setPinnedAlerts((prev) => [...prev, { ...data, _pinId: pinId }]);

            // Show alert toast
            toast.error(data.metadata?.message || "Alert triggered", {
              description: data.metadata?.alert_type?.replace(/_/g, " ") || "System Alert",
              duration: 8000,
            });

            // Refresh active alerts
            fetch(`${API}/admin/traffic/active-alerts?admin_key=${ADMIN_KEY}`)
              .then(r => r.json())
              .then(d => setActiveAlerts(d.active_alerts || []))
              .catch(() => {});

            // Remove pin after ALERT_PIN_DURATION
            setTimeout(() => {
              setPinnedAlerts((prev) => prev.filter((p) => p._pinId !== pinId));
            }, ALERT_PIN_DURATION);
          }
        } catch {
          // ignore
        }
      };

      ws.onclose = (event) => {
        wsRef.current = null;
        if (event.code === 4003) {
          setLiveStatus("disconnected");
          return;
        }
        setLiveStatus("reconnecting");
        if (reconnectCount.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectCount.current += 1;
          const delay = RECONNECT_BASE_DELAY * Math.pow(1.5, reconnectCount.current - 1);
          reconnectTimer.current = setTimeout(connect, delay);
        } else {
          setLiveStatus("disconnected");
        }
      };

      ws.onerror = () => {};
    };

    connect();

    const pingIv = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "ping" }));
      }
    }, 45000);

    return () => {
      clearInterval(pingIv);
      clearTimeout(reconnectTimer.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    if (!livePaused && feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [liveEvents, livePaused]);

  // ── Filtered live events ─────────────────────────────────────

  const filteredLiveEvents = liveEvents.filter((ev) => {
    if (liveTypeFilter === "alerts_only" && ev.type !== "alert") return false;
    if (liveTypeFilter !== "all" && liveTypeFilter !== "alerts_only" && ev.type !== liveTypeFilter) return false;
    if (liveDemoFilter === "demo" && !ev.metadata?.demo) return false;
    if (liveDemoFilter === "live" && ev.metadata?.demo) return false;
    return true;
  });

  const s = summary || {};
  const funnelMax = Math.max(s.upgrade_prompts || 0, 1);
  const convRate = s.upgrade_prompts > 0 ? ((s.checkout_successes || 0) / s.upgrade_prompts * 100).toFixed(1) : "0.0";

  const statusColors = {
    connected: { bg: "bg-[#00FF94]/10", text: "text-[#00FF94]", icon: Wifi, label: "Connected" },
    reconnecting: { bg: "bg-[#FFB800]/10", text: "text-[#FFB800]", icon: RefreshCw, label: "Reconnecting" },
    disconnected: { bg: "bg-red-500/10", text: "text-red-400", icon: WifiOff, label: "Disconnected" },
  };
  const st = statusColors[liveStatus];

  const alertCount = liveEvents.filter(e => e.type === "alert").length;

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
                {activeAlerts.length > 0 && (
                  <Badge className="bg-red-500/20 text-red-400 text-[10px] gap-1 animate-pulse ml-2" data-testid="alert-active-badge">
                    <AlertTriangle className="w-3 h-3" />
                    {activeAlerts.length} ALERT{activeAlerts.length > 1 ? "S" : ""} ACTIVE
                  </Badge>
                )}
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

        {/* Active Alerts Banner */}
        {activeAlerts.length > 0 && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="bg-red-500/[0.05] border-red-500/20 mb-6" data-testid="active-alerts-banner">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="p-2 rounded-lg bg-red-500/10 shrink-0">
                  <BellRing className="w-5 h-5 text-red-400 animate-pulse" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-red-300">Active Alerts</p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {activeAlerts.map(a => (
                      <Badge key={a} className="bg-red-500/15 text-red-400 text-[9px]">{a.replace(/_/g, " ")}</Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

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

            {/* ── Contract Status ────────────────────────────── */}
            {contractStatus && (
              <section className="mb-8" data-testid="contract-status-section">
                <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">Smart Contract</h2>
                <Card className="bg-[#0A0A0A] border-zinc-800/50">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between flex-wrap gap-3">
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${contractStatus.health === "ok" ? "bg-[#00FF94]" : contractStatus.deployed ? "bg-[#FFB800]" : "bg-zinc-600"}`} />
                        <div>
                          <p className="text-sm font-medium text-zinc-300" data-testid="contract-network">
                            {contractStatus.network?.toUpperCase() || "Sepolia"} {contractStatus.deployed ? "" : "— Not Deployed"}
                          </p>
                          {contractStatus.contract_address ? (
                            <a href={contractStatus.explorer_url} target="_blank" rel="noopener noreferrer" className="text-[11px] font-mono text-[#7B61FF] hover:underline" data-testid="contract-address-link">
                              {contractStatus.contract_address}
                            </a>
                          ) : (
                            <p className="text-[11px] text-zinc-600 font-mono" data-testid="contract-not-deployed">Awaiting deployment</p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-[10px]">
                        {contractStatus.verified && <Badge className="bg-[#00FF94]/10 text-[#00FF94] text-[9px]">Verified</Badge>}
                        <span className="text-zinc-600">ABI: {contractStatus.abi_functions || 0} functions</span>
                        {contractStatus.rpc_connected && <span className="text-zinc-500">Block: {contractStatus.latest_block?.toLocaleString()}</span>}
                        <Badge className={contractStatus.health === "ok" ? "bg-[#00FF94]/10 text-[#00FF94] text-[9px]" : contractStatus.health === "not_configured" ? "bg-zinc-800 text-zinc-500 text-[9px]" : "bg-[#FFB800]/10 text-[#FFB800] text-[9px]"} data-testid="contract-health">
                          {contractStatus.health}
                        </Badge>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </section>
            )}

            {/* ── Section 2: Activity Charts ────────────────── */}
            <section className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4" data-testid="activity-charts">
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

            {/* ── Section 4: LIVE EVENT STREAM ──────────────── */}
            <section className="mb-8" data-testid="live-event-stream">
              <Card className="bg-[#0A0A0A] border-zinc-800/50 overflow-hidden">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between flex-wrap gap-3">
                    <CardTitle className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
                      <Terminal className="w-4 h-4 text-[#7B61FF]" />
                      Live Event Stream
                      <Badge className={`${st.bg} ${st.text} text-[9px] gap-1`} data-testid="live-stream-status">
                        <st.icon className={`w-3 h-3 ${liveStatus === "reconnecting" ? "animate-spin" : ""}`} />
                        {st.label}
                      </Badge>
                      {alertCount > 0 && (
                        <Badge className="bg-red-500/15 text-red-400 text-[9px] gap-1" data-testid="live-alert-count">
                          <AlertTriangle className="w-3 h-3" />
                          {alertCount}
                        </Badge>
                      )}
                      <span className="text-[10px] text-zinc-600 font-normal font-mono ml-1">{filteredLiveEvents.length} events</span>
                    </CardTitle>

                    <div className="flex items-center gap-2">
                      {/* Type filter — includes alerts_only */}
                      <Select value={liveTypeFilter} onValueChange={setLiveTypeFilter}>
                        <SelectTrigger className="w-[130px] bg-[#111] border-zinc-800 text-[10px] h-7" data-testid="live-type-filter">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#0A0A0A] border-zinc-800">
                          {EVENT_TYPES.map(t => (
                            <SelectItem key={t} value={t} className="text-xs">
                              {t === "all" ? "All Types" : t === "alerts_only" ? "Alerts Only" : t}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>

                      {/* Demo filter */}
                      <Select value={liveDemoFilter} onValueChange={setLiveDemoFilter}>
                        <SelectTrigger className="w-[90px] bg-[#111] border-zinc-800 text-[10px] h-7" data-testid="live-demo-filter">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-[#0A0A0A] border-zinc-800">
                          <SelectItem value="all" className="text-xs">All</SelectItem>
                          <SelectItem value="demo" className="text-xs">Demo</SelectItem>
                          <SelectItem value="live" className="text-xs">Live</SelectItem>
                        </SelectContent>
                      </Select>

                      {/* Sound toggle */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSoundEnabled(p => !p)}
                        className={`h-7 w-7 p-0 border-zinc-800 ${soundEnabled ? "text-[#FFB800] border-[#FFB800]/30" : "text-zinc-600"}`}
                        data-testid="live-sound-toggle"
                        title={soundEnabled ? "Mute alerts" : "Enable alert sounds"}
                      >
                        {soundEnabled ? <Volume2 className="w-3 h-3" /> : <VolumeX className="w-3 h-3" />}
                      </Button>

                      {/* Pause / Resume */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setLivePaused(p => !p)}
                        className={`h-7 px-2.5 border-zinc-800 text-[10px] ${livePaused ? "text-[#FFB800] border-[#FFB800]/30" : "text-zinc-400"}`}
                        data-testid="live-pause-btn"
                      >
                        {livePaused ? <Play className="w-3 h-3 mr-1" /> : <Pause className="w-3 h-3 mr-1" />}
                        {livePaused ? "Resume" : "Pause"}
                      </Button>

                      {/* Clear */}
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => { setLiveEvents([]); setPinnedAlerts([]); }}
                        className="h-7 px-2.5 border-zinc-800 text-[10px] text-zinc-400"
                        data-testid="live-clear-btn"
                      >
                        <Trash2 className="w-3 h-3 mr-1" /> Clear
                      </Button>
                    </div>
                  </div>
                </CardHeader>

                <CardContent className="p-0">
                  {/* Pinned alerts */}
                  {pinnedAlerts.length > 0 && (
                    <div className="border-b border-red-500/20 bg-red-500/[0.03]" data-testid="pinned-alerts-section">
                      <div className="px-3 py-1 text-[9px] text-red-400/80 uppercase tracking-wider font-semibold flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3" /> Pinned Alerts
                      </div>
                      {pinnedAlerts.map((ev, i) => (
                        <LiveEventLine key={ev._pinId || i} ev={ev} isPinned />
                      ))}
                    </div>
                  )}

                  <div
                    ref={feedRef}
                    className="h-72 overflow-y-auto bg-[#060606] border-t border-zinc-800/30 font-mono"
                    data-testid="live-feed-container"
                  >
                    {filteredLiveEvents.length === 0 ? (
                      <div className="flex items-center justify-center h-full text-zinc-700 text-xs">
                        {liveStatus === "connected"
                          ? "Waiting for events..."
                          : liveStatus === "reconnecting"
                          ? "Reconnecting to event stream..."
                          : "Disconnected from event stream"}
                      </div>
                    ) : (
                      <div className="divide-y divide-zinc-900/50">
                        {filteredLiveEvents.map((ev, i) => (
                          <LiveEventLine key={`${ev.id || ev.timestamp}-${i}`} ev={ev} isPinned={false} />
                        ))}
                      </div>
                    )}
                  </div>

                  {livePaused && (
                    <div className="bg-[#FFB800]/5 border-t border-[#FFB800]/20 px-4 py-1.5 flex items-center justify-center gap-2" data-testid="live-paused-banner">
                      <Pause className="w-3 h-3 text-[#FFB800]" />
                      <span className="text-[10px] text-[#FFB800]">Stream paused — new events are buffered</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            </section>

            {/* ── Section 5: Strategy Activity Cards ────────── */}
            <section className="mb-8" data-testid="strategy-activity">
              <h2 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider mb-4">Strategy Activity</h2>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <KpiCard icon={Eye} label="Strategy Views" value={s.strategy_views || 0} color="#FFB800" testId="kpi-strategy-views" />
                <KpiCard icon={Heart} label="Follows" value={s.follows || 0} color="#ec4899" testId="kpi-follows" />
                <KpiCard icon={ArrowUpRight} label="Unfollows" value={s.unfollows || 0} color="#ef4444" testId="kpi-unfollows" />
                <KpiCard icon={Radio} label="Signals Delivered" value={s.signals_delivered || 0} color="#8b5cf6" testId="kpi-signals" />
              </div>
            </section>

            {/* ── Section 6: Raw Event Table ────────────────── */}
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
                      {EVENT_TYPES.map(t => <SelectItem key={t} value={t} className="text-xs">{t === "all" ? "All Types" : t === "alerts_only" ? "Alerts Only" : t}</SelectItem>)}
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
                        const isAlert = ev.type === "alert";
                        const badgeCfg = typeBadgeConfig[ev.type] || { color: "bg-zinc-700 text-zinc-400" };
                        return (
                          <tr key={ev.id || i} className={`transition-colors ${isAlert ? "bg-red-500/[0.04] hover:bg-red-500/[0.08]" : "hover:bg-white/[0.01]"}`} data-testid={`event-row-${i}`}>
                            <td className="px-4 py-2.5">
                              <div className="flex items-center gap-1.5">
                                {isAlert && <AlertTriangle className="w-3 h-3 text-red-400" />}
                                <Badge className={`${badgeCfg.color} text-[9px] ${isAlert ? "font-bold" : ""}`}>{ev.type}</Badge>
                              </div>
                            </td>
                            <td className="px-4 py-2.5 text-zinc-400 font-mono">
                              {ev.user_id ? ev.user_id.slice(0, 8) + "..." : <span className="text-zinc-700">sys</span>}
                            </td>
                            <td className={`px-4 py-2.5 max-w-[300px] truncate ${isAlert ? "text-red-300 font-semibold" : "text-zinc-500"}`}>
                              {ev.metadata ? Object.entries(ev.metadata).filter(([k]) => k !== "demo").map(([k, v]) => `${k}=${typeof v === "string" ? v.slice(0, 40) : v}`).join(", ") : "-"}
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
