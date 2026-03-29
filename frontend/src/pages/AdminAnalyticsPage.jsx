import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  BarChart3, Users, TrendingUp, Zap, Globe, Eye,
  ArrowUpRight, ArrowDownRight, RefreshCw, Share2, Clock, Activity,
  Target, Save, Check, AlertTriangle
} from "lucide-react";
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { Progress } from "../components/ui/progress";
import { toast } from "sonner";
import { API } from "../lib/constants";

const ADMIN_KEY = localStorage.getItem("adminKey") || "alphaai_admin_2026";
const PERIODS = [
  { value: "24h", label: "24h" },
  { value: "7d", label: "7 days" },
  { value: "30d", label: "30 days" },
  { value: "all", label: "All time" },
];

const PIE_COLORS = ["#7B61FF", "#00FF94", "#FFB800", "#ef4444", "#3b82f6", "#8b5cf6"];

const KpiCard = ({ icon: Icon, label, value, sub, color = "#7B61FF", testId }) => (
  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
    <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/40 transition-colors" data-testid={testId}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className={`p-2 rounded-lg`} style={{ background: `${color}15` }}>
            <Icon className="w-4 h-4" style={{ color }} />
          </div>
        </div>
        <p className="text-2xl font-bold font-mono tracking-tight">{value}</p>
        <p className="text-xs text-zinc-500 mt-1">{label}</p>
        {sub && <p className="text-[10px] text-zinc-600 mt-0.5">{sub}</p>}
      </CardContent>
    </Card>
  </motion.div>
);

