import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import {
  ArrowLeft, Star, Users, TrendingUp, Shield, Zap, BarChart3,
  Clock, ChevronDown, ChevronUp, Send, Loader2
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useAuth } from "../contexts/AuthContext";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const StrategyDetailPage = () => {
  const { id } = useParams();
  const { user, tokens } = useAuth();
  const token = tokens?.access_token;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subscribing, setSubscribing] = useState(false);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [reviewText, setReviewText] = useState("");
  const [reviewRating, setReviewRating] = useState(5);
  const [submittingReview, setSubmittingReview] = useState(false);
  const [showAllReviews, setShowAllReviews] = useState(false);

  const fetchDetail = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/marketplace/strategies/${id}`);
      if (res.ok) {
        const d = await res.json();
        setData(d);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [id]);

  // Check subscription status
  useEffect(() => {
    if (!token) return;
    const checkSub = async () => {
      try {
        const res = await axios.get(`${API}/marketplace/me/strategies`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const subs = res.data.subscriptions || [];
        setIsSubscribed(subs.some(s => s.strategy_id === id));
      } catch { /* ignore */ }
    };
    checkSub();
  }, [token, id]);

  useEffect(() => { fetchDetail(); }, [fetchDetail]);

  const handleSubscribe = async () => {
    if (!token) { toast.error("Please sign in to subscribe"); return; }
    setSubscribing(true);
    try {
      await axios.post(`${API}/marketplace/strategies/${id}/subscribe`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsSubscribed(true);
      toast.success("Subscribed successfully!");
      fetchDetail();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to subscribe");
    }
    setSubscribing(false);
  };

  const handleUnsubscribe = async () => {
    setSubscribing(true);
    try {
      await axios.post(`${API}/marketplace/strategies/${id}/unsubscribe`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIsSubscribed(false);
      toast.success("Unsubscribed");
      fetchDetail();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to unsubscribe");
    }
    setSubscribing(false);
  };

  const handleReview = async (e) => {
    e.preventDefault();
    if (!token) { toast.error("Please sign in to review"); return; }
    setSubmittingReview(true);
    try {
      await axios.post(`${API}/marketplace/strategies/${id}/review`,
        { rating: reviewRating, comment: reviewText.trim() },
        { headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` } }
      );
      toast.success("Review submitted!");
      setReviewText("");
      setReviewRating(5);
      fetchDetail();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to submit review");
    }
    setSubmittingReview(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 bg-zinc-900 rounded-lg animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4 text-center">
        <p className="text-zinc-500">Strategy not found</p>
        <Link to="/strategy-marketplace" className="text-[#7B61FF] text-sm mt-2 inline-block">Back to Marketplace</Link>
      </div>
    );
  }

  const { strategy: s, performance: perf, signals, reviews } = data;
  const isOwner = user?.id === s.creator_id;
  const displayedReviews = showAllReviews ? reviews : reviews.slice(0, 3);

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="strategy-detail-page">
      <div className="max-w-4xl mx-auto">
        {/* Back link */}
        <Link to="/strategy-marketplace" className="inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-300 transition-colors mb-6" data-testid="back-to-marketplace">
          <ArrowLeft className="w-4 h-4" /> Marketplace
        </Link>

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-2xl font-bold font-['Outfit'] text-white" data-testid="strategy-name">{s.name}</h1>
              <div className="flex items-center gap-3 mt-2 flex-wrap">
                <Badge className="bg-zinc-800 text-zinc-400 text-xs">{s.category}</Badge>
                <span className="text-xs text-zinc-600">by {s.creator_name}</span>
                {s.avg_rating > 0 && (
                  <div className="flex items-center gap-1 text-amber-400">
                    <Star className="w-3.5 h-3.5 fill-current" />
                    <span className="text-xs font-mono">{s.avg_rating}</span>
                    <span className="text-zinc-600 text-xs">({s.review_count})</span>
                  </div>
                )}
                <div className="flex items-center gap-1 text-zinc-500 text-xs">
                  <Users className="w-3.5 h-3.5" /> {s.subscriber_count} subscribers
                </div>
              </div>
            </div>
            {!isOwner && (
              isSubscribed ? (
                <Button onClick={handleUnsubscribe} disabled={subscribing} variant="outline" className="border-zinc-700 text-zinc-300" data-testid="unsubscribe-btn">
                  {subscribing ? <Loader2 className="w-4 h-4 animate-spin" /> : "Unsubscribe"}
                </Button>
              ) : (
                <Button onClick={handleSubscribe} disabled={subscribing} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="subscribe-btn">
                  {subscribing ? <Loader2 className="w-4 h-4 animate-spin" /> : "Subscribe"}
                </Button>
              )
            )}
            {isOwner && <Badge className="bg-[#00FF94]/15 text-[#00FF94] text-xs">Your Strategy</Badge>}
          </div>
          <p className="text-sm text-zinc-400 mt-4 leading-relaxed">{s.description}</p>
        </motion.div>

        {/* Performance */}
        {perf && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50 mb-6" data-testid="performance-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                  <BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
                  {[
                    { label: "Sharpe Ratio", value: perf.sharpe_ratio?.toFixed(2) ?? "—", icon: TrendingUp, color: "text-[#00FF94]" },
                    { label: "Win Rate", value: perf.win_rate != null ? `${perf.win_rate}%` : "—", icon: Zap, color: "text-[#00FF94]" },
                    { label: "Max Drawdown", value: perf.max_drawdown != null ? `${perf.max_drawdown}%` : "—", icon: Shield, color: "text-white" },
                    { label: "Total Return", value: perf.total_return != null ? `${perf.total_return}%` : "—", icon: TrendingUp, color: perf.total_return >= 0 ? "text-[#00FF94]" : "text-red-400" },
                    { label: "Total Trades", value: perf.total_trades ?? "—", icon: BarChart3, color: "text-white" },
                  ].map((m, i) => (
                    <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                      <m.icon className="w-4 h-4 text-[#7B61FF] mx-auto mb-1.5" />
                      <p className="text-[10px] text-zinc-600 mb-0.5">{m.label}</p>
                      <p className={`text-base font-bold font-mono ${m.color}`}>{m.value}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Signals */}
        {signals.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50 mb-6" data-testid="signals-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-[#7B61FF]" /> Recent Signals ({signals.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {signals.slice(0, 5).map((sig, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800/20 text-xs">
                      <span className="text-zinc-300 font-mono">{sig.symbol || sig.pair || "—"}</span>
                      <Badge className={`text-[10px] ${sig.action === 'BUY' ? 'bg-[#00FF94]/15 text-[#00FF94]' : 'bg-red-400/15 text-red-400'}`}>
                        {sig.action || sig.side || "SIGNAL"}
                      </Badge>
                      <span className="text-zinc-600">{sig.created_at ? new Date(sig.created_at).toLocaleDateString() : "—"}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Reviews */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50 mb-6" data-testid="reviews-card">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                <Star className="w-4 h-4 text-[#7B61FF]" /> Reviews ({reviews.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {reviews.length === 0 ? (
                <p className="text-zinc-600 text-xs py-4 text-center">No reviews yet. Be the first!</p>
              ) : (
                <div className="space-y-3">
                  {displayedReviews.map((r, i) => (
                    <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/20">
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-zinc-300 font-medium">{r.user_name}</span>
                          <div className="flex items-center gap-0.5">
                            {[...Array(5)].map((_, j) => (
                              <Star key={j} className={`w-3 h-3 ${j < r.rating ? 'text-amber-400 fill-current' : 'text-zinc-700'}`} />
                            ))}
                          </div>
                        </div>
                        <span className="text-[10px] text-zinc-600">{r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}</span>
                      </div>
                      {r.comment && <p className="text-xs text-zinc-500 mt-1">{r.comment}</p>}
                    </div>
                  ))}
                  {reviews.length > 3 && (
                    <button onClick={() => setShowAllReviews(!showAllReviews)} className="text-xs text-[#7B61FF] flex items-center gap-1 mx-auto mt-2">
                      {showAllReviews ? <><ChevronUp className="w-3 h-3" /> Show less</> : <><ChevronDown className="w-3 h-3" /> Show all {reviews.length} reviews</>}
                    </button>
                  )}
                </div>
              )}

              {/* Add review form */}
              {token && !isOwner && (
                <form onSubmit={handleReview} className="mt-4 pt-4 border-t border-zinc-800/50" data-testid="review-form">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-xs text-zinc-500">Your rating:</span>
                    <div className="flex gap-0.5">
                      {[1, 2, 3, 4, 5].map(v => (
                        <button key={v} type="button" onClick={() => setReviewRating(v)} data-testid={`rating-star-${v}`}>
                          <Star className={`w-4 h-4 cursor-pointer transition-colors ${v <= reviewRating ? 'text-amber-400 fill-current' : 'text-zinc-700 hover:text-zinc-500'}`} />
                        </button>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <input
                      value={reviewText}
                      onChange={e => setReviewText(e.target.value)}
                      placeholder="Write a review..."
                      className="flex-1 h-9 px-3 bg-[#050505] border border-zinc-800 rounded text-sm text-zinc-300 placeholder-zinc-600 outline-none focus:border-[#7B61FF]/50"
                      data-testid="review-input"
                    />
                    <Button type="submit" disabled={submittingReview} size="sm" className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 h-9" data-testid="submit-review-btn">
                      {submittingReview ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
                    </Button>
                  </div>
                </form>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Strategy Parameters */}
        {s.parameters && Object.keys(s.parameters).length > 0 && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="parameters-card">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                  <Clock className="w-4 h-4 text-[#7B61FF]" /> Parameters
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {Object.entries(s.parameters).map(([k, v]) => (
                    <div key={k} className="p-2.5 rounded-lg bg-[#050505] border border-zinc-800/20">
                      <p className="text-[10px] text-zinc-600 uppercase tracking-wider">{k}</p>
                      <p className="text-sm font-mono text-zinc-300">{String(v)}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default StrategyDetailPage;
