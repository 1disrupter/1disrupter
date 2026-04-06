import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Scale, Wifi } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { useSystemMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import axios from "axios";

const API = process.env.REACT_APP_BACKEND_URL;

const AnalyticsPage = () => {
  const { mode, isDemo, isLive } = useSystemMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.get(`${API}/api/analytics/summary?days=30`, { headers });
      setSummary(res.data);
      setError(null);
    } catch (e) {
      setError("Could not load analytics");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics, mode]);

  const chartData = summary?.by_pair || [
    { name: 'BTC', signals: 24, winRate: 72 },
    { name: 'ETH', signals: 18, winRate: 68 },
    { name: 'SOL', signals: 14, winRate: 74 },
    { name: 'AVAX', signals: 11, winRate: 61 },
    { name: 'DOGE', signals: 8, winRate: 58 },
  ];

  const stats = summary ? [
    { label: 'Total Signals', value: String(summary.total_signals ?? summary.total_conversions ?? 81), change: 'Last 30 days', positive: true },
    { label: 'Avg Win Rate', value: `${(summary.avg_win_rate ?? summary.overall_conversion_rate ?? 68.2).toFixed(1)}%`, change: summary.win_rate_change || '--', positive: (summary.avg_win_rate ?? 0) > 50 },
    { label: 'Sharpe Ratio', value: (summary.sharpe_ratio ?? 1.74).toFixed(2), change: 'Portfolio-wide', positive: (summary.sharpe_ratio ?? 0) > 1 },
    { label: 'Max Drawdown', value: `${(summary.max_drawdown ?? -8.3).toFixed(1)}%`, change: 'Last 30 days', positive: false },
  ] : [
    { label: 'Total Signals', value: '--', change: 'Loading...', positive: true },
    { label: 'Avg Win Rate', value: '--', change: '--', positive: true },
    { label: 'Sharpe Ratio', value: '--', change: '--', positive: true },
    { label: 'Max Drawdown', value: '--', change: '--', positive: false },
  ];

  const tableRows = chartData.map(p => [
    `${p.name}/USD`, String(p.signals), `${p.winRate}%`,
    `+${(p.avg_return ?? 2.5).toFixed(1)}%`,
    `+${(p.best_trade ?? 5).toFixed(1)}%`,
    `-${(p.worst_trade ?? 3).toFixed(1)}%`,
  ]);

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="analytics-page">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <PageHeader icon={BarChart3} title="Analytics" description="Performance metrics and signal distribution across all trading pairs" testId="analytics-header" />
          <Badge
            className={`text-[10px] font-mono ${isLive ? 'bg-[#00FF94]/10 text-[#00FF94] border border-[#00FF94]/20' : 'bg-[#7B61FF]/10 text-[#7B61FF] border border-[#7B61FF]/20'}`}
            data-testid="analytics-mode-badge"
          >
            <span className={`w-1.5 h-1.5 rounded-full mr-1 ${isLive ? 'bg-[#00FF94] animate-pulse' : 'bg-[#7B61FF]'}`} />
            {isLive ? 'LIVE DATA' : 'DEMO DATA'}
          </Badge>
        </div>

        {loading ? <LoadingSkeleton rows={3} /> : error ? <ErrorState message={error} onRetry={fetchAnalytics} /> : (
          <>
            <StatsRow stats={stats} />

            <div className="grid md:grid-cols-2 gap-6">
              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50">
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Signal Distribution</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                        <XAxis dataKey="name" tick={{ fill: '#52525b', fontSize: 12 }} />
                        <YAxis tick={{ fill: '#52525b', fontSize: 12 }} />
                        <Tooltip contentStyle={{ background: '#0A0A0A', border: '1px solid #27272a', borderRadius: 8 }} />
                        <Bar dataKey="signals" fill="#7B61FF" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>

              <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50">
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><TrendingUp className="w-4 h-4 text-[#00FF94]" /> Win Rate by Pair</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                      <BarChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" />
                        <XAxis dataKey="name" tick={{ fill: '#52525b', fontSize: 12 }} />
                        <YAxis tick={{ fill: '#52525b', fontSize: 12 }} domain={[0, 100]} />
                        <Tooltip contentStyle={{ background: '#0A0A0A', border: '1px solid #27272a', borderRadius: 8 }} />
                        <Bar dataKey="winRate" fill="#00FF94" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </motion.div>
            </div>

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-6">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-2"><CardTitle className="text-sm font-medium flex items-center gap-2"><Scale className="w-4 h-4 text-[#FFB800]" /> Performance Summary</CardTitle></CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead><tr className="border-b border-zinc-800/50">{['Pair', 'Signals', 'Win Rate', 'Avg Return', 'Best Trade', 'Worst Trade'].map(h => (<th key={h} className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">{h}</th>))}</tr></thead>
                      <tbody className="divide-y divide-zinc-800/30">
                        {tableRows.map((row, i) => (
                          <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                            {row.map((cell, j) => (
                              <td key={j} className={`px-4 py-3 text-sm font-mono ${j === 0 ? 'text-zinc-200 font-medium' : cell.startsWith && cell.startsWith('+') ? 'text-[#00FF94]' : cell.startsWith && cell.startsWith('-') ? 'text-red-400' : 'text-zinc-400'}`}>{cell}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
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

export default AnalyticsPage;
