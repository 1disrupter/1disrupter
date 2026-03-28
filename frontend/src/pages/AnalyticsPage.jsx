import { useState, useEffect } from "react";
import axios from "axios";
import { RefreshCw, Scale } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { API } from "../lib/constants";

const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/analytics/overview`),
      axios.get(`${API}/analytics/strategies`),
      axios.get(`${API}/capital/allocations`)
    ]).then(([overviewRes, strategiesRes, allocRes]) => {
      setAnalytics(overviewRes.data);
      setStrategies(strategiesRes.data);
      setAllocations(allocRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="min-h-screen pt-24 px-4 flex items-center justify-center"><RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" /></div>;

  const dailyReturnsData = analytics?.daily_returns?.map((value, index) => ({ day: index + 1, return: value })) || [];

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8"><h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="analytics-title">Analytics & Performance</h1><p className="text-zinc-400 mt-1">Detailed performance metrics and strategy analysis</p></div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card" data-testid="metric-sharpe"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Sharpe Ratio</p><p className="text-3xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">{analytics?.sharpe_ratio}</p></CardContent></Card>
          <Card className="glass-card" data-testid="metric-sortino"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Sortino Ratio</p><p className="text-3xl font-bold text-[#00FF94] font-['JetBrains_Mono']">{analytics?.sortino_ratio}</p></CardContent></Card>
          <Card className="glass-card" data-testid="metric-drawdown"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Max Drawdown</p><p className="text-3xl font-bold text-red-400 font-['JetBrains_Mono']">-{analytics?.max_drawdown}%</p></CardContent></Card>
          <Card className="glass-card" data-testid="metric-winrate"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Win Rate</p><p className="text-3xl font-bold font-['JetBrains_Mono']">{analytics?.win_rate}%</p></CardContent></Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <Card className="glass-card" data-testid="daily-returns-chart">
            <CardHeader><CardTitle>Daily Returns (30D)</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dailyReturnsData}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" /><XAxis dataKey="day" stroke="#71717A" /><YAxis stroke="#71717A" /><Tooltip contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '8px' }} /><Bar dataKey="return" fill="#7B61FF" radius={[4, 4, 0, 0]} /></BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="capital-allocation-chart">
            <CardHeader><CardTitle className="flex items-center gap-2"><Scale className="w-5 h-5 text-[#00FF94]" />Capital Allocation</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={allocations} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#27272A" /><XAxis type="number" stroke="#71717A" /><YAxis dataKey="strategy_name" type="category" stroke="#71717A" width={120} /><Tooltip contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '8px' }} /><Bar dataKey="allocation_percent" fill="#00FF94" radius={[0, 4, 4, 0]} /></BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="glass-card" data-testid="strategies-table">
          <CardHeader><CardTitle>Strategy Details</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead><tr className="border-b border-zinc-800"><th className="text-left p-4 text-zinc-500">Strategy</th><th className="text-right p-4 text-zinc-500">Return</th><th className="text-right p-4 text-zinc-500">Trades</th><th className="text-right p-4 text-zinc-500">Win Rate</th></tr></thead>
                <tbody>
                  {strategies.map((strategy, index) => (
                    <tr key={index} className="border-b border-zinc-800/50" data-testid={`strategy-row-${index}`}>
                      <td className="p-4 font-medium">{strategy.name}</td>
                      <td className={`p-4 text-right font-mono ${strategy.return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{strategy.return >= 0 ? '+' : ''}{strategy.return}%</td>
                      <td className="p-4 text-right font-mono text-zinc-400">{strategy.trades}</td>
                      <td className="p-4 text-right font-mono">{strategy.win_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalyticsPage;
