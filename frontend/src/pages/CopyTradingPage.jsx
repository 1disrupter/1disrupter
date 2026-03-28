/**
 * AlphaAI Copy Trading Page
 * Manage copy relationships, pending approvals, and following/followers.
 */
import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Switch } from '../components/ui/switch';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from '../components/ui/dialog';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '../components/ui/select';
import {
  Users, UserPlus, Settings, Check, X, AlertCircle, Loader2,
  TrendingUp, DollarSign, Target, Shield, RefreshCw, Pause,
  Play, Trash2, Bell, ArrowUpRight, ArrowDownRight, Copy
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============= FOLLOW TRADER MODAL =============
export const FollowTraderModal = ({ open, onOpenChange, traderId, traderName, token, onSuccess }) => {
  const [mode, setMode] = useState('auto');
  const [allocation, setAllocation] = useState(10);
  const [maxPerTrade, setMaxPerTrade] = useState(500);
  const [loading, setLoading] = useState(false);

  const handleFollow = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/copy/follow`, {
        trader_id: traderId,
        mode,
        allocation_percent: allocation,
        max_per_trade: maxPerTrade,
      }, { headers: { Authorization: `Bearer ${token}` } });

      if (res.data.success) {
        toast.success(`Now following ${traderName}!`);
        onSuccess?.();
        onOpenChange(false);
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to follow trader');
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#121212] border-zinc-800 max-w-md" data-testid="follow-trader-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-[#7B61FF]" />
            Follow {traderName}
          </DialogTitle>
          <DialogDescription>Configure how trades are copied to your portfolio</DialogDescription>
        </DialogHeader>

        <div className="space-y-5 py-2">
          {/* Mode Selection */}
          <div>
            <label className="text-sm text-zinc-400 mb-2 block">Copy Mode</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setMode('auto')}
                className={`p-3 rounded-lg border text-left transition-all ${
                  mode === 'auto' ? 'border-[#7B61FF] bg-[#7B61FF]/10' : 'border-zinc-800 bg-[#050505]'
                }`}
                data-testid="mode-auto-btn"
              >
                <Play className={`w-4 h-4 mb-1 ${mode === 'auto' ? 'text-[#7B61FF]' : 'text-zinc-500'}`} />
                <p className="text-sm font-medium">Auto Copy</p>
                <p className="text-xs text-zinc-500">Trades execute immediately</p>
              </button>
              <button
                onClick={() => setMode('manual')}
                className={`p-3 rounded-lg border text-left transition-all ${
                  mode === 'manual' ? 'border-[#7B61FF] bg-[#7B61FF]/10' : 'border-zinc-800 bg-[#050505]'
                }`}
                data-testid="mode-manual-btn"
              >
                <Bell className={`w-4 h-4 mb-1 ${mode === 'manual' ? 'text-[#7B61FF]' : 'text-zinc-500'}`} />
                <p className="text-sm font-medium">Manual Approve</p>
                <p className="text-xs text-zinc-500">Approve each trade</p>
              </button>
            </div>
          </div>

          {/* Allocation % */}
          <div>
            <label className="text-sm text-zinc-400 mb-2 block">
              Allocation Percentage — <span className="text-white font-mono">{allocation}%</span>
            </label>
            <input
              type="range"
              min="1"
              max="100"
              value={allocation}
              onChange={(e) => setAllocation(Number(e.target.value))}
              className="w-full accent-[#7B61FF]"
              data-testid="allocation-slider"
            />
            <div className="flex justify-between text-xs text-zinc-600 mt-1">
              <span>1%</span><span>50%</span><span>100%</span>
            </div>
          </div>

          {/* Max Per Trade */}
          <div>
            <label className="text-sm text-zinc-400 mb-2 block">Max Per Trade (USD)</label>
            <div className="flex gap-2">
              {[100, 250, 500, 1000].map(amt => (
                <button
                  key={amt}
                  onClick={() => setMaxPerTrade(amt)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                    maxPerTrade === amt ? 'bg-[#7B61FF] text-white' : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                  }`}
                >
                  ${amt}
                </button>
              ))}
            </div>
            <Input
              type="number"
              value={maxPerTrade}
              onChange={(e) => setMaxPerTrade(Number(e.target.value))}
              className="mt-2 bg-[#050505] border-zinc-800"
              placeholder="Custom amount"
              data-testid="max-per-trade-input"
            />
          </div>

          {/* Summary */}
          <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-sm">
            <p className="text-zinc-400">When {traderName} trades <span className="text-white font-mono">$1,000</span>:</p>
            <p className="text-white mt-1">
              You&apos;ll {mode === 'auto' ? 'automatically' : 'be asked to'} trade{' '}
              <span className="text-[#7B61FF] font-mono font-bold">
                ${Math.min(1000 * allocation / 100, maxPerTrade).toFixed(0)}
              </span>
            </p>
          </div>
        </div>

        <DialogFooter className="gap-2">
          <Button
            onClick={handleFollow}
            disabled={loading}
            className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 h-11"
            data-testid="confirm-follow-btn"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : (
              <>
                <UserPlus className="w-4 h-4 mr-2" />
                Start Copying
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============= COPY SETTINGS MODAL =============
const EditSettingsModal = ({ open, onOpenChange, relationship, token, onSuccess }) => {
  const [mode, setMode] = useState(relationship?.mode || 'auto');
  const [allocation, setAllocation] = useState(relationship?.allocation_percent || 10);
  const [maxPerTrade, setMaxPerTrade] = useState(relationship?.max_per_trade || 500);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (relationship) {
      setMode(relationship.mode);
      setAllocation(relationship.allocation_percent);
      setMaxPerTrade(relationship.max_per_trade);
    }
  }, [relationship]);

  const handleSave = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/copy/settings`, {
        relationship_id: relationship.id,
        mode,
        allocation_percent: allocation,
        max_per_trade: maxPerTrade,
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Settings updated');
      onSuccess?.();
      onOpenChange(false);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update settings');
    }
    setLoading(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="bg-[#121212] border-zinc-800 max-w-md" data-testid="edit-settings-modal">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-[#7B61FF]" />
            Copy Settings
          </DialogTitle>
          <DialogDescription className="text-zinc-500">
            Adjust how trades are copied from this trader
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-5 py-2">
          <div>
            <label className="text-sm text-zinc-400 mb-2 block">Copy Mode</label>
            <Select value={mode} onValueChange={setMode}>
              <SelectTrigger className="bg-[#050505] border-zinc-800" data-testid="edit-mode-select">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="auto">Auto Copy</SelectItem>
                <SelectItem value="manual">Manual Approve</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="text-sm text-zinc-400 mb-2 block">
              Allocation — <span className="text-white font-mono">{allocation}%</span>
            </label>
            <input type="range" min="1" max="100" value={allocation}
              onChange={(e) => setAllocation(Number(e.target.value))}
              className="w-full accent-[#7B61FF]"
              data-testid="edit-allocation-slider"
            />
          </div>

          <div>
            <label className="text-sm text-zinc-400 mb-2 block">Max Per Trade (USD)</label>
            <Input type="number" value={maxPerTrade} onChange={(e) => setMaxPerTrade(Number(e.target.value))}
              className="bg-[#050505] border-zinc-800" data-testid="edit-max-input"
            />
          </div>
        </div>

        <DialogFooter>
          <Button onClick={handleSave} disabled={loading} className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
            data-testid="save-settings-btn"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Save Changes'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// ============= MAIN COPY TRADING PAGE =============
const CopyTradingPage = () => {
  const { user, tokens } = useAuth();
  const [following, setFollowing] = useState([]);
  const [followers, setFollowers] = useState([]);
  const [pendingTrades, setPendingTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editRel, setEditRel] = useState(null);
  const [editOpen, setEditOpen] = useState(false);
  const [actionLoading, setActionLoading] = useState({});

  const isPro = user?.is_pro || user?.is_elite;
  const token = tokens?.access_token;

  const loadData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [fRes, flRes, pRes] = await Promise.all([
        axios.get(`${API}/copy/following`, { headers }),
        axios.get(`${API}/copy/followers`, { headers }),
        axios.get(`${API}/copy/pending`, { headers }),
      ]);
      setFollowing(fRes.data.following || []);
      setFollowers(flRes.data.followers || []);
      setPendingTrades(pRes.data.pending_trades || []);
    } catch (err) {
      console.error('Copy trading data error:', err);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { loadData(); }, [loadData]);

  const handleUnfollow = async (relId) => {
    setActionLoading(prev => ({ ...prev, [relId]: true }));
    try {
      await axios.delete(`${API}/copy/unfollow/${relId}`, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Unfollowed trader');
      loadData();
    } catch (err) {
      toast.error('Failed to unfollow');
    }
    setActionLoading(prev => ({ ...prev, [relId]: false }));
  };

  const handleTogglePause = async (rel) => {
    const newStatus = rel.status === 'active' ? 'paused' : 'active';
    setActionLoading(prev => ({ ...prev, [rel.id]: true }));
    try {
      await axios.put(`${API}/copy/settings`, {
        relationship_id: rel.id,
        status: newStatus,
      }, { headers: { Authorization: `Bearer ${token}` } });
      toast.success(newStatus === 'active' ? 'Resumed copying' : 'Paused copying');
      loadData();
    } catch (err) {
      toast.error('Failed to update');
    }
    setActionLoading(prev => ({ ...prev, [rel.id]: false }));
  };

  const handleApprove = async (tradeId) => {
    setActionLoading(prev => ({ ...prev, [tradeId]: 'approve' }));
    try {
      await axios.post(`${API}/copy/approve/${tradeId}`, {}, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Trade approved and executed');
      loadData();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to approve');
    }
    setActionLoading(prev => ({ ...prev, [tradeId]: false }));
  };

  const handleReject = async (tradeId) => {
    setActionLoading(prev => ({ ...prev, [tradeId]: 'reject' }));
    try {
      await axios.post(`${API}/copy/reject/${tradeId}`, {}, { headers: { Authorization: `Bearer ${token}` } });
      toast.success('Trade rejected');
      loadData();
    } catch (err) {
      toast.error('Failed to reject');
    }
    setActionLoading(prev => ({ ...prev, [tradeId]: false }));
  };

  if (!isPro) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4" data-testid="copy-trading-page">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-[#7B61FF]/10">
                <Copy className="w-6 h-6 text-[#7B61FF]" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold font-['Outfit'] tracking-tight">Copy Trading</h1>
              <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] border border-[#7B61FF]/30 text-xs">Pro</Badge>
            </div>
            <p className="text-zinc-500 text-sm md:text-base ml-0 md:ml-14">Mirror trades from top-performing traders automatically</p>
          </motion.div>

          {/* Stats Preview */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Top Traders', value: '48', sub: 'Available to follow' },
              { label: 'Avg Win Rate', value: '72%', sub: 'Top 10 traders' },
              { label: 'Total Copied', value: '$2.4M', sub: 'This month' },
              { label: 'Avg Return', value: '+11.2%', sub: 'Monthly' },
            ].map((s, i) => (
              <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-5">
                  <p className="text-xs text-zinc-500 mb-1.5 uppercase tracking-wider">{s.label}</p>
                  <p className="text-xl font-bold font-['JetBrains_Mono'] text-white/40">{s.value}</p>
                  <p className="text-[11px] text-zinc-700 mt-1">{s.sub}</p>
                </CardContent>
              </Card>
            ))}
          </motion.div>

          {/* Top Traders Preview */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mb-8">
            <h3 className="text-sm text-zinc-600 uppercase tracking-wider mb-4">Top Traders Preview</h3>
            <div className="space-y-3 opacity-50">
              {[
                { name: 'CryptoWhale', winRate: '76%', pnl: '+$48.2K', followers: 342 },
                { name: 'AlphaTrader', winRate: '71%', pnl: '+$32.1K', followers: 189 },
                { name: 'SolanaSniper', winRate: '69%', pnl: '+$28.4K', followers: 267 },
              ].map((t, i) => (
                <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50">
                  <CardContent className="p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-[#7B61FF]/20 flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-[#7B61FF]" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">{t.name}</p>
                        <p className="text-xs text-zinc-600">{t.followers} followers</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6 text-sm font-mono">
                      <span className="text-zinc-400">{t.winRate} win</span>
                      <span className="text-[#00FF94]/60">{t.pnl}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.div>

          {/* Upgrade CTA */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card className="bg-gradient-to-r from-[#7B61FF]/10 to-transparent border-[#7B61FF]/20">
              <CardContent className="p-8 text-center">
                <Shield className="w-10 h-10 mx-auto text-[#7B61FF] mb-3" />
                <h2 className="text-lg font-bold font-['Outfit'] mb-2">Unlock Copy Trading</h2>
                <p className="text-sm text-zinc-500 mb-5 max-w-md mx-auto">
                  Upgrade to Pro to automatically mirror trades from top-performing traders in real time
                </p>
                <Button asChild className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8">
                  <Link to="/pricing" data-testid="upgrade-cta-btn">Upgrade to Pro — $49/mo</Link>
                </Button>
                <p className="text-[11px] text-zinc-600 mt-3">Cancel anytime. No lock-in.</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="copy-trading-page">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="copy-trading-title">
              <Copy className="inline w-8 h-8 mr-2 text-[#7B61FF]" />
              Copy Trading
            </h1>
            <p className="text-zinc-400 mt-1">Mirror trades from top traders automatically</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={loadData} className="border-zinc-700" data-testid="refresh-btn">
              <RefreshCw className="w-4 h-4 mr-2" /> Refresh
            </Button>
            <Button asChild className="bg-[#7B61FF] hover:bg-[#7B61FF]/90">
              <Link to="/leaderboard" data-testid="find-traders-btn">
                <UserPlus className="w-4 h-4 mr-2" /> Find Traders
              </Link>
            </Button>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card">
            <CardContent className="pt-4 pb-4">
              <p className="text-xs text-zinc-500">Following</p>
              <p className="text-2xl font-bold font-mono" data-testid="following-count">{following.length}</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="pt-4 pb-4">
              <p className="text-xs text-zinc-500">Followers</p>
              <p className="text-2xl font-bold font-mono" data-testid="followers-count">{followers.length}</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="pt-4 pb-4">
              <p className="text-xs text-zinc-500">Trades Copied</p>
              <p className="text-2xl font-bold font-mono text-[#00FF94]" data-testid="trades-copied-count">
                {following.reduce((sum, r) => sum + (r.stats?.trades_copied || 0), 0)}
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="pt-4 pb-4">
              <p className="text-xs text-zinc-500">Pending Approvals</p>
              <p className="text-2xl font-bold font-mono text-[#FFB800]" data-testid="pending-count">
                {pendingTrades.length}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Tabs */}
        <Tabs defaultValue="following" className="space-y-6">
          <TabsList className="bg-[#121212] border border-zinc-800">
            <TabsTrigger value="following" data-testid="tab-following">
              Following ({following.length})
            </TabsTrigger>
            <TabsTrigger value="pending" data-testid="tab-pending">
              Pending {pendingTrades.length > 0 && (
                <Badge className="ml-2 bg-[#FFB800]/20 text-[#FFB800]">{pendingTrades.length}</Badge>
              )}
            </TabsTrigger>
            <TabsTrigger value="followers" data-testid="tab-followers">
              Followers ({followers.length})
            </TabsTrigger>
          </TabsList>

          {/* Following Tab */}
          <TabsContent value="following">
            {loading ? (
              <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-[#7B61FF]" />
              </div>
            ) : following.length === 0 ? (
              <Card className="glass-card">
                <CardContent className="text-center py-12">
                  <Users className="w-12 h-12 mx-auto text-zinc-600 mb-3" />
                  <p className="text-zinc-400 mb-4">You&apos;re not following any traders yet</p>
                  <Button asChild className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 rounded-full">
                    <Link to="/leaderboard">Browse Leaderboard</Link>
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {following.map((rel) => (
                  <motion.div key={rel.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                    <Card className="glass-card" data-testid={`following-card-${rel.trader_id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className="w-12 h-12 rounded-full bg-[#7B61FF]/20 flex items-center justify-center">
                              <TrendingUp className="w-6 h-6 text-[#7B61FF]" />
                            </div>
                            <div>
                              <p className="font-medium text-lg">{rel.trader_display_name}</p>
                              <div className="flex items-center gap-3 text-sm text-zinc-500">
                                <Badge className={`text-xs ${rel.mode === 'auto' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-[#FFB800]/20 text-[#FFB800]'}`}>
                                  {rel.mode === 'auto' ? 'AUTO' : 'MANUAL'}
                                </Badge>
                                <span>{rel.allocation_percent}% allocation</span>
                                <span>Max ${rel.max_per_trade}</span>
                                {rel.status === 'paused' && (
                                  <Badge className="bg-zinc-700 text-zinc-400 text-xs">PAUSED</Badge>
                                )}
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <p className="text-xs text-zinc-500">Trades Copied</p>
                              <p className="font-mono font-bold">{rel.stats?.trades_copied || 0}</p>
                            </div>
                            <div className="flex gap-1">
                              <Button size="sm" variant="ghost"
                                onClick={() => handleTogglePause(rel)}
                                disabled={!!actionLoading[rel.id]}
                                className="text-zinc-400 hover:text-white"
                                data-testid={`toggle-pause-${rel.trader_id}`}
                              >
                                {rel.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                              </Button>
                              <Button size="sm" variant="ghost"
                                onClick={() => { setEditRel(rel); setEditOpen(true); }}
                                className="text-zinc-400 hover:text-white"
                                data-testid={`edit-settings-${rel.trader_id}`}
                              >
                                <Settings className="w-4 h-4" />
                              </Button>
                              <Button size="sm" variant="ghost"
                                onClick={() => handleUnfollow(rel.id)}
                                disabled={!!actionLoading[rel.id]}
                                className="text-red-400 hover:text-red-300"
                                data-testid={`unfollow-${rel.trader_id}`}
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Pending Trades Tab */}
          <TabsContent value="pending">
            {pendingTrades.length === 0 ? (
              <Card className="glass-card">
                <CardContent className="text-center py-12">
                  <Bell className="w-12 h-12 mx-auto text-zinc-600 mb-3" />
                  <p className="text-zinc-400">No pending trade approvals</p>
                  <p className="text-xs text-zinc-600 mt-1">Trades from manual-mode followed traders will appear here</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {pendingTrades.map((trade) => (
                  <motion.div key={trade.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                    <Card className="glass-card border-[#FFB800]/20" data-testid={`pending-trade-${trade.id}`}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-4">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              trade.side?.toUpperCase() === 'BUY' ? 'bg-[#00FF94]/20' : 'bg-red-400/20'
                            }`}>
                              {trade.side?.toUpperCase() === 'BUY'
                                ? <ArrowUpRight className="w-5 h-5 text-[#00FF94]" />
                                : <ArrowDownRight className="w-5 h-5 text-red-400" />}
                            </div>
                            <div>
                              <p className="font-medium">
                                <Badge className={trade.side?.toUpperCase() === 'BUY' ? 'bg-[#00FF94]/20 text-[#00FF94] mr-2' : 'bg-red-400/20 text-red-400 mr-2'}>
                                  {trade.side?.toUpperCase()}
                                </Badge>
                                <span className="font-mono">{trade.symbol}</span>
                              </p>
                              <p className="text-sm text-zinc-500">
                                Amount: <span className="text-white font-mono">${trade.scaled_amount?.toFixed(2)}</span>
                                {' '} (from ${trade.original_amount?.toFixed(2)} original)
                              </p>
                            </div>
                          </div>

                          <div className="flex gap-2">
                            <Button size="sm"
                              onClick={() => handleApprove(trade.id)}
                              disabled={!!actionLoading[trade.id]}
                              className="bg-[#00FF94] hover:bg-[#00FF94]/80 text-black"
                              data-testid={`approve-${trade.id}`}
                            >
                              {actionLoading[trade.id] === 'approve' ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Check className="w-4 h-4 mr-1" /> Approve</>}
                            </Button>
                            <Button size="sm" variant="outline"
                              onClick={() => handleReject(trade.id)}
                              disabled={!!actionLoading[trade.id]}
                              className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                              data-testid={`reject-${trade.id}`}
                            >
                              {actionLoading[trade.id] === 'reject' ? <Loader2 className="w-4 h-4 animate-spin" /> : <><X className="w-4 h-4 mr-1" /> Reject</>}
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Followers Tab */}
          <TabsContent value="followers">
            {followers.length === 0 ? (
              <Card className="glass-card">
                <CardContent className="text-center py-12">
                  <Users className="w-12 h-12 mx-auto text-zinc-600 mb-3" />
                  <p className="text-zinc-400">No one is copying your trades yet</p>
                  <p className="text-xs text-zinc-600 mt-1">Make your profile public on the leaderboard to attract followers</p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-3">
                {followers.map((rel) => (
                  <Card key={rel.id} className="glass-card" data-testid={`follower-card-${rel.copier_id}`}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-zinc-800 flex items-center justify-center">
                            <Users className="w-5 h-5 text-zinc-400" />
                          </div>
                          <div>
                            <p className="font-medium">{rel.copier_name}</p>
                            <div className="flex items-center gap-2 text-xs text-zinc-500">
                              <Badge className={`text-xs ${rel.mode === 'auto' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-[#FFB800]/20 text-[#FFB800]'}`}>
                                {rel.mode?.toUpperCase()}
                              </Badge>
                              <span>{rel.allocation_percent}%</span>
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-xs text-zinc-500">Trades Copied</p>
                          <p className="font-mono">{rel.stats?.trades_copied || 0}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>

      {/* Edit Settings Modal */}
      {editRel && (
        <EditSettingsModal
          open={editOpen}
          onOpenChange={setEditOpen}
          relationship={editRel}
          token={token}
          onSuccess={loadData}
        />
      )}
    </div>
  );
};

export default CopyTradingPage;
