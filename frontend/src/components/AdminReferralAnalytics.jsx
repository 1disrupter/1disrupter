import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import { Badge } from "../components/ui/badge";
import { Users, DollarSign, TrendingUp, UserPlus, Link2 } from "lucide-react";
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
          {p.name}: {p.value}
        </p>
      ))}
    </div>
  );
};

const StatCard = ({ icon: Icon, label, value, color, bg, delay = 0 }) => (
  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay }}>
    <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/60 transition-all group" data-testid={`ref-stat-${label.toLowerCase().replace(/\s/g, "-")}`}>
      <CardContent className="p-4">
        <div className={`w-8 h-8 rounded-lg ${bg} flex items-center justify-center mb-2 group-hover:scale-110 transition-transform`}>
          <Icon className={`w-4 h-4 ${color}`} />
        </div>
        <p className="text-[11px] text-zinc-500 uppercase tracking-wider">{label}</p>
        <p className="text-xl font-bold font-['JetBrains_Mono'] text-zinc-100 mt-0.5">{value}</p>
      </CardContent>
    </Card>
  </motion.div>
);

const AdminReferralAnalytics = () => {
  const [summary, setSummary] = useState(null);
  const [events, setEvents] = useState(null);
  const [range, setRange] = useState("7d");
  const [loading, setLoading] = useState(true);

  const fetchSummary = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/referrals/admin/summary?admin_key=${ADMIN_KEY}`);
      setSummary(res.data);
    } catch { /* ignore */ }
  }, []);

  const fetchEvents = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/referrals/admin/events?admin_key=${ADMIN_KEY}&range=${range}`);
      setEvents(res.data);
    } catch { /* ignore */ }
  }, [range]);

  useEffect(() => {
    Promise.all([fetchSummary(), fetchEvents()]).finally(() => setLoading(false));
  }, [fetchSummary, fetchEvents]);

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50">
              <CardContent className="p-4"><div className="h-16 bg-zinc-900 rounded animate-pulse" /></CardContent>
            </Card>
          ))}
        </div>
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardContent className="p-6"><div className="h-48 bg-zinc-900 rounded animate-pulse" /></CardContent>
        </Card>
      </div>
    );
  }

  const stats = summary ? [
    { icon: UserPlus, label: "Total Referrals", value: summary.total_referrals, color: "text-[#7B61FF]", bg: "bg-[#7B61FF]/10" },
    { icon: Users, label: "Active Subs (Referred)", value: summary.active_subscribers_from_referrals, color: "text-emerald-400", bg: "bg-emerald-400/10" },
    { icon: DollarSign, label: "Revenue (Referred)", value: `$${summary.total_revenue_from_referrals.toFixed(2)}`, color: "text-amber-400", bg: "bg-amber-400/10" },
    { icon: TrendingUp, label: "Commissions Owed", value: `$${summary.total_commissions_owed.toFixed(2)}`, color: "text-sky-400", bg: "bg-sky-400/10" },
  ] : [];

  const daily = events?.daily?.map(d => ({ ...d, date: d.date.slice(5) })) || [];

  return (
    <div className="space-y-5" data-testid="admin-referral-analytics">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
          <Link2 className="w-4 h-4 text-[#7B61FF]" /> Affiliate Performance
        </h3>
        <Select value={range} onValueChange={setRange}>
          <SelectTrigger className="w-28 h-8 text-xs bg-[#0A0A0A] border-zinc-800" data-testid="referral-range-select">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="today">Today</SelectItem>
            <SelectItem value="7d">Last 7 days</SelectItem>
            <SelectItem value="30d">Last 30 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {stats.map((s, i) => <StatCard key={s.label} {...s} delay={i * 0.04} />)}
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Referral Signups Over Time */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-zinc-400 uppercase tracking-wider">Referral Signups</CardTitle>
          </CardHeader>
          <CardContent className="pt-0" data-testid="referral-signups-chart">
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={daily}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 10 }} />
                <YAxis tick={{ fill: "#555", fontSize: 10 }} allowDecimals={false} />
                <Tooltip content={<ChartTooltip />} />
                <Line type="monotone" dataKey="signups" name="Signups" stroke="#7B61FF" strokeWidth={2} dot={{ r: 3, fill: "#7B61FF" }} />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Referral Conversions vs Signups */}
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-zinc-400 uppercase tracking-wider">Signups vs Conversions</CardTitle>
          </CardHeader>
          <CardContent className="pt-0" data-testid="referral-conversions-chart">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={daily}>
                <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                <XAxis dataKey="date" tick={{ fill: "#555", fontSize: 10 }} />
                <YAxis tick={{ fill: "#555", fontSize: 10 }} allowDecimals={false} />
                <Tooltip content={<ChartTooltip />} />
                <Legend wrapperStyle={{ fontSize: 10, color: "#666" }} />
                <Bar dataKey="signups" name="Signups" fill="#7B61FF" radius={[2, 2, 0, 0]} />
                <Bar dataKey="conversions" name="Conversions" fill="#00FF94" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top Referrers Table */}
      {summary?.top_referrers?.length > 0 && (
        <Card className="bg-[#0A0A0A] border-zinc-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-zinc-400 uppercase tracking-wider">Top Referrers</CardTitle>
          </CardHeader>
          <CardContent className="p-0" data-testid="top-referrers-table">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-800/50">
                    <th className="text-left p-3 text-[11px] text-zinc-500 font-medium">#</th>
                    <th className="text-left p-3 text-[11px] text-zinc-500 font-medium">Referrer</th>
                    <th className="text-left p-3 text-[11px] text-zinc-500 font-medium">Code</th>
                    <th className="text-right p-3 text-[11px] text-zinc-500 font-medium">Signups</th>
                    <th className="text-right p-3 text-[11px] text-zinc-500 font-medium">Conversions</th>
                    <th className="text-right p-3 text-[11px] text-zinc-500 font-medium">Earnings</th>
                  </tr>
                </thead>
                <tbody>
                  {summary.top_referrers.map((r, i) => (
                    <tr key={i} className="border-b border-zinc-800/30 last:border-0 hover:bg-zinc-900/50 transition-colors">
                      <td className="p-3 text-zinc-600 font-mono text-xs">{i + 1}</td>
                      <td className="p-3 text-zinc-300 text-xs">{r.email}</td>
                      <td className="p-3 font-mono text-xs text-[#7B61FF]">{r.code}</td>
                      <td className="p-3 text-right text-zinc-200 font-mono text-xs">{r.signups}</td>
                      <td className="p-3 text-right text-emerald-400 font-mono text-xs">{r.conversions}</td>
                      <td className="p-3 text-right text-amber-400 font-mono text-xs">${r.earnings.toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default AdminReferralAnalytics;
