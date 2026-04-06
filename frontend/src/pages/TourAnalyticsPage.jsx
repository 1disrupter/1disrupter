import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  Brain, Users, TrendingUp, Target, MousePointerClick,
  Crown, RefreshCw, ArrowDownRight, ChevronRight
} from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, AreaChart, Area
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const STEP_LABELS = {
  welcome: "Welcome",
  dashboard: "Dashboard",
  signals: "Live Signals",
  research: "Research",
  lab: "Strategy Lab",
  agents: "AI Agents",
  mode: "Demo Badge",
  cta: "Upgrade CTA",
};

const KpiCard = ({ icon: Icon, label, value, sub, color = "#7B61FF" }) => (
  <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}>
    <Card className="bg-[#0A0A0A] border-zinc-800/50">
      <CardContent className="p-5">
        <div className="flex items-start justify-between mb-3">
          <div className="p-2 rounded-lg" style={{ background: `${color}15` }}>
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

export default function TourAnalyticsPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/analytics/tour/summary?days=${days}`);
      setData(res.data);
    } catch {
      toast.error("Failed to load tour analytics");
    } finally {
      setLoading(false);
    }
  }, [days]);

  useEffect(() => { fetch(); }, [fetch]);

  const funnelData = (data?.funnel || []).map(s => ({
    name: STEP_LABELS[s.step_id] || s.step_id,
    views: s.views,
    unique: s.unique_sessions,
  }));

  const dropoffData = (data?.dropoff || []).map(s => ({
    name: STEP_LABELS[s.step_id] || s.step_id,
    skips: s.count,
  }));

  const dailyData = (data?.daily || []).map(d => ({
    date: d.date?.slice(5),
    views: d.step_view || 0,
    completes: d.complete || 0,
    skips: d.skip || 0,
    cta: d.cta_click || 0,
  }));

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="tour-analytics-page">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold font-['Outfit']" data-testid="tour-analytics-title">Tour Analytics</h1>
            </div>
            <p className="text-sm text-zinc-500">Track guided tour engagement, drop-off points, and conversion</p>
          </div>
          <div className="flex items-center gap-2">
            {[7, 30, 90].map(d => (
              <Button
                key={d}
                variant={days === d ? "default" : "outline"}
                size="sm"
                onClick={() => setDays(d)}
                className={`rounded-full text-xs h-8 ${days === d ? "bg-[#7B61FF] text-white" : "border-zinc-800 text-zinc-400"}`}
                data-testid={`tour-period-${d}d`}
              >
                {d}d
              </Button>
            ))}
            <Button variant="ghost" size="icon" onClick={fetch} className="h-8 w-8" data-testid="tour-refresh-btn">
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          <KpiCard
            icon={Users}
            label="Tour Starts"
            value={data?.starts ?? "—"}
            sub={`Last ${days} days`}
            color="#7B61FF"
          />
          <KpiCard
            icon={Target}
            label="Completions"
            value={data?.completes ?? "—"}
            sub={`${data?.completion_rate ?? 0}% completion rate`}
            color="#00FF94"
          />
          <KpiCard
            icon={MousePointerClick}
            label="CTA Clicks"
            value={data?.cta_clicks ?? "—"}
            sub={`${data?.cta_rate ?? 0}% of starts`}
            color="#FFB800"
          />
          <KpiCard
            icon={ArrowDownRight}
            label="Skip Rate"
            value={`${data?.starts ? Math.round(((data?.totals?.skip || 0) / data.starts) * 100) : 0}%`}
            sub={`${data?.totals?.skip || 0} total skips`}
            color="#ef4444"
          />
        </div>

        {/* Funnel + Dropoff */}
        <div className="grid lg:grid-cols-2 gap-4">
          {/* Step Funnel */}
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-[#7B61FF]" />
                Step Funnel
                <Badge variant="outline" className="ml-auto text-[10px] border-zinc-700 text-zinc-500">Views per step</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {funnelData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={funnelData} barSize={28}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                    <XAxis dataKey="name" tick={{ fill: "#71717a", fontSize: 10 }} angle={-25} textAnchor="end" height={50} />
                    <YAxis tick={{ fill: "#71717a", fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ background: "#0D0D0D", border: "1px solid #27272a", borderRadius: 12, fontSize: 12 }}
                      labelStyle={{ color: "#a1a1aa" }}
                    />
                    <Bar dataKey="views" fill="#7B61FF" radius={[4, 4, 0, 0]} name="Views" />
                    <Bar dataKey="unique" fill="#00FF94" radius={[4, 4, 0, 0]} name="Unique Sessions" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[260px] flex items-center justify-center text-sm text-zinc-600" data-testid="funnel-empty">
                  No tour data yet. Funnel will appear once users start the tour.
                </div>
              )}
            </CardContent>
          </Card>

          {/* Dropoff Points */}
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                <ArrowDownRight className="w-4 h-4 text-red-500" />
                Drop-off Points
                <Badge variant="outline" className="ml-auto text-[10px] border-zinc-700 text-zinc-500">Where users skip</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {dropoffData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={dropoffData} barSize={28}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                    <XAxis dataKey="name" tick={{ fill: "#71717a", fontSize: 10 }} angle={-25} textAnchor="end" height={50} />
                    <YAxis tick={{ fill: "#71717a", fontSize: 10 }} />
                    <Tooltip
                      contentStyle={{ background: "#0D0D0D", border: "1px solid #27272a", borderRadius: 12, fontSize: 12 }}
                      labelStyle={{ color: "#a1a1aa" }}
                    />
                    <Bar dataKey="skips" fill="#ef4444" radius={[4, 4, 0, 0]} name="Skips" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-[260px] flex items-center justify-center text-sm text-zinc-600" data-testid="dropoff-empty">
                  No drop-off data yet. Will appear when users skip the tour.
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Daily Trend */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-zinc-300 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-[#00FF94]" />
              Daily Tour Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {dailyData.length > 0 ? (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart data={dailyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                  <XAxis dataKey="date" tick={{ fill: "#71717a", fontSize: 10 }} />
                  <YAxis tick={{ fill: "#71717a", fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ background: "#0D0D0D", border: "1px solid #27272a", borderRadius: 12, fontSize: 12 }}
                    labelStyle={{ color: "#a1a1aa" }}
                  />
                  <Area type="monotone" dataKey="views" stroke="#7B61FF" fill="#7B61FF" fillOpacity={0.15} name="Views" />
                  <Area type="monotone" dataKey="completes" stroke="#00FF94" fill="#00FF94" fillOpacity={0.15} name="Completions" />
                  <Area type="monotone" dataKey="cta" stroke="#FFB800" fill="#FFB800" fillOpacity={0.15} name="CTA Clicks" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[220px] flex items-center justify-center text-sm text-zinc-600" data-testid="daily-empty">
                Daily trend data will appear after tour interactions.
              </div>
            )}
          </CardContent>
        </Card>

        {/* Step-by-step breakdown table */}
        {funnelData.length > 0 && (
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-zinc-300">Step Breakdown</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="tour-step-table">
                  <thead>
                    <tr className="text-zinc-500 text-xs border-b border-zinc-800/50">
                      <th className="text-left py-2 px-3">Step</th>
                      <th className="text-right py-2 px-3">Views</th>
                      <th className="text-right py-2 px-3">Unique</th>
                      <th className="text-right py-2 px-3">Drop-off</th>
                      <th className="text-right py-2 px-3">Retention</th>
                    </tr>
                  </thead>
                  <tbody>
                    {funnelData.map((s, i) => {
                      const maxViews = funnelData[0]?.views || 1;
                      const retention = Math.round((s.views / maxViews) * 100);
                      const skips = dropoffData.find(d => d.name === s.name)?.skips || 0;
                      return (
                        <tr key={s.name} className="border-b border-zinc-800/30 hover:bg-white/[0.02]">
                          <td className="py-2.5 px-3 flex items-center gap-2">
                            <span className="w-5 h-5 rounded bg-zinc-800 text-[10px] flex items-center justify-center text-zinc-400 font-mono">{i + 1}</span>
                            <span className="text-zinc-300">{s.name}</span>
                          </td>
                          <td className="text-right py-2.5 px-3 font-mono text-zinc-300">{s.views}</td>
                          <td className="text-right py-2.5 px-3 font-mono text-zinc-400">{s.unique}</td>
                          <td className="text-right py-2.5 px-3 font-mono text-red-400">{skips || "—"}</td>
                          <td className="text-right py-2.5 px-3">
                            <div className="flex items-center justify-end gap-2">
                              <div className="w-16 h-1.5 rounded-full bg-zinc-800 overflow-hidden">
                                <div
                                  className="h-full rounded-full bg-gradient-to-r from-[#7B61FF] to-[#00FF94]"
                                  style={{ width: `${retention}%` }}
                                />
                              </div>
                              <span className="text-xs font-mono text-zinc-400 w-8 text-right">{retention}%</span>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
