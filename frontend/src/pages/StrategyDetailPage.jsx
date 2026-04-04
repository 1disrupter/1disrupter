import { useState, useEffect, useCallback } from "react";
import { useParams, Link, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { ArrowLeft, Star, Users, Clock, Loader2, Copy } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { useAuth } from "../contexts/AuthContext";
import axios from "axios";
import StrategyPerformanceBlock from "../components/marketplace/StrategyPerformanceBlock";
import EquityCurveChart from "../components/marketplace/EquityCurveChart";
import SignalsTable from "../components/marketplace/SignalsTable";
import ReviewsList from "../components/marketplace/ReviewsList";
import { SubscribeButton, UnsubscribeButton } from "../components/marketplace/SubscribeButtons";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const StrategyDetailPage = () => {
  const { id } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const { user, tokens } = useAuth();
  const token = tokens?.access_token;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isSubscribed, setIsSubscribed] = useState(false);
  const [polling, setPolling] = useState(false);

  const fetchDetail = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/marketplace/strategies/${id}`);
      if (res.ok) setData(await res.json());
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [id]);

  // Check subscription status
  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await axios.get(`${API}/marketplace/me/strategies`, { headers: { Authorization: `Bearer ${token}` } });
        setIsSubscribed((res.data.subscriptions || []).some(s => s.strategy_id === id));
      } catch { /* ignore */ }
    })();
  }, [token, id]);

  useEffect(() => { fetchDetail(); }, [fetchDetail]);

  // Poll for Stripe checkout status on return from payment
  useEffect(() => {
    const sessionId = searchParams.get("session_id");
    const success = searchParams.get("success");
    if (!sessionId || !token || !success) return;

    let attempts = 0;
    const maxAttempts = 5;
    setPolling(true);

    const poll = async () => {
      try {
        const res = await axios.get(`${API}/marketplace/checkout/status/${sessionId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.data.payment_status === "paid") {
          toast.success("Payment successful! You are now subscribed.");
          setIsSubscribed(true);
          setPolling(false);
          setSearchParams({});
          fetchDetail();
          return;
        }
        if (res.data.status === "expired") {
          toast.error("Payment session expired. Please try again.");
          setPolling(false);
          setSearchParams({});
          return;
        }
      } catch { /* ignore */ }

      attempts++;
      if (attempts < maxAttempts) {
        setTimeout(poll, 2000);
      } else {
        toast.info("Payment is being processed. Please refresh in a moment.");
        setPolling(false);
        setSearchParams({});
      }
    };
    poll();
  }, [searchParams, token, fetchDetail, setSearchParams]);

  // Handle cancel return
  useEffect(() => {
    if (searchParams.get("canceled")) {
      toast.info("Checkout canceled.");
      setSearchParams({});
    }
  }, [searchParams, setSearchParams]);

  const refresh = () => { fetchDetail(); };
  const onSubscribeChange = () => { setIsSubscribed(!isSubscribed); refresh(); };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {[...Array(4)].map((_, i) => <div key={i} className="h-24 bg-zinc-900 rounded-lg animate-pulse" />)}
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen pt-24 pb-12 px-4 text-center">
        <p className="text-zinc-500">Strategy not found</p>
        <Link to="/marketplace" className="text-[#7B61FF] text-sm mt-2 inline-block">Back to Marketplace</Link>
      </div>
    );
  }

  const { strategy: s, performance: perf, signals, reviews } = data;
  const isOwner = user?.id === s.creator_id;

  // Build equity curve from performance extra field (if available)
  const equityCurve = perf?.extra?.equity_curve || [];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="strategy-detail-page">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Payment processing banner */}
        {polling && (
          <div className="flex items-center gap-3 p-4 rounded-lg bg-[#7B61FF]/10 border border-[#7B61FF]/20" data-testid="payment-processing">
            <Loader2 className="w-4 h-4 text-[#7B61FF] animate-spin" />
            <span className="text-sm text-zinc-300">Processing payment...</span>
          </div>
        )}

        {/* Back */}
        <Link to="/marketplace" className="inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-300 transition-colors" data-testid="back-to-marketplace">
          <ArrowLeft className="w-4 h-4" /> Marketplace
        </Link>

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
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
            <div className="flex items-center gap-2">
              {s.risk_label && (
                <Badge className={`text-xs ${
                  s.risk_label === 'High' ? 'bg-red-500/15 text-red-400' :
                  s.risk_label === 'Medium-High' ? 'bg-orange-500/15 text-orange-400' :
                  s.risk_label === 'Medium' ? 'bg-amber-500/15 text-amber-400' :
                  'bg-green-500/15 text-green-400'
                }`} data-testid="strategy-risk-label">{s.risk_label} Risk</Badge>
              )}
              {isOwner && <Badge className="bg-[#00FF94]/15 text-[#00FF94] text-xs">Your Strategy</Badge>}
              {!isOwner && token && (
                <Button
                  size="sm"
                  variant="outline"
                  className="h-8 rounded-full border-zinc-700 hover:border-[#7B61FF] text-xs"
                  data-testid="copy-strategy-btn"
                  onClick={async () => {
                    try {
                      await axios.post(`${API}/marketplace/strategies/${id}/copy`, {}, { headers: { Authorization: `Bearer ${token}` } });
                      toast.success("Strategy copied to your collection!");
                    } catch (e) {
                      toast.error(e.response?.data?.detail || "Failed to copy strategy");
                    }
                  }}
                >
                  <Copy className="w-3.5 h-3.5 mr-1" />Copy Strategy
                </Button>
              )}
              {!isOwner && (
                isSubscribed
                  ? <UnsubscribeButton strategyId={id} token={token} onDone={onSubscribeChange} />
                  : <SubscribeButton strategyId={id} token={token} onDone={onSubscribeChange} />
              )}
            </div>
          </div>
          <p className="text-sm text-zinc-400 mt-4 leading-relaxed">{s.description}</p>
        </motion.div>

        {/* Performance */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <StrategyPerformanceBlock performance={perf} />
        </motion.div>

        {/* Equity Curve */}
        {equityCurve.length >= 2 && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <EquityCurveChart equityCurve={equityCurve} />
          </motion.div>
        )}

        {/* Signals Table */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <SignalsTable signals={signals} />
        </motion.div>

        {/* Reviews */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <ReviewsList reviews={reviews} strategyId={id} token={token} isOwner={isOwner} onReviewAdded={refresh} />
        </motion.div>

        {/* Parameters */}
        {s.parameters && Object.keys(s.parameters).length > 0 && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
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
