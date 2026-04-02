import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  CreditCard, ArrowUpRight, Receipt, DollarSign,
  Layers, CheckCircle, XCircle, Clock, AlertCircle, ExternalLink, Loader2
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { toast } from "sonner";
import { useAuth } from "../contexts/AuthContext";
import { UnsubscribeButton } from "../components/marketplace/SubscribeButtons";
import axios from "axios";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const statusConfig = {
  paid: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-400/10", label: "Paid" },
  complete: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-400/10", label: "Complete" },
  active: { icon: CheckCircle, color: "text-emerald-400", bg: "bg-emerald-400/10", label: "Active" },
  initiated: { icon: Clock, color: "text-amber-400", bg: "bg-amber-400/10", label: "Pending" },
  pending: { icon: Clock, color: "text-amber-400", bg: "bg-amber-400/10", label: "Pending" },
  canceled: { icon: XCircle, color: "text-zinc-500", bg: "bg-zinc-500/10", label: "Canceled" },
  expired: { icon: AlertCircle, color: "text-red-400", bg: "bg-red-400/10", label: "Expired" },
};

const StatusBadge = ({ status }) => {
  const cfg = statusConfig[status] || statusConfig.pending;
  const Icon = cfg.icon;
  return (
    <Badge className={`${cfg.bg} ${cfg.color} border-0 text-[11px] gap-1`} data-testid={`status-badge-${status}`}>
      <Icon className="w-3 h-3" /> {cfg.label}
    </Badge>
  );
};

