import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { ArrowUpRight, Star, Layers, CreditCard } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useAuth } from "../contexts/AuthContext";
import { UnsubscribeButton } from "../components/marketplace/SubscribeButtons";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MyStrategiesPage = () => {
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const navigate = useNavigate();

  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const res = await axios.get(`${API}/marketplace/me/strategies`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSubscriptions(res.data.subscriptions || []);
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    if (!token) { navigate("/login"); return; }
    fetchData();
  }, [token, fetchData, navigate]);

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="my-strategies-page">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold font-['Outfit'] text-white" data-testid="my-strategies-title">My Subscriptions</h1>
            <p className="text-sm text-zinc-500 mt-1">Strategies you are subscribed to</p>
          </div>
          <Link to="/marketplace">
            <Button variant="outline" className="border-zinc-700 text-zinc-300 text-sm"><Layers className="w-3.5 h-3.5 mr-1.5" /> Browse Marketplace</Button>
          </Link>
          <Link to="/billing">
            <Button variant="outline" className="border-zinc-700 text-zinc-300 text-sm" data-testid="manage-billing-btn"><CreditCard className="w-3.5 h-3.5 mr-1.5" /> Manage Billing</Button>
          </Link>
        </motion.div>

        {/* Content */}
        {loading ? (
          <div className="space-y-3">{[...Array(3)].map((_, i) => <div key={i} className="h-20 bg-zinc-900 rounded-lg animate-pulse" />)}</div>
        ) : subscriptions.length === 0 ? (
          <div className="text-center py-16">
            <p className="text-zinc-500 text-sm">No active subscriptions</p>
            <Link to="/marketplace" className="text-[#7B61FF] text-sm mt-2 inline-block">Browse marketplace</Link>
          </div>
        ) : (
          <div className="space-y-3">
            {subscriptions.map((sub, i) => (
              <motion.div key={sub.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
                <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-colors" data-testid={`subscribed-card-${i}`}>
                  <CardContent className="p-4 flex items-center justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <Link to={`/marketplace/${sub.strategy_id}`} className="text-sm font-semibold text-zinc-200 hover:text-white transition-colors flex items-center gap-1">
                        {sub.strategy_name} <ArrowUpRight className="w-3.5 h-3.5 text-zinc-600" />
                      </Link>
                      <div className="flex items-center gap-2 mt-1">
                        {sub.strategy?.category && <Badge className="bg-zinc-800 text-zinc-500 text-[10px]">{sub.strategy.category}</Badge>}
                        {sub.strategy?.avg_rating > 0 && (
                          <div className="flex items-center gap-0.5 text-amber-400">
                            <Star className="w-3 h-3 fill-current" /><span className="text-[10px] font-mono">{sub.strategy.avg_rating}</span>
                          </div>
                        )}
                        <span className="text-[10px] text-zinc-600">Since {new Date(sub.subscribed_at).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <UnsubscribeButton strategyId={sub.strategy_id} token={token} onDone={fetchData} size="sm" />
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

export default MyStrategiesPage;
