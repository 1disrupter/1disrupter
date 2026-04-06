import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Bot, Calendar, Target, Activity } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

const Stat = ({ icon: Icon, label, value, color }) => (
  <Card className="bg-[#0A0A0A] border-zinc-800/50">
    <CardContent className="p-4 flex items-center gap-3">
      <Icon className="w-4 h-4 shrink-0" style={{ color }} />
      <div>
        <p className="text-[10px] text-zinc-600 uppercase tracking-wider">{label}</p>
        <p className="text-lg font-bold font-mono text-zinc-100">{value}</p>
      </div>
    </CardContent>
  </Card>
);

const chartTooltip = { background: "#0A0A0A", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 };

const LiveAnalytics = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetch_ = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/analytics/live?days=30`);
      setData(res.data);
    } catch { /* keep existing */ }
    finally { setLoading(false); }
  }, []);

  useEffect(() => {
    fetch_();
    const id = setInterval(fetch_, 20000);
    return () => clearInterval(id);
  }, [fetch_]);

  if (loading) {
    return (
      <div className="space-y-4" data-testid="analytics-loading">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">{[0,1,2,3].map(i => <div key={i} className="h-20 bg-[#0A0A0A] border border-zinc-800/40 rounded-xl animate-pulse" />)}</div>
        <div className="grid md:grid-cols-2 gap-4">{[0,1].map(i => <div key={i} className="h-64 bg-[#0A0A0A] border border-zinc-800/40 rounded-xl animate-pulse" />)}</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-16" data-testid="analytics-empty">
        <BarChart3 className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
        <p className="text-sm text-zinc-500">No analytics data available</p>
      </div>
    );
  }

  const { total_signals, avg_win_rate, sharpe_ratio, max_drawdown, by_pair = [], by_agent = [], daily = [] } = data;

  return (
    <div className="space-y-6">
      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat icon={Activity} label="Total Signals" value={total_signals?.toLocaleString() ?? "—"} color="#7B61FF" />
        <Stat icon={Target} label="Avg Win Rate" value={`${avg_win_rate ?? 0}%`} color="#00FF94" />
        <Stat icon={TrendingUp} label="Sharpe Ratio" value={sharpe_ratio ?? "—"} color="#FFB800" />
        <Stat icon={BarChart3} label="Max Drawdown" value={`${max_drawdown ?? 0}%`} color="#FF6B6B" />
      </div>

      {/* Charts row */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Asset distribution */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Signal Distribution</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={by_pair}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                  <XAxis dataKey="name" tick={{ fill: "#52525b", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#52525b", fontSize: 11 }} />
                  <Tooltip contentStyle={chartTooltip} />
                  <Bar dataKey="signals" fill="#7B61FF" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Win rate by pair */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><TrendingUp className="w-4 h-4 text-[#00FF94]" /> Win Rate by Pair</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={by_pair}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                  <XAxis dataKey="name" tick={{ fill: "#52525b", fontSize: 11 }} />
                  <YAxis tick={{ fill: "#52525b", fontSize: 11 }} domain={[0, 100]} />
                  <Tooltip contentStyle={chartTooltip} />
                  <Bar dataKey="winRate" fill="#00FF94" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Second row */}
      <div className="grid md:grid-cols-2 gap-4">
        {/* Agent accuracy */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><Bot className="w-4 h-4 text-[#FFB800]" /> Agent Accuracy</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={230}>
                <BarChart data={by_agent} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                  <XAxis type="number" domain={[0, 100]} tick={{ fill: "#52525b", fontSize: 11 }} />
                  <YAxis dataKey="name" type="category" width={120} tick={{ fill: "#52525b", fontSize: 10 }} />
                  <Tooltip contentStyle={chartTooltip} />
                  <Bar dataKey="accuracy" fill="#FFB800" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Daily signal volume */}
        <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><Calendar className="w-4 h-4 text-[#7B61FF]" /> Daily Signal Volume</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={230}>
                <LineChart data={daily}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                  <XAxis dataKey="date" tick={{ fill: "#52525b", fontSize: 10 }} tickFormatter={v => v.slice(5)} />
                  <YAxis tick={{ fill: "#52525b", fontSize: 11 }} />
                  <Tooltip contentStyle={chartTooltip} />
                  <Line type="monotone" dataKey="signals" stroke="#7B61FF" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default LiveAnalytics;
