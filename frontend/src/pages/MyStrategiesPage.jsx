import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import {
  Plus, ArrowUpRight, Star, Users, Eye, EyeOff, Loader2, Layers
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { useAuth } from "../contexts/AuthContext";

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const MyStrategiesPage = () => {
  const { user, tokens } = useAuth();
  const token = tokens?.access_token;
  const navigate = useNavigate();

  const [tab, setTab] = useState("subscribed");
  const [subscribed, setSubscribed] = useState([]);
  const [created, setCreated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  // Create form
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newCategory, setNewCategory] = useState("other");
  const [creating, setCreating] = useState(false);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchData = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const [subsRes, createdRes] = await Promise.all([
        axios.get(`${API}/marketplace/me/strategies`, { headers }),
        axios.get(`${API}/marketplace/me/created`, { headers }),
      ]);
      setSubscribed(subsRes.data.subscriptions || []);
      setCreated(createdRes.data.strategies || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    if (!token) { navigate("/login"); return; }
    fetchData();
  }, [token, fetchData, navigate]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newName.trim()) { toast.error("Name is required"); return; }
    setCreating(true);
    try {
      const res = await axios.post(`${API}/marketplace/strategies/create`,
        { name: newName.trim(), description: newDesc.trim(), category: newCategory },
        { headers: { ...headers, "Content-Type": "application/json" } }
      );
      toast.success("Strategy created!");
      setShowCreate(false);
      setNewName("");
      setNewDesc("");
      setNewCategory("other");
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to create");
    }
    setCreating(false);
  };

  const handlePublish = async (id) => {
    setActionLoading(id);
    try {
      await axios.post(`${API}/marketplace/strategies/${id}/publish`, {}, { headers });
      toast.success("Published!");
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to publish");
    }
    setActionLoading(null);
  };

  const handleUnpublish = async (id) => {
    setActionLoading(id);
    try {
      await axios.post(`${API}/marketplace/strategies/${id}/unpublish`, {}, { headers });
      toast.success("Unpublished");
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to unpublish");
    }
    setActionLoading(null);
  };

  const handleUnsubscribe = async (strategyId) => {
    setActionLoading(strategyId);
    try {
      await axios.post(`${API}/marketplace/strategies/${strategyId}/unsubscribe`, {}, { headers });
      toast.success("Unsubscribed");
      fetchData();
    } catch (err) {
      toast.error(err.response?.data?.detail || "Failed to unsubscribe");
    }
    setActionLoading(null);
  };

  const STATUS_STYLES = {
    draft: "bg-zinc-800 text-zinc-400",
    published: "bg-[#00FF94]/15 text-[#00FF94]",
    disabled: "bg-red-500/15 text-red-400",
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="my-strategies-page">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8 flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold font-['Outfit'] text-white" data-testid="my-strategies-title">My Strategies</h1>
            <p className="text-sm text-zinc-500 mt-1">Manage your subscriptions and created strategies</p>
          </div>
          <div className="flex gap-3">
            <Link to="/strategy-marketplace">
              <Button variant="outline" className="border-zinc-700 text-zinc-300 text-sm" data-testid="browse-marketplace-link">
                <Layers className="w-3.5 h-3.5 mr-1.5" /> Browse Marketplace
              </Button>
            </Link>
            <Button onClick={() => { setShowCreate(!showCreate); setTab("created"); }} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-sm" data-testid="create-strategy-btn">
              <Plus className="w-3.5 h-3.5 mr-1.5" /> Create
            </Button>
          </div>
        </motion.div>

        {/* Tabs */}
        <div className="flex gap-1 mb-6 bg-zinc-900/50 rounded-lg p-1 w-fit">
          {[
            { key: "subscribed", label: "Subscribed", count: subscribed.length },
            { key: "created", label: "Created", count: created.length },
          ].map(t => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 rounded-md text-sm transition-colors ${tab === t.key ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
              data-testid={`tab-${t.key}`}
            >
              {t.label} <span className="text-zinc-600 ml-1 font-mono text-xs">{t.count}</span>
            </button>
          ))}
        </div>

        {/* Create Form */}
        {showCreate && tab === "created" && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} className="mb-6">
            <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="create-form">
              <CardContent className="p-5">
                <form onSubmit={handleCreate} className="space-y-4">
                  <div>
                    <label className="text-xs text-zinc-500 uppercase tracking-wider mb-1.5 block">Strategy Name</label>
                    <Input value={newName} onChange={e => setNewName(e.target.value)} placeholder="e.g., BTC Breakout Scanner" className="bg-[#050505] border-zinc-800 text-sm" data-testid="create-name-input" />
                  </div>
                  <div>
                    <label className="text-xs text-zinc-500 uppercase tracking-wider mb-1.5 block">Description</label>
                    <textarea value={newDesc} onChange={e => setNewDesc(e.target.value)} placeholder="Describe your strategy..." rows={3} className="w-full px-3 py-2 bg-[#050505] border border-zinc-800 rounded-md text-sm text-zinc-300 placeholder-zinc-600 outline-none focus:border-[#7B61FF]/50 resize-none" data-testid="create-desc-input" />
                  </div>
                  <div>
                    <label className="text-xs text-zinc-500 uppercase tracking-wider mb-1.5 block">Category</label>
                    <select value={newCategory} onChange={e => setNewCategory(e.target.value)} className="h-10 px-3 bg-[#050505] border border-zinc-800 rounded-md text-sm text-zinc-300 w-full" data-testid="create-category-select">
                      {["btc","eth","sol","xrp","trend","scalping","momentum","mean_reversion","arbitrage","other"].map(c => (
                        <option key={c} value={c}>{c}</option>
                      ))}
                    </select>
                  </div>
                  <div className="flex gap-2 pt-1">
                    <Button type="submit" disabled={creating} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-sm" data-testid="create-submit-btn">
                      {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Draft"}
                    </Button>
                    <Button type="button" variant="outline" onClick={() => setShowCreate(false)} className="border-zinc-700 text-zinc-400 text-sm">Cancel</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Content */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => <div key={i} className="h-20 bg-zinc-900 rounded-lg animate-pulse" />)}
          </div>
        ) : (
          <>
            {/* Subscribed Tab */}
            {tab === "subscribed" && (
              subscribed.length === 0 ? (
                <div className="text-center py-16">
                  <p className="text-zinc-500 text-sm">No subscriptions yet</p>
                  <Link to="/strategy-marketplace" className="text-[#7B61FF] text-sm mt-2 inline-block">Browse marketplace</Link>
                </div>
              ) : (
                <div className="space-y-3">
                  {subscribed.map((sub, i) => (
                    <motion.div key={sub.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
                      <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-colors" data-testid={`subscribed-card-${i}`}>
                        <CardContent className="p-4 flex items-center justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <Link to={`/strategy-marketplace/${sub.strategy_id}`} className="text-sm font-semibold text-zinc-200 hover:text-white transition-colors flex items-center gap-1">
                              {sub.strategy_name} <ArrowUpRight className="w-3.5 h-3.5 text-zinc-600" />
                            </Link>
                            <div className="flex items-center gap-2 mt-1">
                              {sub.strategy?.category && <Badge className="bg-zinc-800 text-zinc-500 text-[10px]">{sub.strategy.category}</Badge>}
                              {sub.strategy?.avg_rating > 0 && (
                                <div className="flex items-center gap-0.5 text-amber-400">
                                  <Star className="w-3 h-3 fill-current" />
                                  <span className="text-[10px] font-mono">{sub.strategy.avg_rating}</span>
                                </div>
                              )}
                              <span className="text-[10px] text-zinc-600">Subscribed {new Date(sub.subscribed_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <Button onClick={() => handleUnsubscribe(sub.strategy_id)} disabled={actionLoading === sub.strategy_id} variant="outline" size="sm" className="border-zinc-700 text-zinc-400 text-xs shrink-0" data-testid={`unsub-btn-${i}`}>
                            {actionLoading === sub.strategy_id ? <Loader2 className="w-3 h-3 animate-spin" /> : "Unsubscribe"}
                          </Button>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              )
            )}

            {/* Created Tab */}
            {tab === "created" && (
              created.length === 0 && !showCreate ? (
                <div className="text-center py-16">
                  <p className="text-zinc-500 text-sm">You haven&apos;t created any strategies yet</p>
                  <Button onClick={() => setShowCreate(true)} className="mt-3 bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-sm">
                    <Plus className="w-3.5 h-3.5 mr-1" /> Create your first
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {created.map((s, i) => (
                    <motion.div key={s.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.03 * i }}>
                      <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid={`created-card-${i}`}>
                        <CardContent className="p-4 flex items-center justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <Link to={`/strategy-marketplace/${s.id}`} className="text-sm font-semibold text-zinc-200 hover:text-white transition-colors flex items-center gap-1">
                              {s.name} <ArrowUpRight className="w-3.5 h-3.5 text-zinc-600" />
                            </Link>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge className={`text-[10px] ${STATUS_STYLES[s.status] || STATUS_STYLES.draft}`}>{s.status}</Badge>
                              <Badge className="bg-zinc-800 text-zinc-500 text-[10px]">{s.category}</Badge>
                              <div className="flex items-center gap-1 text-zinc-600 text-[10px]">
                                <Users className="w-3 h-3" /> {s.subscriber_count}
                              </div>
                              {s.avg_rating > 0 && (
                                <div className="flex items-center gap-0.5 text-amber-400">
                                  <Star className="w-3 h-3 fill-current" />
                                  <span className="text-[10px] font-mono">{s.avg_rating}</span>
                                </div>
                              )}
                            </div>
                          </div>
                          <div className="shrink-0">
                            {s.status === "draft" ? (
                              <Button onClick={() => handlePublish(s.id)} disabled={actionLoading === s.id} size="sm" className="bg-[#00FF94]/15 text-[#00FF94] hover:bg-[#00FF94]/25 text-xs" data-testid={`publish-btn-${i}`}>
                                {actionLoading === s.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><Eye className="w-3 h-3 mr-1" /> Publish</>}
                              </Button>
                            ) : s.status === "published" ? (
                              <Button onClick={() => handleUnpublish(s.id)} disabled={actionLoading === s.id} variant="outline" size="sm" className="border-zinc-700 text-zinc-400 text-xs" data-testid={`unpublish-btn-${i}`}>
                                {actionLoading === s.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <><EyeOff className="w-3 h-3 mr-1" /> Unpublish</>}
                              </Button>
                            ) : null}
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  ))}
                </div>
              )
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default MyStrategiesPage;
