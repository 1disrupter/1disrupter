import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Scale, Clock, Target } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { PageHeader, StatsRow } from "../components/PlaceholderUI";

const mockAnalyticsData = [
  { name: 'BTC', signals: 24, winRate: 72 },
  { name: 'ETH', signals: 18, winRate: 68 },
  { name: 'SOL', signals: 14, winRate: 74 },
  { name: 'AVAX', signals: 11, winRate: 61 },
  { name: 'DOGE', signals: 8, winRate: 58 },
  { name: 'MATIC', signals: 6, winRate: 66 },
];

const AnalyticsPage = () => {
  const stats = [
    { label: 'Total Signals', value: '81', change: 'Last 30 days', positive: true },
    { label: 'Avg Win Rate', value: '68.2%', change: '+1.4%', positive: true },
    { label: 'Sharpe Ratio', value: '1.74', change: 'Portfolio-wide', positive: true },
    { label: 'Max Drawdown', value: '-8.3%', change: 'Last 30 days', positive: false },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="analytics-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader
          icon={BarChart3}
          title="Analytics"
          description="Performance metrics and signal distribution across all trading pairs"
          testId="analytics-header"
        />

        <StatsRow stats={stats} />

        <div className="grid md:grid-cols-2 gap-6">
          {/* Signal Distribution Chart */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Signal Distribution
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={mockAnalyticsData}>
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

          {/* Win Rate by Pair */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-[#00FF94]" /> Win Rate by Pair
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={mockAnalyticsData}>
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

        {/* Performance Summary Table */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-6">
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Scale className="w-4 h-4 text-[#FFB800]" /> Performance Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-zinc-800/50">
                      {['Pair', 'Signals', 'Win Rate', 'Avg Return', 'Best Trade', 'Worst Trade'].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/30">
                    {[
                      ['BTC/USD', '24', '72%', '+3.2%', '+8.4%', '-2.1%'],
                      ['ETH/USD', '18', '68%', '+2.8%', '+6.7%', '-3.4%'],
                      ['SOL/USD', '14', '74%', '+4.1%', '+12.2%', '-4.8%'],
                      ['AVAX/USD', '11', '61%', '+1.9%', '+5.3%', '-3.9%'],
                      ['DOGE/USD', '8', '58%', '+1.4%', '+4.1%', '-2.8%'],
                    ].map((row, i) => (
                      <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                        {row.map((cell, j) => (
                          <td key={j} className={`px-4 py-3 text-sm font-mono ${
                            j === 0 ? 'text-zinc-200 font-medium' :
                            cell.startsWith('+') ? 'text-[#00FF94]' :
                            cell.startsWith('-') ? 'text-red-400' : 'text-zinc-400'
                          }`}>{cell}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
