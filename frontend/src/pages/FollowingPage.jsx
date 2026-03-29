import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import { Heart, TrendingUp, X, Loader2, BarChart3, Shield, Zap, UserMinus } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { API } from "../lib/constants";

const typeColors = { momentum: "bg-[#7B61FF]/15 text-[#7B61FF]", mean_reversion: "bg-[#00FF94]/15 text-[#00FF94]", breakout: "bg-[#FFB800]/15 text-[#FFB800]" };

const FollowingPage = () => {
  const { isDemoMode } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isPro, setIsPro] = useState(false);
  const [detailModal, setDetailModal] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const url = isDemoMode ? `${API}/strategies/following/demo` : `${API}/strategies/following`;
      const headers = !isDemoMode && token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.get(url, { headers });
      if (res.data?.success) {
        setStrategies(res.data.following || []);
        setIsPro(res.data.is_pro || false);
      }
    } catch { }
    setLoading(false);
  }, [isDemoMode, token]);

  useEffect(() => { load(); }, [load]);

  const unfollow = async (stratId) => {
    if (isDemoMode) {
      setStrategies(prev => prev.filter(s => s.id !== stratId));
      toast.success("Strategy unfollowed");
      return;
    }
    try {
      await axios.post(`${API}/strategies/${stratId}/unfollow`, {}, { headers: { Authorization: `Bearer ${token}` } });
      setStrategies(prev => prev.filter(s => s.id !== stratId));
      toast.success("Strategy unfollowed");
    } catch {
      toast.error("Failed to unfollow");
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="following-page">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold font-['Outfit'] flex items-center gap-3" data-testid="following-title">
                <div className="p-2.5 rounded-xl bg-red-500/10 border border-red-500/20">
                  <Heart className="w-6 h-6 text-red-400" />
                </div>
                Following
              </h1>
              <p className="text-sm text-zinc-500 mt-2 ml-14">Strategies you follow — receive signal notifications automatically</p>
            </div>
            <Badge className={isDemoMode ? "bg-zinc-700 text-zinc-400 text-[9px]" : isPro ? "bg-[#7B61FF]/10 text-[#7B61FF] text-[9px]" : "bg-zinc-700 text-zinc-400 text-[9px]"}>
              {isDemoMode ? "Demo Mode" : isPro ? "Pro — Unlimited" : `Free — ${strategies.length}/1 follows`}
            </Badge>
          </div>
        </motion.div>

        {loading ? (
          <div className="flex items-center justify-center py-20"><Loader2 className="w-6 h-6 animate-spin text-[#7B61FF]" /></div>
        ) : strategies.length === 0 ? (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50 border-dashed">
              <CardContent className="py-16 text-center">
                <Heart className="w-10 h-10 text-zinc-700 mx-auto mb-4" />
                <h3 className="text-sm font-semibold text-zinc-400 mb-2">No strategies followed yet</h3>
                <p className="text-xs text-zinc-600 mb-4">Visit the Leaderboard to find and follow top-performing strategies</p>
                <a href={isDemoMode ? "/leaderboard?demo=true" : "/leaderboard"}>
                  <Button className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white text-xs">Browse Leaderboard</Button>
                </a>
              </CardContent>
            </Card>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {strategies.map((s, i) => (
              <motion.div key={s.id} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-all" data-testid={`following-card-${i}`}>
                  <CardContent className="p-5">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        <div className="p-2 rounded-lg bg-[#7B61FF]/10"><TrendingUp className="w-5 h-5 text-[#7B61FF]" /></div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="text-sm font-semibold text-zinc-200 truncate">{s.name}</h3>
                            <Badge className={typeColors[s.type] || "bg-zinc-700 text-zinc-400"} >{s.type?.replace("_", " ")}</Badge>
                            <span className="text-[10px] font-mono text-zinc-600">{s.asset}</span>
                          </div>
                          {s.followed_at && <p className="text-[10px] text-zinc-600">Following since {new Date(s.followed_at).toLocaleDateString()}</p>}
                        </div>
                      </div>
                      <div className="flex items-center gap-4 shrink-0 ml-4">
                        <div className="grid grid-cols-4 gap-4 text-center">
                          {[
                            { label: "Sharpe", value: s.metrics?.sharpe_ratio, color: "text-white" },
                            { label: "Return", value: `${s.metrics?.total_return}%`, color: (s.metrics?.total_return || 0) >= 0 ? "text-[#00FF94]" : "text-red-400" },
                            { label: "MaxDD", value: `${s.metrics?.max_drawdown}%`, color: "text-red-400" },
                            { label: "WinRate", value: `${s.metrics?.win_rate}%`, color: "text-zinc-300" },
                          ].map((m, j) => (
                            <div key={j}>
                              <p className="text-[9px] text-zinc-600 uppercase">{m.label}</p>
                              <p className={`text-xs font-mono font-bold ${m.color}`}>{m.value}</p>
                            </div>
                          ))}
                        </div>
                        <Button variant="outline" size="sm" onClick={() => unfollow(s.id)} className="rounded-full border-zinc-800 hover:border-red-500/50 hover:text-red-400 text-[10px] h-7 px-3" data-testid={`unfollow-${i}`}>
                          <UserMinus className="w-3 h-3 mr-1" /> Unfollow
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default FollowingPage;
