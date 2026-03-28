import { useState, useEffect } from "react";
import axios from "axios";
import { BarChart3, RefreshCw } from "lucide-react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from "recharts";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle
} from "../components/ui/dialog";
import { API } from "../lib/constants";

const ConversionAnalyticsPage = () => {
  const [summary, setSummary] = useState(null);
  const [daily, setDaily] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [featureDetail, setFeatureDetail] = useState(null);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/analytics/summary?days=30`),
      axios.get(`${API}/analytics/daily?days=14`)
    ]).then(([summaryRes, dailyRes]) => {
      setSummary(summaryRes.data);
      setDaily(dailyRes.data.daily || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const loadFeatureDetail = async (feature) => {
    setSelectedFeature(feature);
    try {
      const res = await axios.get(`${API}/analytics/feature/${feature}?days=30`);
      setFeatureDetail(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="min-h-screen pt-24 px-4 flex items-center justify-center"><RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" /></div>;

  const featureColors = {
    'exit_popup': '#FF6B6B',
    'timed_popup': '#7B61FF',
    'unlock_live_btn': '#00FF94',
    'upgrade_cta': '#FFB800',
    'missed_trade': '#FF8C42',
    'social_proof': '#4ECDC4',
    'dashboard': '#A78BFA'
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="conversion-analytics-title">
            Conversion Analytics
          </h1>
          <p className="text-zinc-400 mt-1">A/B Testing & Feature Performance Dashboard</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Total Views</p>
              <p className="text-3xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">{summary?.total_views || 0}</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Conversions</p>
              <p className="text-3xl font-bold text-[#00FF94] font-['JetBrains_Mono']">{summary?.total_conversions || 0}</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Conversion Rate</p>
              <p className="text-3xl font-bold text-[#FFB800] font-['JetBrains_Mono']">{summary?.overall_conversion_rate || 0}%</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Top Performer</p>
              <p className="text-xl font-bold text-white font-['JetBrains_Mono']">{summary?.top_performer || 'N/A'}</p>
            </CardContent>
          </Card>
        </div>

        {/* Feature Performance Table */}
        <Card className="glass-card mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-[#7B61FF]" />
              Feature Performance (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summary?.features?.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-zinc-800">
                      <th className="text-left p-4 text-zinc-500">Feature</th>
                      <th className="text-right p-4 text-zinc-500">Views</th>
                      <th className="text-right p-4 text-zinc-500">Clicks</th>
                      <th className="text-right p-4 text-zinc-500">Conversions</th>
                      <th className="text-right p-4 text-zinc-500">Click Rate</th>
                      <th className="text-right p-4 text-zinc-500">Conv. Rate</th>
                      <th className="text-right p-4 text-zinc-500">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.features.map((feature, index) => (
                      <tr key={index} className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full" 
                              style={{ backgroundColor: featureColors[feature.feature] || '#7B61FF' }}
                            />
                            <span className="font-medium">{feature.feature.replace(/_/g, ' ')}</span>
                          </div>
                        </td>
                        <td className="p-4 text-right font-mono text-zinc-400">{feature.views}</td>
                        <td className="p-4 text-right font-mono text-zinc-400">{feature.clicks}</td>
                        <td className="p-4 text-right font-mono text-[#00FF94]">{feature.conversions}</td>
                        <td className="p-4 text-right font-mono">{feature.click_rate}%</td>
                        <td className="p-4 text-right">
                          <span className={`font-mono font-bold ${feature.conversion_rate > 5 ? 'text-[#00FF94]' : feature.conversion_rate > 2 ? 'text-[#FFB800]' : 'text-zinc-400'}`}>
                            {feature.conversion_rate}%
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => loadFeatureDetail(feature.feature)}
                            className="border-zinc-700"
                          >
                            Details
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-zinc-500">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No analytics data yet</p>
                <p className="text-sm mt-2">Data will appear as users interact with conversion features</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Daily Chart */}
        {daily.length > 0 && (
          <Card className="glass-card mb-8">
            <CardHeader>
              <CardTitle>Daily Conversions (Last 14 Days)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={daily}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis dataKey="date" stroke="#71717A" fontSize={12} />
                    <YAxis stroke="#71717A" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '8px' }} 
                    />
                    <Bar dataKey="views" name="Views" fill="#7B61FF" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="conversions" name="Conversions" fill="#00FF94" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Feature Detail Modal */}
        <Dialog open={!!selectedFeature} onOpenChange={() => setSelectedFeature(null)}>
          <DialogContent className="bg-[#121212] border-zinc-800 max-w-lg">
            <DialogHeader>
              <DialogTitle className="capitalize">{selectedFeature?.replace(/_/g, ' ')} - Details</DialogTitle>
            </DialogHeader>
            {featureDetail && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Views</p>
                    <p className="text-2xl font-bold font-mono">{featureDetail.events?.view || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Clicks</p>
                    <p className="text-2xl font-bold font-mono">{featureDetail.events?.click || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Conversions</p>
                    <p className="text-2xl font-bold font-mono text-[#00FF94]">{featureDetail.events?.conversion || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Dismisses</p>
                    <p className="text-2xl font-bold font-mono text-red-400">{featureDetail.events?.dismiss || 0}</p>
                  </div>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                  <p className="text-sm text-zinc-500 mb-2">Rates</p>
                  <div className="flex justify-between">
                    <span>Click Rate: <span className="font-mono font-bold">{featureDetail.click_rate}%</span></span>
                    <span>Conversion: <span className="font-mono font-bold text-[#00FF94]">{featureDetail.conversion_rate}%</span></span>
                  </div>
                </div>
                {featureDetail.peak_hour !== null && (
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Peak Activity Hour</p>
                    <p className="text-lg font-bold">{featureDetail.peak_hour}:00</p>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default ConversionAnalyticsPage;
