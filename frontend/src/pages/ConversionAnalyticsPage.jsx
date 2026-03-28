import { motion } from "framer-motion";
import { BarChart3, TrendingUp, Users, Eye, MousePointer } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { PageHeader, StatsRow } from "../components/PlaceholderUI";

const mockFunnelData = [
  { stage: 'Landing', visitors: 2400 },
  { stage: 'Register', visitors: 840 },
  { stage: 'Free Tier', visitors: 620 },
  { stage: 'Trial', visitors: 280 },
  { stage: 'Pro', visitors: 142 },
  { stage: 'Elite', visitors: 38 },
];

const ConversionAnalyticsPage = () => {
  const stats = [
    { label: 'Total Visitors', value: '2.4K', change: '+18% MoM', positive: true },
    { label: 'Sign-up Rate', value: '35%', change: '+4.2%', positive: true },
    { label: 'Free → Pro', value: '22.9%', change: '+1.8%', positive: true },
    { label: 'LTV', value: '$284', change: '+$32', positive: true },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="conversion-analytics-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader
          icon={BarChart3}
          title="Conversion Analytics"
          description="Track visitor-to-subscriber funnel performance"
          badge="Internal"
          testId="conversion-header"
        />

        <StatsRow stats={stats} />

        {/* Funnel Chart */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mb-6">
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <MousePointer className="w-4 h-4 text-[#7B61FF]" /> Conversion Funnel
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={mockFunnelData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1a1a1a" horizontal={false} />
                  <XAxis type="number" tick={{ fill: '#52525b', fontSize: 12 }} />
                  <YAxis dataKey="stage" type="category" tick={{ fill: '#a1a1aa', fontSize: 12 }} width={80} />
                  <Tooltip contentStyle={{ background: '#0A0A0A', border: '1px solid #27272a', borderRadius: 8 }} />
                  <Bar dataKey="visitors" fill="#7B61FF" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* Metrics Table */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-[#00FF94]" /> Stage Metrics
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-zinc-800/50">
                      {['Stage', 'Users', 'Conversion', 'Drop-off', 'Avg Time'].map(h => (
                        <th key={h} className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-800/30">
                    {[
                      ['Landing → Register', '840', '35.0%', '65.0%', '2m 14s'],
                      ['Register → Free Tier', '620', '73.8%', '26.2%', '48s'],
                      ['Free Tier → Trial', '280', '45.2%', '54.8%', '3d 8h'],
                      ['Trial → Pro', '142', '50.7%', '49.3%', '6d 12h'],
                      ['Pro → Elite', '38', '26.8%', '73.2%', '28d'],
                    ].map((row, i) => (
                      <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                        {row.map((cell, j) => (
                          <td key={j} className={`px-4 py-3 text-sm font-mono ${
                            j === 0 ? 'text-zinc-200' : j === 2 ? 'text-[#00FF94]' : j === 3 ? 'text-red-400' : 'text-zinc-400'
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

export default ConversionAnalyticsPage;
