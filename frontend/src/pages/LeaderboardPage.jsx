import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy, TrendingUp, TrendingDown, BarChart3, ArrowUpDown, ChevronUp, ChevronDown,
  RefreshCw, X, Shield, Zap, Loader2, Minus, Heart
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { useAuth } from "../contexts/AuthContext";
import { useDemoMode } from "../contexts/DemoModeContext";
import UpgradeModal from "../components/UpgradeModal";
import { API } from "../lib/constants";
import { trackEvent } from "../lib/tracking";

const SORT_COLS = [
  { key: "sharpe_ratio", label: "Sharpe", apiKey: "sharpe" },
  { key: "total_return", label: "Return %", apiKey: "total_return" },
  { key: "max_drawdown", label: "Max DD %", apiKey: "max_drawdown" },
  { key: "win_rate", label: "Win Rate %", apiKey: "win_rate" },
];

const typeColors = {
  momentum: "bg-[#7B61FF]/15 text-[#7B61FF]",
  mean_reversion: "bg-[#00FF94]/15 text-[#00FF94]",
  breakout: "bg-[#FFB800]/15 text-[#FFB800]",
};

const LeaderboardPage = () => {
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const { isDemoMode } = useDemoMode();
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState("sharpe");
  const [sortOrder, setSortOrder] = useState("desc");
  const [detailModal, setDetailModal] = useState(null);
  const [followedIds, setFollowedIds] = useState(new Set());
  const [upgradeOpen, setUpgradeOpen] = useState(false);

  const loadFollowedIds = useCallback(async () => {
    if (isDemoMode) {
      setFollowedIds(new Set(["demo-1", "demo-2"]));
      return;
    }
    if (!token) return;
    try {
      const res = await axios.get(`${API}/strategies/following/ids`, { headers: { Authorization: `Bearer ${token}` } });
      setFollowedIds(new Set(res.data?.ids || []));
    } catch { }
  }, [isDemoMode, token]);

  const loadStrategies = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/leaderboard/strategies`, {
        params: { sort_by: sortBy, order: sortOrder, limit: 50, demo: isDemoMode },
      });
      if (res.data?.success) {
        setStrategies(res.data.strategies || []);
      }
    } catch (e) {
      console.error("Leaderboard error:", e);
      toast.error("Failed to load leaderboard");
    }
    setLoading(false);
  }, [sortBy, sortOrder, isDemoMode]);

  useEffect(() => { loadStrategies(); }, [loadStrategies]);
  useEffect(() => { loadFollowedIds(); }, [loadFollowedIds]);

  const toggleFollow = async (stratId) => {
    if (isDemoMode) {
      setFollowedIds(prev => {
        const next = new Set(prev);
        if (next.has(stratId)) { next.delete(stratId); toast.success("Strategy unfollowed"); trackEvent("unfollow", { strategy_id: stratId }); }
        else { next.add(stratId); toast.success("Strategy followed! You'll receive signal notifications."); trackEvent("follow", { strategy_id: stratId }); }
        return next;
      });
      return;
    }
    if (!token) { toast.info("Sign in to follow strategies"); return; }
    const isFollowed = followedIds.has(stratId);
    try {
      const endpoint = isFollowed ? `${API}/strategies/${stratId}/unfollow` : `${API}/strategies/${stratId}/follow`;
      const res = await axios.post(endpoint, {}, { headers: { Authorization: `Bearer ${token}` } });
      if (res.data?.success) {
        setFollowedIds(prev => { const n = new Set(prev); isFollowed ? n.delete(stratId) : n.add(stratId); return n; });
        toast.success(isFollowed ? "Strategy unfollowed" : "Strategy followed! You'll receive signal notifications.");
        trackEvent(isFollowed ? "unfollow" : "follow", { strategy_id: stratId });
      }
    } catch (e) {
      if (e.response?.status === 403) {
        setUpgradeOpen(true);
      } else { toast.error("Failed to update follow"); }
    }
  };

  const handleSort = (colApiKey) => {
    if (sortBy === colApiKey) {
      setSortOrder(prev => prev === "desc" ? "asc" : "desc");
    } else {
      setSortBy(colApiKey);
      setSortOrder(colApiKey === "max_drawdown" ? "asc" : "desc");
    }
  };

  const openDetail = async (strat) => {
    trackEvent("strategy_view", { strategy_id: strat.id, name: strat.name });
    if (strat.metrics?.equity_curve?.length > 0) {
      setDetailModal(strat);
      return;
    }
    try {
      const res = await axios.get(`${API}/leaderboard/strategies/${strat.id}`, { params: { demo: isDemoMode } });
      if (res.data?.success) setDetailModal(res.data.strategy);
    } catch {
      setDetailModal(strat);
    }
  };

  const topThree = strategies.slice(0, 3);

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="leaderboard-page">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold font-['Outfit'] flex items-center gap-3" data-testid="leaderboard-title">
                <div className="p-2.5 rounded-xl bg-[#FFB800]/10 border border-[#FFB800]/20">
                  <Trophy className="w-6 h-6 text-[#FFB800]" />
                </div>
                Strategy Leaderboard
              </h1>
              <p className="text-sm text-zinc-500 mt-2 ml-14">Ranked by real market performance using CoinGecko OHLC data</p>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={strategies.length > 0 && strategies[0]?.data_source === "coingecko" ? "bg-[#00FF94]/10 text-[#00FF94] text-[9px]" : "bg-zinc-700 text-zinc-400 text-[9px]"} data-testid="lb-data-source">
                {isDemoMode ? "Demo Mode — Mock Data" : "Data: CoinGecko"}
              </Badge>
              <Button variant="outline" size="sm" onClick={loadStrategies} className="border-zinc-800 rounded-full" data-testid="refresh-btn">
                <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
              </Button>
            </div>
          </div>
        </motion.div>

        {/* Top 3 Podium */}
        {topThree.length >= 3 && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-3 gap-4 mb-8">
            {[1, 0, 2].map((idx, pos) => {
              const s = topThree[idx];
              if (!s) return null;
              const medal = idx === 0 ? { color: "border-[#FFB800]/40 bg-[#FFB800]/5", text: "text-[#FFB800]", label: "1st" } : idx === 1 ? { color: "border-zinc-500/30 bg-zinc-500/5", text: "text-zinc-400", label: "2nd" } : { color: "border-[#CD7F32]/30 bg-[#CD7F32]/5", text: "text-[#CD7F32]", label: "3rd" };
              return (
                <Card key={idx} className={`bg-[#0A0A0A] ${medal.color} ${idx === 0 ? "md:-mt-4" : ""}`} data-testid={`podium-${idx}`}>
                  <CardContent className="p-4 text-center">
                    <div className={`text-2xl font-bold font-mono ${medal.text} mb-2`}>{medal.label}</div>
                    <p className="text-sm font-semibold text-zinc-200 mb-1 truncate">{s.name}</p>
                    <Badge className={typeColors[s.type] || "bg-zinc-700 text-zinc-400"} >{s.type?.replace("_", " ")}</Badge>
                    <div className="mt-3 space-y-1 text-xs font-mono">
                      <div className="flex justify-between"><span className="text-zinc-600">Sharpe</span><span className="text-white font-bold">{s.metrics?.sharpe_ratio}</span></div>
                      <div className="flex justify-between"><span className="text-zinc-600">Return</span><span className={s.metrics?.total_return >= 0 ? "text-[#00FF94]" : "text-red-400"}>{s.metrics?.total_return}%</span></div>
                      <div className="flex justify-between"><span className="text-zinc-600">Win Rate</span><span className="text-zinc-300">{s.metrics?.win_rate}%</span></div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </motion.div>
        )}

        {/* Rankings Table */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-[#7B61FF]" /> All Strategies ({strategies.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              {loading ? (
                <div className="flex items-center justify-center py-16"><Loader2 className="w-6 h-6 animate-spin text-[#7B61FF]" /></div>
              ) : strategies.length === 0 ? (
                <div className="py-16 text-center text-zinc-600 text-sm">No strategies backtested yet. Go to Strategy Lab or Simulation to create one.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full" data-testid="strategy-table">
                    <thead>
                      <tr className="border-b border-zinc-800/50">
                        <th className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider w-12">#</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">Strategy</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">Type</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">Asset</th>
                        {SORT_COLS.map(col => (
                          <th key={col.key} className="px-4 py-3 text-right text-xs font-medium text-zinc-500 uppercase tracking-wider cursor-pointer select-none hover:text-zinc-300 transition-colors" onClick={() => handleSort(col.apiKey)} data-testid={`sort-${col.apiKey}`}>
                            <span className="inline-flex items-center gap-1">
                              {col.label}
                              {sortBy === col.apiKey ? (sortOrder === "desc" ? <ChevronDown className="w-3 h-3 text-[#7B61FF]" /> : <ChevronUp className="w-3 h-3 text-[#7B61FF]" />) : <ArrowUpDown className="w-3 h-3 text-zinc-700" />}
                            </span>
                          </th>
                        ))}
                        <th className="px-4 py-3 text-right text-xs font-medium text-zinc-500 uppercase tracking-wider">Trades</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-zinc-500 uppercase tracking-wider w-28">Follow</th>
                        <th className="px-4 py-3 text-center text-xs font-medium text-zinc-500 uppercase tracking-wider w-20"></th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-zinc-800/30">
                      {strategies.map((s, i) => (
                        <tr key={s.id || i} className="hover:bg-white/[0.02] transition-colors" data-testid={`leaderboard-row-${i}`}>
                          <td className="px-4 py-4">
                            <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${i === 0 ? "bg-[#FFB800]/20 text-[#FFB800]" : i === 1 ? "bg-zinc-400/15 text-zinc-400" : i === 2 ? "bg-[#CD7F32]/15 text-[#CD7F32]" : "bg-zinc-800/50 text-zinc-500"}`}>{i + 1}</div>
                          </td>
                          <td className="px-4 py-4 text-sm font-medium text-zinc-200 max-w-[200px] truncate">{s.name}</td>
                          <td className="px-4 py-4"><Badge className={typeColors[s.type] || "bg-zinc-700 text-zinc-400"} >{s.type?.replace("_", " ")}</Badge></td>
                          <td className="px-4 py-4 text-xs font-mono text-zinc-400">{s.asset}</td>
                          <td className="px-4 py-4 text-right text-sm font-mono font-bold text-white">{s.metrics?.sharpe_ratio}</td>
                          <td className={`px-4 py-4 text-right text-sm font-mono ${(s.metrics?.total_return || 0) >= 0 ? "text-[#00FF94]" : "text-red-400"}`}>{s.metrics?.total_return}%</td>
                          <td className="px-4 py-4 text-right text-sm font-mono text-red-400">{s.metrics?.max_drawdown}%</td>
                          <td className="px-4 py-4 text-right text-sm font-mono text-zinc-300">{s.metrics?.win_rate}%</td>
                          <td className="px-4 py-4 text-right text-xs font-mono text-zinc-500">{s.metrics?.total_trades || "--"}</td>
                          <td className="px-4 py-4 text-center">
                            <Button size="sm" variant={followedIds.has(s.id) ? "default" : "outline"} onClick={(e) => { e.stopPropagation(); toggleFollow(s.id); }} className={`rounded-full text-[10px] h-7 px-3 ${followedIds.has(s.id) ? "bg-red-500/15 text-red-400 border-red-500/30 hover:bg-red-500/25" : "border-zinc-800 hover:border-[#7B61FF]/50"}`} data-testid={`follow-${i}`}>
                              <Heart className={`w-3 h-3 mr-1 ${followedIds.has(s.id) ? "fill-current" : ""}`} /> {followedIds.has(s.id) ? "Following" : "Follow"}
                            </Button>
                          </td>
                          <td className="px-4 py-4 text-center">
                            <Button size="sm" variant="outline" onClick={() => openDetail(s)} className="rounded-full border-zinc-800 hover:border-[#7B61FF]/50 text-[10px] h-7 px-3" data-testid={`view-strategy-${i}`}>View</Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Strategy Detail Modal */}
        <AnimatePresence>
          {detailModal && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setDetailModal(null)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} onClick={e => e.stopPropagation()} className="w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
                <Card className="bg-[#0A0A0A] border-zinc-800" data-testid="strategy-detail-modal">
                  <CardHeader className="border-b border-zinc-800/50 pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base font-semibold text-zinc-100">{detailModal.name}</CardTitle>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className={typeColors[detailModal.type] || "bg-zinc-700 text-zinc-400"}>{detailModal.type?.replace("_", " ")}</Badge>
                          <span className="text-xs font-mono text-zinc-500">{detailModal.asset}</span>
                          <Badge className={detailModal.data_source === "coingecko" ? "bg-[#00FF94]/10 text-[#00FF94] text-[9px]" : "bg-zinc-700 text-zinc-400 text-[9px]"} data-testid="detail-data-source">
                            {detailModal.data_source === "coingecko" ? "Data: CoinGecko" : "Demo Mode — Mock Data"}
                          </Badge>
                        </div>
                      </div>
                      <button onClick={() => setDetailModal(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-5 space-y-5">
                    {/* Key Metrics Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                      {[
                        { label: "Sharpe Ratio", value: detailModal.metrics?.sharpe_ratio, color: "text-white" },
                        { label: "Total Return", value: `${detailModal.metrics?.total_return}%`, color: (detailModal.metrics?.total_return || 0) >= 0 ? "text-[#00FF94]" : "text-red-400" },
                        { label: "Max Drawdown", value: `${detailModal.metrics?.max_drawdown}%`, color: "text-red-400" },
                        { label: "Win Rate", value: `${detailModal.metrics?.win_rate}%`, color: "text-white" },
                      ].map((m, i) => (
                        <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                          <p className="text-[10px] text-zinc-600 uppercase tracking-wider mb-1">{m.label}</p>
                          <p className={`text-lg font-bold font-mono ${m.color}`}>{m.value}</p>
                        </div>
                      ))}
                    </div>

                    {/* Equity Curve */}
                    {detailModal.metrics?.equity_curve?.length > 0 && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1"><TrendingUp className="w-3 h-3" /> Equity Curve</p>
                        <div className="h-32 flex items-end gap-[2px]">
                          {detailModal.metrics.equity_curve.map((pt, i) => {
                            const vals = detailModal.metrics.equity_curve.map(p => p.value);
                            const mn = Math.min(...vals);
                            const mx = Math.max(...vals);
                            const pct = mx > mn ? ((pt.value - mn) / (mx - mn)) * 100 : 50;
                            return (<div key={i} className="flex-1 rounded-t bg-[#00FF94]/50 hover:bg-[#00FF94]/70 transition-colors" style={{ height: `${Math.max(pct, 3)}%` }} title={`$${Math.round(pt.value).toLocaleString()}`} />);
                          })}
                        </div>
                      </div>
                    )}

                    {/* Additional Stats */}
                    <div className="grid grid-cols-3 gap-3 text-center">
                      {[
                        { icon: Zap, label: "Total Trades", value: detailModal.metrics?.total_trades || "--" },
                        { icon: Shield, label: "Profit Factor", value: detailModal.metrics?.profit_factor || "--" },
                        { icon: BarChart3, label: "Capital", value: detailModal.metrics?.initial_capital ? `$${detailModal.metrics.initial_capital.toLocaleString()} → $${(detailModal.metrics.final_capital || 0).toLocaleString()}` : "--" },
                      ].map((m, i) => (
                        <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30">
                          <m.icon className="w-3.5 h-3.5 text-[#7B61FF] mx-auto mb-1" />
                          <p className="text-[10px] text-zinc-600">{m.label}</p>
                          <p className="text-xs font-mono text-zinc-300">{m.value}</p>
                        </div>
                      ))}
                    </div>

                    {/* Parameters */}
                    {detailModal.parameters && Object.keys(detailModal.parameters).length > 0 && (
                      <div>
                        <p className="text-xs text-zinc-500 mb-2">Parameters</p>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(detailModal.parameters).map(([k, v]) => (
                            <Badge key={k} className="bg-zinc-800 text-zinc-400 font-mono text-[10px]">{k}: {String(v)}</Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {detailModal.updated_at && (
                      <p className="text-[10px] text-zinc-700 text-right">Last updated: {new Date(detailModal.updated_at).toLocaleString()}</p>
                    )}

                    <div className="pt-2 border-t border-zinc-800/50">
                      <Button onClick={() => { toggleFollow(detailModal.id); setDetailModal(null); }} className={`w-full rounded-full text-xs ${followedIds.has(detailModal.id) ? "bg-red-500/15 text-red-400 border border-red-500/30 hover:bg-red-500/25" : "bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white"}`} data-testid="detail-follow-btn">
                        <Heart className={`w-3.5 h-3.5 mr-1.5 ${followedIds.has(detailModal.id) ? "fill-current" : ""}`} /> {followedIds.has(detailModal.id) ? "Unfollow Strategy" : "Follow Strategy"}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        <UpgradeModal open={upgradeOpen} onClose={() => setUpgradeOpen(false)} feature="Unlimited strategy follows" />
      </div>
    </div>
  );
};

export default LeaderboardPage;
