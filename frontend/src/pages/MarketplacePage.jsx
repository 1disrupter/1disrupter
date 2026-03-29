import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { Store, Star, Users, Search, ShoppingCart, X, TrendingUp, Shield, Zap, BarChart3 } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockMarketplaceItems } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";

const MOCK_DETAILS = {
  "BTC Momentum Pro": { description: "Advanced momentum-based strategy targeting BTC/USDT with dynamic position sizing and multi-timeframe confirmation.", returns: [12, 8, -3, 15, 7, 22, -5, 18, 11, 4, 9, 14], metrics: { sharpe: 1.85, maxDD: "6.2%", winRate: "67%", avgTrade: "+0.82%", trades: 342, runtime: "8 months" } },
  "ETH Swing Hunter": { description: "Swing trading strategy for ETH using RSI divergences and support/resistance breakouts with tight risk management.", returns: [5, 11, -2, 8, 14, -4, 19, 6, 3, 12, 7, 10], metrics: { sharpe: 1.62, maxDD: "5.8%", winRate: "63%", avgTrade: "+0.65%", trades: 198, runtime: "6 months" } },
  "DeFi Yield Optimizer": { description: "Automated yield farming optimizer across major DeFi protocols. Rebalances positions based on APY changes and gas costs.", returns: [3, 4, 2, 5, 3, 4, 6, 3, 5, 4, 3, 5], metrics: { sharpe: 2.41, maxDD: "2.1%", winRate: "89%", avgTrade: "+0.34%", trades: 520, runtime: "12 months" } },
};