const BillingPortalPage = () => {
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const navigate = useNavigate();

  const [overview, setOverview] = useState(null);
  const [subscriptions, setSubscriptions] = useState({ active: [], canceled: [] });
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [portalLoading, setPortalLoading] = useState(false);
  const [tab, setTab] = useState("subscriptions");

  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const fetchAll = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [ovRes, subRes, payRes] = await Promise.all([
        axios.get(`${API}/billing/overview`, { headers }),
        axios.get(`${API}/billing/subscriptions`, { headers }),
        axios.get(`${API}/billing/payments`, { headers }),
      ]);
      setOverview(ovRes.data);
      setSubscriptions({ active: subRes.data.active || [], canceled: subRes.data.canceled || [] });
      setPayments(payRes.data.payments || []);
    } catch (e) {
      console.error("Billing fetch error:", e);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    if (!token) { navigate("/login"); return; }
    fetchAll();
  }, [token, fetchAll, navigate]);

  const openStripePortal = async () => {
    setPortalLoading(true);
    try {
      const res = await axios.post(`${API}/billing/portal`, {
        return_url: window.location.href,
      }, { headers });
      if (res.data.url) {
        window.location.href = res.data.url;
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to open billing portal");
      setPortalLoading(false);
    }
  };

  const OverviewCards = () => {
    if (!overview) return null;
    const cards = [
      { label: "Active Subscriptions", value: overview.active_subscriptions, icon: Layers, accent: "text-[#7B61FF]", bg: "bg-[#7B61FF]/10" },
      { label: "Monthly Cost", value: `$${overview.monthly_cost.toFixed(2)}`, icon: DollarSign, accent: "text-emerald-400", bg: "bg-emerald-400/10" },
      { label: "Total Spent", value: `$${overview.total_spent.toFixed(2)}`, icon: CreditCard, accent: "text-amber-400", bg: "bg-amber-400/10" },
      { label: "Total Payments", value: overview.total_payments, icon: Receipt, accent: "text-sky-400", bg: "bg-sky-400/10" },
    ];
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6" data-testid="billing-overview-cards">
        {cards.map((c, i) => (
          <motion.div key={c.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50">
              <CardContent className="p-4">
                <div className={`w-8 h-8 rounded-lg ${c.bg} flex items-center justify-center mb-2`}>
                  <c.icon className={`w-4 h-4 ${c.accent}`} />
                </div>
                <p className="text-[11px] text-zinc-500 uppercase tracking-wider">{c.label}</p>
                <p className="text-lg font-bold text-zinc-100 font-mono mt-0.5" data-testid={`billing-${c.label.toLowerCase().replace(/\s/g, "-")}`}>{c.value}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    );
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="billing-portal-page">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-6 flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold font-['Outfit'] text-white" data-testid="billing-title">Billing & Subscriptions</h1>
            <p className="text-sm text-zinc-500 mt-1">Manage your subscriptions and payment history</p>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <Button
              onClick={openStripePortal}
              disabled={portalLoading}
              className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-sm"
              data-testid="manage-stripe-billing-btn"
            >
              {portalLoading ? <Loader2 className="w-4 h-4 animate-spin mr-1.5" /> : <ExternalLink className="w-3.5 h-3.5 mr-1.5" />}
              Manage Billing
            </Button>
            <Link to="/strategy-marketplace">
              <Button variant="outline" className="border-zinc-700 text-zinc-300 text-sm" data-testid="browse-marketplace-btn">
                <Layers className="w-3.5 h-3.5 mr-1.5" /> Browse Marketplace
              </Button>
            </Link>
          </div>
        </motion.div>

        {loading ? (
          <div className="space-y-3">
            {[...Array(4)].map((_, i) => <div key={i} className="h-20 bg-zinc-900 rounded-lg animate-pulse" />)}
          </div>
        ) : (
          <>
            <OverviewCards />

            {/* Tabs */}
            <div className="flex gap-1 mb-6 border-b border-zinc-800 pb-px" data-testid="billing-tabs">
              {[
                { key: "subscriptions", label: "Subscriptions", count: subscriptions.active.length },
                { key: "payments", label: "Payment History", count: payments.length },
              ].map((t) => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={`px-4 py-2 text-sm font-medium transition-colors relative ${
                    tab === t.key
                      ? "text-[#7B61FF]"
                      : "text-zinc-500 hover:text-zinc-300"
                  }`}
                  data-testid={`billing-tab-${t.key}`}
                >
                  {t.label}
                  {t.count > 0 && (
                    <span className="ml-1.5 text-[10px] bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded-full">{t.count}</span>
                  )}
                  {tab === t.key && (
                    <motion.div layoutId="billing-tab-indicator" className="absolute bottom-0 left-0 right-0 h-0.5 bg-[#7B61FF] rounded-full" />
                  )}
                </button>
              ))}
            </div>

            {/* Subscriptions Tab */}
            {tab === "subscriptions" && (
              <div className="space-y-6" data-testid="subscriptions-section">
                {/* Active */}
                {subscriptions.active.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-400 mb-3">Active Subscriptions</h3>
                    <div className="space-y-2">
                      {subscriptions.active.map((sub, i) => (
                        <motion.div key={sub.id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
                          <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-colors" data-testid={`active-sub-${i}`}>
                            <CardContent className="p-4 flex items-center justify-between gap-4">
                              <div className="flex-1 min-w-0">
                                <Link to={`/marketplace/${sub.strategy_id}`} className="text-sm font-semibold text-zinc-200 hover:text-white transition-colors flex items-center gap-1">
                                  {sub.strategy_name} <ArrowUpRight className="w-3.5 h-3.5 text-zinc-600" />
                                </Link>
                                <div className="flex items-center gap-2 mt-1.5 flex-wrap">
                                  <StatusBadge status="active" />
                                  <span className="text-[11px] text-zinc-600">$9.99/mo</span>
                                  <span className="text-[11px] text-zinc-600">Since {new Date(sub.subscribed_at).toLocaleDateString()}</span>
                                </div>
                              </div>
                              <UnsubscribeButton strategyId={sub.strategy_id} token={token} onDone={fetchAll} size="sm" />
                            </CardContent>
                          </Card>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Canceled */}
                {subscriptions.canceled.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-500 mb-3">Past Subscriptions</h3>
                    <div className="space-y-2">
                      {subscriptions.canceled.map((sub, i) => (
                        <Card key={sub.id} className="bg-[#0A0A0A]/60 border-zinc-800/30" data-testid={`canceled-sub-${i}`}>
                          <CardContent className="p-4 flex items-center justify-between gap-4">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm text-zinc-500">{sub.strategy_name}</p>
                              <div className="flex items-center gap-2 mt-1">
                                <StatusBadge status="canceled" />
                                {sub.canceled_at && (
                                  <span className="text-[11px] text-zinc-600">Canceled {new Date(sub.canceled_at).toLocaleDateString()}</span>
                                )}
                              </div>
                            </div>
                            <Link to={`/marketplace/${sub.strategy_id}`}>
                              <Button variant="outline" size="sm" className="border-zinc-800 text-zinc-500 text-xs" data-testid="resubscribe-btn">
                                Resubscribe
                              </Button>
                            </Link>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                )}

                {subscriptions.active.length === 0 && subscriptions.canceled.length === 0 && (
                  <div className="text-center py-16" data-testid="no-subscriptions">
                    <Layers className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
                    <p className="text-zinc-500 text-sm">No subscriptions yet</p>
                    <Link to="/strategy-marketplace" className="text-[#7B61FF] text-sm mt-2 inline-block hover:underline">
                      Browse strategies to subscribe
                    </Link>
                  </div>
                )}
              </div>
            )}

            {/* Payments Tab */}
            {tab === "payments" && (
              <div data-testid="payments-section">
                {payments.length === 0 ? (
                  <div className="text-center py-16" data-testid="no-payments">
                    <Receipt className="w-10 h-10 text-zinc-700 mx-auto mb-3" />
                    <p className="text-zinc-500 text-sm">No payment history</p>
                  </div>
                ) : (
                  <Card className="bg-[#0A0A0A] border-zinc-800/50">
                    <CardContent className="p-0">
                      <div className="overflow-x-auto">
                        <table className="w-full text-sm" data-testid="payments-table">
                          <thead>
                            <tr className="border-b border-zinc-800/50">
                              <th className="text-left p-3 text-[11px] uppercase tracking-wider text-zinc-500 font-medium">Date</th>
                              <th className="text-left p-3 text-[11px] uppercase tracking-wider text-zinc-500 font-medium">Strategy</th>
                              <th className="text-left p-3 text-[11px] uppercase tracking-wider text-zinc-500 font-medium">Amount</th>
                              <th className="text-left p-3 text-[11px] uppercase tracking-wider text-zinc-500 font-medium">Status</th>
                            </tr>
                          </thead>
                          <tbody>
                            {payments.map((p, i) => (
                              <tr key={p.id || i} className="border-b border-zinc-800/30 last:border-0 hover:bg-zinc-900/50 transition-colors" data-testid={`payment-row-${i}`}>
                                <td className="p-3 text-zinc-400 font-mono text-xs">
                                  {new Date(p.created_at).toLocaleDateString()}
                                </td>
                                <td className="p-3 text-zinc-300 text-xs">{p.strategy_name}</td>
                                <td className="p-3 text-zinc-200 font-mono text-xs">
                                  ${p.amount?.toFixed(2)} <span className="text-zinc-600 uppercase">{p.currency}</span>
                                </td>
                                <td className="p-3">
                                  <StatusBadge status={p.payment_status} />
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default BillingPortalPage;
