import { useState, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Search, Filter, TrendingUp, ChevronDown } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Card, CardContent } from "../components/ui/card";
import { useAuth } from "../contexts/AuthContext";
import { Link } from "react-router-dom";
import { Button } from "../components/ui/button";
import StrategyCard from "../components/marketplace/StrategyCard";

const API = process.env.REACT_APP_BACKEND_URL;

const CATEGORIES = [
  { value: "", label: "All Categories" },
  { value: "btc", label: "BTC" },
  { value: "eth", label: "ETH" },
  { value: "sol", label: "SOL" },
  { value: "xrp", label: "XRP" },
  { value: "trend", label: "Trend" },
  { value: "scalping", label: "Scalping" },
  { value: "momentum", label: "Momentum" },
  { value: "mean_reversion", label: "Mean Reversion" },
  { value: "arbitrage", label: "Arbitrage" },
];

const SORT_OPTIONS = [
  { value: "popularity", label: "Most Popular" },
  { value: "newest", label: "Newest" },
  { value: "rating", label: "Top Rated" },
  { value: "performance", label: "Best Performance" },
];

const StrategyMarketplacePage = () => {
  const { tokens } = useAuth();
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(0);
  const [category, setCategory] = useState("");
  const [sortBy, setSortBy] = useState("popularity");
  const [search, setSearch] = useState("");

  const fetchStrategies = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ sort_by: sortBy, page: String(page), limit: "12" });
      if (category) params.set("category", category);
      const res = await fetch(`${API}/api/marketplace/strategies?${params}`);
      if (!res.ok) throw new Error();
      const data = await res.json();

      // Enrich cards with performance peek
      const enriched = await Promise.all((data.strategies || []).map(async (s) => {
        try {
          const r = await fetch(`${API}/api/marketplace/strategies/${s.id}`);
          if (r.ok) {
            const d = await r.json();
            return { ...s, _perf: d.performance };
          }
        } catch { /* ignore */ }
        return { ...s, _perf: null };
      }));

      setStrategies(enriched);
      setTotal(data.total || 0);
      setPages(data.pages || 0);
    } catch {
      setStrategies([]);
    }
    setLoading(false);
  }, [category, sortBy, page]);

  useEffect(() => { fetchStrategies(); }, [fetchStrategies]);

  const filtered = search
    ? strategies.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || (s.description || "").toLowerCase().includes(search.toLowerCase()))
    : strategies;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="strategy-marketplace-page">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <h1 className="text-3xl font-bold font-['Outfit'] text-white" data-testid="marketplace-title">Strategy Marketplace</h1>
              <p className="text-sm text-zinc-500 mt-1">Browse, subscribe, and review community strategies</p>
            </div>
            <div className="flex items-center gap-3">
              {tokens && (
                <>
                  <Link to="/me/strategies">
                    <Button variant="outline" className="border-zinc-700 text-zinc-300 text-sm" data-testid="my-subscriptions-link">My Subscriptions</Button>
                  </Link>
                  <Link to="/creator/strategies">
                    <Button variant="outline" className="border-zinc-700 text-zinc-300 text-sm" data-testid="creator-dashboard-link">Creator Dashboard</Button>
                  </Link>
                </>
              )}
              <Badge className="bg-[#7B61FF]/15 text-[#7B61FF] border border-[#7B61FF]/20 text-xs font-mono">{total} published</Badge>
            </div>
          </div>
        </motion.div>

        {/* Filters */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="flex flex-col sm:flex-row gap-3 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
            <Input placeholder="Search strategies..." value={search} onChange={e => setSearch(e.target.value)} className="bg-[#0A0A0A] border-zinc-800 text-sm pl-10 h-10" data-testid="marketplace-search-input" />
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 pointer-events-none" />
              <select value={category} onChange={e => { setCategory(e.target.value); setPage(1); }} className="h-10 pl-9 pr-8 bg-[#0A0A0A] border border-zinc-800 rounded-md text-sm text-zinc-300 appearance-none cursor-pointer" data-testid="category-filter">
                {CATEGORIES.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 pointer-events-none" />
            </div>
            <div className="relative">
              <TrendingUp className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 pointer-events-none" />
              <select value={sortBy} onChange={e => { setSortBy(e.target.value); setPage(1); }} className="h-10 pl-9 pr-8 bg-[#0A0A0A] border border-zinc-800 rounded-md text-sm text-zinc-300 appearance-none cursor-pointer" data-testid="sort-filter">
                {SORT_OPTIONS.map(s => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
              <ChevronDown className="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-zinc-600 pointer-events-none" />
            </div>
          </div>
        </motion.div>

        {/* Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {[...Array(6)].map((_, i) => (
              <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50 animate-pulse">
                <CardContent className="p-5 space-y-3">
                  <div className="h-5 bg-zinc-800 rounded w-3/4" />
                  <div className="h-3 bg-zinc-800/50 rounded w-full" />
                  <div className="h-3 bg-zinc-800/50 rounded w-2/3" />
                  <div className="flex gap-2 pt-2"><div className="h-6 bg-zinc-800 rounded w-16" /><div className="h-6 bg-zinc-800 rounded w-16" /></div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-20">
            <p className="text-zinc-500 text-sm">No strategies found.</p>
            <p className="text-zinc-600 text-xs mt-1">Try adjusting your filters or check back later.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filtered.map((s, i) => (
              <motion.div key={s.id} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.04 * i }}>
                <StrategyCard strategy={s} index={i} />
              </motion.div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {pages > 1 && (
          <div className="flex justify-center gap-2 mt-8">
            {Array.from({ length: pages }, (_, i) => i + 1).map(p => (
              <button key={p} onClick={() => setPage(p)} className={`w-8 h-8 rounded text-xs font-mono transition-colors ${p === page ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`page-${p}`}>{p}</button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyMarketplacePage;
