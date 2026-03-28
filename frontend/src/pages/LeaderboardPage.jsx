import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Copy, DollarSign, Lock, RefreshCw, Target, TrendingUp, Trophy, User
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle
} from "../components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "../components/ui/select";
import { useAuth } from "../contexts/AuthContext";
import { FollowTraderModal } from "./CopyTradingPage";
import { API } from "../lib/constants";

const LeaderboardPage = () => {
  const { user, tokens } = useAuth();
  const [traders, setTraders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('all_time');
  const [sortBy, setSortBy] = useState('pnl');
  const [myRank, setMyRank] = useState(null);
  const [topPerformers, setTopPerformers] = useState(null);
  const [selectedTrader, setSelectedTrader] = useState(null);
  const [traderDetailOpen, setTraderDetailOpen] = useState(false);
  const [followModalOpen, setFollowModalOpen] = useState(false);
  const [followTarget, setFollowTarget] = useState(null);

  const userTier = user?.user_tier || (user?.is_elite ? 'elite' : user?.is_pro ? 'pro' : 'free');
  const isPro = userTier !== 'free';

  useEffect(() => {
    loadLeaderboard();
    loadTopPerformers();
    if (user?.id) loadMyRank();
  }, [period, sortBy, user]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/leaderboard?period=${period}&sort_by=${sortBy}&user_tier=${userTier}&limit=50`);
      setTraders(res.data.traders || []);
    } catch (error) {
      console.error('Leaderboard error:', error);
    }
    setLoading(false);
  };

  const loadTopPerformers = async () => {
    try {
      const res = await axios.get(`${API}/leaderboard/top-performers?limit=5`);
      setTopPerformers(res.data);
    } catch (error) {
      console.error('Top performers error:', error);
    }
  };

  const loadMyRank = async () => {
    try {
      const res = await axios.get(`${API}/leaderboard/me?user_id=${user.id}`);
      setMyRank(res.data);
    } catch (error) {
      console.error('My rank error:', error);
    }
  };

  const viewTraderProfile = async (traderId) => {
    try {
      const res = await axios.get(`${API}/leaderboard/trader/${traderId}?user_tier=${userTier}`);
      setSelectedTrader(res.data);
      setTraderDetailOpen(true);
    } catch (error) {
      toast.error('Failed to load trader profile');
    }
  };

  const formatPnl = (value) => {
    if (value === undefined || value === null) return '-';
    const formatted = Math.abs(value).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    return value >= 0 ? `+${formatted}` : `-${formatted.replace('$', '')}`;
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="leaderboard-title">
              <Trophy className="inline w-8 h-8 mr-2 text-[#FFB800]" />
              Leaderboard
            </h1>
            <p className="text-zinc-400 mt-1">Top performing traders on AlphaAI</p>
          </div>
          {myRank && myRank.ranks?.pnl && (
            <div className="text-right">
              <p className="text-sm text-zinc-500">Your Rank</p>
              <p className="text-2xl font-bold text-[#7B61FF]">#{myRank.ranks.pnl}</p>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-6">
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-36 bg-[#121212] border-zinc-800" data-testid="period-select">
              <SelectValue placeholder="Period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
              <SelectItem value="all_time">All Time</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-36 bg-[#121212] border-zinc-800" data-testid="sort-select">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pnl">Total P&L</SelectItem>
              <SelectItem value="win_rate">Win Rate</SelectItem>
              <SelectItem value="roi">ROI %</SelectItem>
              <SelectItem value="total_trades">Trades</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" onClick={loadLeaderboard} className="border-zinc-700">
            <RefreshCw className="w-4 h-4 mr-2" /> Refresh
          </Button>
        </div>

        {/* Top Performers Cards */}
        {topPerformers && (
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <Card className="glass-card border-[#FFB800]/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-[#FFB800]" /> Top P&L
                </CardTitle>
              </CardHeader>
              <CardContent>
                {topPerformers.top_by_pnl?.slice(0, 3).map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[#FFB800] font-bold">{i + 1}</span>
                      <span className="text-sm truncate">{t.display_name || `Trader_${t.user_id?.slice(0,6)}`}</span>
                    </div>
                    <span className="text-[#00FF94] font-mono text-sm">{formatPnl(t.stats?.total_pnl)}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="glass-card border-[#00FF94]/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Target className="w-4 h-4 text-[#00FF94]" /> Top Win Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                {topPerformers.top_by_win_rate?.slice(0, 3).map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[#00FF94] font-bold">{i + 1}</span>
                      <span className="text-sm truncate">{t.display_name || `Trader_${t.user_id?.slice(0,6)}`}</span>
                    </div>
                    <span className="text-white font-mono text-sm">{t.stats?.win_rate?.toFixed(1)}%</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="glass-card border-[#7B61FF]/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-[#7B61FF]" /> Top ROI
                </CardTitle>
              </CardHeader>
              <CardContent>
                {topPerformers.top_by_roi?.slice(0, 3).map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[#7B61FF] font-bold">{i + 1}</span>
                      <span className="text-sm truncate">{t.display_name || `Trader_${t.user_id?.slice(0,6)}`}</span>
                    </div>
                    <span className="text-white font-mono text-sm">{t.stats?.roi_percentage?.toFixed(1)}%</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Leaderboard */}
        <Card className="glass-card">
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-zinc-800">
                      <th className="text-left p-4 text-zinc-500 text-sm">Rank</th>
                      <th className="text-left p-4 text-zinc-500 text-sm">Trader</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Total P&L</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Win Rate</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">ROI</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Trades</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {traders.map((trader, i) => (
                      <tr key={trader.user_id} className="border-b border-zinc-800/50 hover:bg-[#050505]/50" data-testid={`leaderboard-row-${i}`}>
                        <td className="p-4">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                            trader.rank_position === 1 ? 'bg-[#FFB800]/20 text-[#FFB800]' :
                            trader.rank_position === 2 ? 'bg-zinc-400/20 text-zinc-400' :
                            trader.rank_position === 3 ? 'bg-[#CD7F32]/20 text-[#CD7F32]' :
                            'bg-zinc-800 text-zinc-400'
                          }`}>
                            {trader.rank_position}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{trader.display_name || `Trader_${trader.user_id?.slice(0,6)}`}</span>
                            {trader.is_elite && <Badge className="bg-[#FFB800]/20 text-[#FFB800] text-xs">ELITE</Badge>}
                            {trader.is_pro && !trader.is_elite && <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-xs">PRO</Badge>}
                          </div>
                        </td>
                        <td className={`p-4 text-right font-mono ${trader.stats?.total_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {formatPnl(trader.stats?.total_pnl)}
                        </td>
                        <td className="p-4 text-right font-mono">
                          {trader.stats?.win_rate?.toFixed(1) || '-'}%
                        </td>
                        <td className={`p-4 text-right font-mono ${(trader.stats?.roi_percentage || 0) >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {trader.stats?.roi_percentage?.toFixed(1) || '-'}%
                        </td>
                        <td className="p-4 text-right font-mono text-zinc-400">
                          {trader.stats?.total_trades || 0}
                        </td>
                        <td className="p-4 text-right">
                          <div className="flex justify-end gap-1">
                            {isPro && trader.user_id !== user?.id && (
                              <Button size="sm" onClick={() => { setFollowTarget(trader); setFollowModalOpen(true); }}
                                className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-xs"
                                data-testid={`follow-btn-${trader.user_id}`}
                              >
                                <Copy className="w-3 h-3 mr-1" /> Copy
                              </Button>
                            )}
                            <Button size="sm" variant="outline" onClick={() => viewTraderProfile(trader.user_id)} className="border-zinc-700">
                              View
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {!isPro && traders.length >= 10 && (
              <div className="p-4 border-t border-zinc-800 bg-[#7B61FF]/5 text-center" data-testid="leaderboard-upgrade-cta">
                <Lock className="inline w-4 h-4 mr-1 text-[#7B61FF]" />
                <p className="text-sm text-zinc-400 inline">
                  Free users can only see the Top 10. 
                </p>
                <Button asChild size="sm" variant="link" className="text-[#7B61FF] p-0 ml-1">
                  <Link to="/pricing">Upgrade to Pro</Link>
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trader Detail Dialog */}
        <Dialog open={traderDetailOpen} onOpenChange={setTraderDetailOpen}>
          <DialogContent className="bg-[#121212] border-zinc-800 max-w-lg">
            <DialogHeader>
              <DialogTitle>Trader Profile</DialogTitle>
            </DialogHeader>
            {selectedTrader && (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-[#7B61FF]/20 flex items-center justify-center">
                    <User className="w-8 h-8 text-[#7B61FF]" />
                  </div>
                  <div>
                    <p className="text-xl font-bold">{selectedTrader.display_name || `Trader_${selectedTrader.user_id?.slice(0,6)}`}</p>
                    <div className="flex gap-2 mt-1">
                      {selectedTrader.is_elite && <Badge className="bg-[#FFB800]/20 text-[#FFB800]">ELITE</Badge>}
                      {selectedTrader.is_pro && !selectedTrader.is_elite && <Badge className="bg-[#7B61FF]/20 text-[#7B61FF]">PRO</Badge>}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">Total P&L</p>
                    <p className={`text-lg font-mono ${selectedTrader.stats?.total_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {formatPnl(selectedTrader.stats?.total_pnl)}
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">Win Rate</p>
                    <p className="text-lg font-mono">{selectedTrader.stats?.win_rate?.toFixed(1) || '-'}%</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">ROI</p>
                    <p className={`text-lg font-mono ${(selectedTrader.stats?.roi_percentage || 0) >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {selectedTrader.stats?.roi_percentage?.toFixed(1) || '-'}%
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">Total Trades</p>
                    <p className="text-lg font-mono">{selectedTrader.stats?.total_trades || 0}</p>
                  </div>
                </div>

                {selectedTrader.recent_trades && selectedTrader.recent_trades.length > 0 && (
                  <div>
                    <p className="text-sm text-zinc-500 mb-2">Recent Trades</p>
                    <div className="space-y-2">
                      {selectedTrader.recent_trades.slice(0, 5).map((trade, i) => (
                        <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#050505]">
                          <div className="flex items-center gap-2">
                            <Badge className={trade.side === 'buy' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-400/20 text-red-400'}>
                              {trade.side?.toUpperCase()}
                            </Badge>
                            <span className="font-mono">{trade.symbol}</span>
                          </div>
                          <span className={`font-mono ${trade.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                            {formatPnl(trade.pnl)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {!isPro && (
                  <div className="p-3 rounded-lg bg-[#7B61FF]/10 border border-[#7B61FF]/30 text-center">
                    <p className="text-sm text-zinc-400">
                      Upgrade to Pro to see full trade history and copy this trader
                    </p>
                  </div>
                )}

                {isPro && selectedTrader.user_id !== user?.id && (
                  <Button
                    onClick={() => { setFollowTarget(selectedTrader); setFollowModalOpen(true); setTraderDetailOpen(false); }}
                    className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
                    data-testid="follow-from-profile-btn"
                  >
                    <Copy className="w-4 h-4 mr-2" /> Copy This Trader
                  </Button>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Follow Trader Modal */}
        {followTarget && (
          <FollowTraderModal
            open={followModalOpen}
            onOpenChange={setFollowModalOpen}
            traderId={followTarget.user_id}
            traderName={followTarget.display_name || `Trader_${followTarget.user_id?.slice(0,6)}`}
            token={tokens?.access_token}
            onSuccess={() => toast.success('Navigate to Copy Trading to manage your follows')}
          />
        )}
      </div>
    </div>
  );
};

// Main App

export default LeaderboardPage;