const MarketplacePage = () => {
  const { isDemoMode, demoMarketplace } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const [searchQuery, setSearchQuery] = useState("");
  const [previewItem, setPreviewItem] = useState(null);

  const { data: apiData, loading, error, refetch } = useApiData("/marketplace/items", { skip: isDemoMode, token });
  const items = isDemoMode ? demoMarketplace : (apiData?.items || apiData || mockMarketplaceItems);
  const arr = Array.isArray(items) ? items : [];
  const filtered = searchQuery ? arr.filter(i => (i.name || "").toLowerCase().includes(searchQuery.toLowerCase())) : arr;

  const stats = [
    { label: "Available", value: String(arr.length), change: "Strategies & bots", positive: true },
    { label: "Top Rated", value: "4.8", change: "Avg rating", positive: true },
    { label: "Total Installs", value: "12.4K", change: "All time", positive: true },
    { label: "New This Week", value: "6", change: "Fresh strategies", positive: true },
  ];

  const openPreview = (item) => {
    const details = MOCK_DETAILS[item.name] || MOCK_DETAILS["BTC Momentum Pro"];
    setPreviewItem({ ...item, ...details });
  };

  const installItem = (item) => {
    toast.success(`${item.name} installed successfully!`);
    setPreviewItem(null);
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="marketplace-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader icon={Store} title="Marketplace" description="Discover and install community strategies, agents, and trading tools" testId="marketplace-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load marketplace" onRetry={refetch} /> : (
          <>
            <StatsRow stats={stats} />

            {/* Search */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
                <Input placeholder="Search strategies, agents, and tools..." value={searchQuery} onChange={e => setSearchQuery(e.target.value)} className="bg-[#0A0A0A] border-zinc-800 text-sm pl-10 h-11 rounded-xl" data-testid="marketplace-search" />
              </div>
            </motion.div>

            {/* Items Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {filtered.map((item, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 * i }}>
                  <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-all group">
                    <CardContent className="p-5">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <h3 className="text-sm font-semibold text-zinc-200 mb-1">{item.name}</h3>
                          <div className="flex items-center gap-2">
                            <Badge className="bg-zinc-800 text-zinc-400 text-[10px]">{item.category || item.type || "Strategy"}</Badge>
                            <div className="flex items-center gap-0.5 text-yellow-400">
                              <Star className="w-3 h-3 fill-current" />
                              <span className="text-[10px] font-mono">{item.rating || 4.5}</span>
                            </div>
                          </div>
                        </div>
                        <p className="text-sm font-bold text-[#7B61FF]">{item.price || "Free"}</p>
                      </div>
                      <p className="text-xs text-zinc-500 mb-4 line-clamp-2">{item.description || "High-performance trading strategy optimized for crypto markets"}</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-xs text-zinc-600">
                          <Users className="w-3 h-3" />
                          <span>{item.installs || item.users || "1.2K"} installs</span>
                        </div>
                        <Button onClick={() => openPreview(item)} size="sm" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white text-xs cursor-pointer" data-testid={`install-item-${i}`}><ShoppingCart className="w-3 h-3 mr-1" /> Preview</Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </>
        )}

        {/* Preview Modal */}
        <AnimatePresence>
          {previewItem && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setPreviewItem(null)}>
              <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} onClick={e => e.stopPropagation()} className="w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
                <Card className="bg-[#0A0A0A] border-zinc-800" data-testid="preview-modal">
                  <CardHeader className="border-b border-zinc-800/50 pb-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle className="text-base font-semibold text-zinc-100">{previewItem.name}</CardTitle>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge className="bg-zinc-800 text-zinc-400 text-[10px]">{previewItem.category || previewItem.type || "Strategy"}</Badge>
                          <div className="flex items-center gap-0.5 text-yellow-400"><Star className="w-3 h-3 fill-current" /><span className="text-[10px] font-mono">{previewItem.rating || 4.5}</span></div>
                          <span className="text-xs text-zinc-600">|</span>
                          <span className="text-xs text-zinc-500">{previewItem.installs || previewItem.users || "1.2K"} installs</span>
                        </div>
                      </div>
                      <button onClick={() => setPreviewItem(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                    </div>
                  </CardHeader>
                  <CardContent className="p-5 space-y-5">
                    <p className="text-sm text-zinc-400 leading-relaxed">{previewItem.description}</p>

                    {/* Performance Chart (simple bar chart) */}
                    <div>
                      <p className="text-xs text-zinc-500 mb-3 flex items-center gap-1"><BarChart3 className="w-3 h-3" /> Monthly Returns (%)</p>
                      <div className="flex items-end gap-1 h-24">
                        {(previewItem.returns || []).map((r, i) => (
                          <div key={i} className="flex-1 flex flex-col items-center gap-1">
                            <div className={`w-full rounded-t transition-all ${r >= 0 ? "bg-[#00FF94]/60" : "bg-red-400/60"}`} style={{ height: `${Math.abs(r) * 4}px`, minHeight: "2px" }} />
                            <span className="text-[8px] font-mono text-zinc-600">{r > 0 ? "+" : ""}{r}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Metrics Grid */}
                    {previewItem.metrics && (
                      <div className="grid grid-cols-3 gap-3">
                        {[
                          { icon: TrendingUp, label: "Sharpe", value: previewItem.metrics.sharpe },
                          { icon: Shield, label: "Max DD", value: previewItem.metrics.maxDD },
                          { icon: Zap, label: "Win Rate", value: previewItem.metrics.winRate },
                        ].map((m, i) => (
                          <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                            <m.icon className="w-3.5 h-3.5 text-[#7B61FF] mx-auto mb-1" />
                            <p className="text-[10px] text-zinc-600 mb-0.5">{m.label}</p>
                            <p className="text-sm font-bold font-mono text-white">{m.value}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="flex items-center justify-between pt-2 border-t border-zinc-800/50">
                      <div className="text-xs text-zinc-600">{previewItem.metrics?.trades} trades over {previewItem.metrics?.runtime}</div>
                      <div className="flex gap-2">
                        <Button variant="outline" onClick={() => setPreviewItem(null)} className="rounded-full border-zinc-800 text-xs">Cancel</Button>
                        <Button onClick={() => installItem(previewItem)} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white text-xs" data-testid="confirm-install-btn"><ShoppingCart className="w-3 h-3 mr-1" /> Install</Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default MarketplacePage;