const AdminAnalyticsPage = () => {
  const [period, setPeriod] = useState("30d");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [liveEvents, setLiveEvents] = useState([]);

  // Goal tracker state
  const [goals, setGoals] = useState({ k_factor_target: 1.0, demo_signup_target: 15.0, demo_pro_target: 5.0 });
  const [editGoals, setEditGoals] = useState(null); // null = not editing
  const [savingGoals, setSavingGoals] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/admin/analytics?admin_key=${ADMIN_KEY}&period=${period}`);
      if (!res.ok) throw new Error(res.status === 403 ? "Admin access denied" : `Error ${res.status}`);
      const json = await res.json();
      setData(json);
      setLiveEvents(json.recent_events || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Fetch goals on mount
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${API}/admin/analytics/goals?admin_key=${ADMIN_KEY}`);
        if (res.ok) { const g = await res.json(); setGoals(g); }
      } catch { /* use defaults */ }
    })();
  }, []);

  const saveGoals = async () => {
    setSavingGoals(true);
    try {
      const res = await fetch(`${API}/admin/analytics/goals?admin_key=${ADMIN_KEY}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(editGoals),
      });
      if (!res.ok) throw new Error("Save failed");
      const saved = await res.json();
      setGoals({ k_factor_target: saved.k_factor_target, demo_signup_target: saved.demo_signup_target, demo_pro_target: saved.demo_pro_target });
      setEditGoals(null);
      toast.success("Goals saved!");
    } catch (e) {
      toast.error("Failed to save goals");
    } finally {
      setSavingGoals(false);
    }
  };

  // Simulate live event polling every 15s
  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/admin/analytics?admin_key=${ADMIN_KEY}&period=24h`);
        if (res.ok) {
          const json = await res.json();
          setLiveEvents(json.recent_events || []);
        }
      } catch { /* silent */ }
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  const kpi = data?.kpi || {};

  if (error) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4">
        <div className="max-w-7xl mx-auto text-center py-20">
          <div className="w-16 h-16 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-4">
            <span className="text-red-400 text-2xl">!</span>
          </div>
          <h2 className="text-lg font-semibold mb-2 text-zinc-300">{error === "Admin access denied" ? "Access Denied" : "Error Loading Analytics"}</h2>
          <p className="text-sm text-zinc-500 mb-4">{error === "Admin access denied" ? "You need admin privileges to view this page." : error}</p>
          <Button onClick={fetchData} variant="outline" className="rounded-full border-zinc-700"><RefreshCw className="w-4 h-4 mr-2" /> Retry</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="admin-analytics-page">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 rounded-xl bg-[#7B61FF]/10">
                  <BarChart3 className="w-6 h-6 text-[#7B61FF]" />
                </div>
                <h1 className="text-2xl sm:text-3xl font-bold font-['Outfit'] tracking-tight">Demo Analytics</h1>
                <Badge className="bg-red-500/15 text-red-400 text-[10px]">Admin</Badge>
              </div>
              <p className="text-sm text-zinc-500">Track demo link performance, conversion funnels, and viral growth</p>
            </div>
            <div className="flex items-center gap-2">
              {PERIODS.map(p => (
                <button
                  key={p.value}
                  onClick={() => setPeriod(p.value)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${period === p.value ? "bg-[#7B61FF]/15 border-[#7B61FF]/40 text-[#7B61FF]" : "border-zinc-800 text-zinc-500 hover:border-zinc-600"}`}
                  data-testid={`period-${p.value}`}
                >
                  {p.label}
                </button>
              ))}
              <Button onClick={fetchData} size="sm" variant="ghost" className="rounded-full text-zinc-500" data-testid="refresh-analytics"><RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /></Button>
            </div>
          </div>
        </motion.div>

        {loading && !data ? (
          <div className="space-y-4 animate-pulse">
            {[1, 2, 3].map(i => <div key={i} className="h-24 rounded-xl bg-zinc-800/30" />)}
          </div>
        ) : (
          <>
            {/* KPI Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <KpiCard icon={Eye} label="Demo Link Opens" value={kpi.demo_opens?.toLocaleString() || "0"} sub={`${period} period`} color="#7B61FF" testId="kpi-demo-opens" />
              <KpiCard icon={Users} label="Demo → Signup" value={`${kpi.demo_signup_rate || 0}%`} sub={`${kpi.total_signups || 0} signups`} color="#00FF94" testId="kpi-signup-rate" />
              <KpiCard icon={TrendingUp} label="Demo → Pro" value={`${kpi.demo_pro_rate || 0}%`} sub={`${kpi.total_pro || 0} pro users`} color="#FFB800" testId="kpi-pro-rate" />
              <KpiCard icon={Zap} label="Viral K-Factor" value={kpi.k_factor || "0.00"} sub={kpi.k_factor >= 1 ? "Viral growth!" : "Below viral threshold"} color={kpi.k_factor >= 1 ? "#00FF94" : "#ef4444"} testId="kpi-k-factor" />
            </div>

            {/* Charts Row */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {/* Opens Over Time */}
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="chart-opens-over-time">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2"><Activity className="w-4 h-4 text-[#7B61FF]" /> Demo Opens Over Time</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={220}>
                      <AreaChart data={data?.opens_over_time || []}>
                        <defs>
                          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#7B61FF" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#7B61FF" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                        <XAxis dataKey="date" tick={{ fill: "#52525b", fontSize: 10 }} />
                        <YAxis tick={{ fill: "#52525b", fontSize: 10 }} />
                        <Tooltip contentStyle={{ background: "#0A0A0A", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }} />
                        <Area type="monotone" dataKey="count" stroke="#7B61FF" fill="url(#areaGrad)" strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Pages Distribution */}
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="chart-pages">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2"><Globe className="w-4 h-4 text-[#00FF94]" /> Entry Pages</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={(data?.pages_per_session || []).slice(0, 8)} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                        <XAxis type="number" tick={{ fill: "#52525b", fontSize: 10 }} />
                        <YAxis type="category" dataKey="path" tick={{ fill: "#52525b", fontSize: 10 }} width={100} />
                        <Tooltip contentStyle={{ background: "#0A0A0A", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }} />
                        <Bar dataKey="count" fill="#00FF94" radius={[0, 4, 4, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* Bottom Row: Event Types Pie + Top Referrers + Live Stream */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {/* Event Types */}
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="chart-event-types">
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Event Breakdown</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={180}>
                      <PieChart>
                        <Pie data={data?.event_types || []} dataKey="count" nameKey="type" cx="50%" cy="50%" innerRadius={40} outerRadius={70} paddingAngle={2}>
                          {(data?.event_types || []).map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                        </Pie>
                        <Tooltip contentStyle={{ background: "#0A0A0A", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }} />
                      </PieChart>
                    </ResponsiveContainer>
                    <div className="space-y-1 mt-2">
                      {(data?.event_types || []).slice(0, 4).map((e, i) => (
                        <div key={i} className="flex items-center justify-between text-xs">
                          <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full" style={{ background: PIE_COLORS[i % PIE_COLORS.length] }} /><span className="text-zinc-400">{e.type}</span></div>
                          <span className="font-mono text-zinc-500">{e.count}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Top Referrers */}
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="top-referrers">
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><Share2 className="w-4 h-4 text-[#FFB800]" /> Top Referrers</CardTitle></CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[260px]">
                      {(data?.top_referrers || []).length === 0 ? (
                        <div className="text-center py-8 text-xs text-zinc-600">No external referrers yet.<br />Most visits are direct.</div>
                      ) : (
                        <div className="space-y-2">
                          {data.top_referrers.map((r, i) => (
                            <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800/30">
                              <div className="flex items-center gap-2 min-w-0">
                                <span className="text-xs font-mono text-zinc-500 w-5">{i + 1}.</span>
                                <span className="text-xs text-zinc-300 truncate">{r.referrer}</span>
                              </div>
                              <Badge variant="outline" className="text-[10px] shrink-0 ml-2">{r.count}</Badge>
                            </div>
                          ))}
                        </div>
                      )}
                    </ScrollArea>
                  </CardContent>
                </Card>
              </motion.div>

              {/* Live Events Stream */}
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="live-events-stream">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm font-medium flex items-center gap-2"><Clock className="w-4 h-4 text-red-400" /> Live Events</CardTitle>
                      <div className="flex items-center gap-1"><div className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" /><span className="text-[10px] text-red-400">Live</span></div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[260px]">
                      {liveEvents.length === 0 ? (
                        <div className="text-center py-8 text-xs text-zinc-600">No events yet in this period.</div>
                      ) : (
                        <div className="space-y-1.5">
                          {liveEvents.map((e, i) => (
                            <motion.div key={`${e.timestamp}-${i}`} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.03 }} className="flex items-start gap-2 p-2 rounded-lg hover:bg-white/[0.02] transition-colors">
                              <div className="w-1.5 h-1.5 rounded-full bg-[#7B61FF] mt-1.5 shrink-0" />
                              <div className="min-w-0">
                                <p className="text-xs text-zinc-300">{e.event_type}</p>
                                <div className="flex items-center gap-2 text-[10px] text-zinc-600 mt-0.5">
                                  <span>{e.path || "--"}</span>
                                  <span>{e.timestamp ? new Date(e.timestamp).toLocaleTimeString() : "--"}</span>
                                </div>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      )}
                    </ScrollArea>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            {/* ========= GOAL TRACKER WIDGET ========= */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.32 }} className="mb-8" data-testid="goal-tracker-widget">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                      <Target className="w-4 h-4 text-[#FFB800]" /> Goal Tracker
                    </CardTitle>
                    {editGoals ? (
                      <div className="flex items-center gap-2">
                        <Button onClick={() => setEditGoals(null)} size="sm" variant="ghost" className="text-xs text-zinc-500 h-7 px-2">Cancel</Button>
                        <Button onClick={saveGoals} size="sm" disabled={savingGoals} className="text-xs bg-[#00FF94]/15 text-[#00FF94] hover:bg-[#00FF94]/25 h-7 px-3 rounded-full" data-testid="save-goals-btn">
                          <Save className="w-3 h-3 mr-1" /> {savingGoals ? "Saving..." : "Save Goals"}
                        </Button>
                      </div>
                    ) : (
                      <Button onClick={() => setEditGoals({ ...goals })} size="sm" variant="outline" className="text-xs border-zinc-800 h-7 px-3 rounded-full" data-testid="edit-goals-btn">
                        Edit Targets
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  {/* Goal target inputs (only when editing) */}
                  {editGoals && (
                    <div className="grid grid-cols-3 gap-4 mb-6 p-4 rounded-xl bg-[#050505] border border-zinc-800/30">
                      {[
                        { key: "k_factor_target", label: "K-Factor Target", max: 5, step: 0.1 },
                        { key: "demo_signup_target", label: "Demo→Signup Target (%)", max: 100, step: 1 },
                        { key: "demo_pro_target", label: "Demo→PRO Target (%)", max: 100, step: 1 },
                      ].map(f => (
                        <div key={f.key}>
                          <label className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1.5 block">{f.label}</label>
                          <Input
                            type="number"
                            min={0} max={f.max} step={f.step}
                            value={editGoals[f.key]}
                            onChange={e => setEditGoals(prev => ({ ...prev, [f.key]: parseFloat(e.target.value) || 0 }))}
                            className="bg-[#0A0A0A] border-zinc-800 text-sm h-9 font-mono"
                            data-testid={`goal-input-${f.key}`}
                          />
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Progress bars */}
                  <div className="grid md:grid-cols-3 gap-6">
                    {(() => {
                      const trends = data?.trends_24h || {};
                      const metrics = [
                        {
                          label: "K-Factor",
                          current: kpi.k_factor || 0,
                          target: goals.k_factor_target,
                          color: "#7B61FF",
                          trend: (trends.k_factor || 0) - (trends.k_factor_prev || 0),
                          format: v => v.toFixed(2),
                        },
                        {
                          label: "Demo → Signup",
                          current: kpi.demo_signup_rate || 0,
                          target: goals.demo_signup_target,
                          color: "#00FF94",
                          trend: (trends.demo_signup_rate || 0) - (trends.demo_signup_rate_prev || 0),
                          format: v => `${v.toFixed(1)}%`,
                          suffix: "%",
                        },
                        {
                          label: "Demo → PRO",
                          current: kpi.demo_pro_rate || 0,
                          target: goals.demo_pro_target,
                          color: "#FFB800",
                          trend: (trends.demo_pro_rate || 0) - (trends.demo_pro_rate_prev || 0),
                          format: v => `${v.toFixed(1)}%`,
                          suffix: "%",
                        },
                      ];

                      return metrics.map((m, i) => {
                        const pct = m.target > 0 ? Math.min(100, (m.current / m.target) * 100) : 0;
                        const achieved = m.current >= m.target && m.target > 0;
                        const needsAttention = pct < 50 && m.target > 0;
                        const trendUp = m.trend > 0;
                        const trendFlat = m.trend === 0;

                        return (
                          <div key={i} className="space-y-3" data-testid={`goal-metric-${i}`}>
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-zinc-500 font-medium">{m.label}</span>
                              <div className="flex items-center gap-1.5">
                                {achieved ? (
                                  <Badge className="bg-[#00FF94]/15 text-[#00FF94] text-[10px] gap-1" data-testid={`goal-achieved-${i}`}>
                                    <Check className="w-2.5 h-2.5" /> Goal Achieved
                                  </Badge>
                                ) : needsAttention ? (
                                  <Badge className="bg-red-400/15 text-red-400 text-[10px] gap-1" data-testid={`goal-attention-${i}`}>
                                    <AlertTriangle className="w-2.5 h-2.5" /> Needs Attention
                                  </Badge>
                                ) : null}
                              </div>
                            </div>

                            <div className="flex items-end justify-between">
                              <div>
                                <span className="text-lg font-bold font-mono" style={{ color: m.color }}>{m.format(m.current)}</span>
                                <span className="text-xs text-zinc-600 ml-1">/ {m.format(m.target)}</span>
                              </div>
                              {!trendFlat && (
                                <div className={`flex items-center gap-0.5 text-[10px] font-mono ${trendUp ? "text-[#00FF94]" : "text-red-400"}`} data-testid={`goal-trend-${i}`}>
                                  {trendUp ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                                  {trendUp ? "+" : ""}{m.trend.toFixed(m.suffix ? 1 : 2)}
                                  <span className="text-zinc-600 ml-0.5">24h</span>
                                </div>
                              )}
                            </div>

                            <div className="relative">
                              <Progress value={pct} className="h-2" />
                              <span className="text-[10px] text-zinc-600 font-mono mt-1 block">{pct.toFixed(0)}% of target</span>
                            </div>
                          </div>
                        );
                      });
                    })()}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Conversion Funnel Summary */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.35 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="conversion-funnel">
                <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><ArrowUpRight className="w-4 h-4 text-[#00FF94]" /> Conversion Funnel</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex items-center gap-2">
                    {[
                      { label: "Demo Opens", value: kpi.demo_opens || 0, color: "#7B61FF" },
                      { label: "Signups", value: kpi.total_signups || 0, color: "#00FF94" },
                      { label: "Pro Upgrades", value: kpi.total_pro || 0, color: "#FFB800" },
                    ].map((step, i) => (
                      <div key={i} className="flex items-center gap-2 flex-1">
                        <div className="flex-1 text-center p-4 rounded-xl border border-zinc-800/30" style={{ background: `${step.color}08` }}>
                          <p className="text-xl font-bold font-mono" style={{ color: step.color }}>{step.value.toLocaleString()}</p>
                          <p className="text-[10px] text-zinc-500 mt-1">{step.label}</p>
                        </div>
                        {i < 2 && <ArrowUpRight className="w-4 h-4 text-zinc-700 shrink-0" />}
                      </div>
                    ))}
                  </div>
                  <div className="flex items-center gap-2 mt-3 text-xs text-zinc-600 justify-center">
                    <span>Demo → Signup: <span className="text-[#00FF94] font-mono">{kpi.demo_signup_rate || 0}%</span></span>
                    <span className="text-zinc-800">|</span>
                    <span>Demo → Pro: <span className="text-[#FFB800] font-mono">{kpi.demo_pro_rate || 0}%</span></span>
                    <span className="text-zinc-800">|</span>
                    <span>K-Factor: <span className={`font-mono ${kpi.k_factor >= 1 ? "text-[#00FF94]" : "text-zinc-400"}`}>{kpi.k_factor || 0}</span></span>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
};

export default AdminAnalyticsPage;
