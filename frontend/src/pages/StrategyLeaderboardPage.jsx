import { useState, useEffect, useCallback } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Trophy, ChevronUp, ChevronDown, ArrowUpRight, Eye
} from "lucide-react";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";

const API = process.env.REACT_APP_BACKEND_URL;

const SORT_COLS = [
  { key: "total_return", label: "Return %" },
  { key: "sharpe_ratio", label: "Sharpe" },
  { key: "win_rate", label: "Win Rate %" },
  { key: "max_drawdown", label: "Max DD %" },
];

const riskBadge = (label) => {
  if (!label) return null;
  const cls =
    label === "High" ? "bg-red-500/15 text-red-400" :
    label === "Medium-High" ? "bg-orange-500/15 text-orange-400" :
    label === "Medium" ? "bg-amber-500/15 text-amber-400" :
    "bg-green-500/15 text-green-400";
  return <Badge className={`text-[10px] ${cls}`}>{label}</Badge>;
};

const fmtVal = (v, suffix = "") => {
  if (v == null) return <span className="text-zinc-700">—</span>;
  const num = Number(v);
  const color = num > 0 ? "text-[#00FF94]" : num < 0 ? "text-red-400" : "text-zinc-400";
  return <span className={`font-mono ${color}`}>{num > 0 ? "+" : ""}{num}{suffix}</span>;
};

const RowSkeleton = () => (
  <tr className="border-b border-zinc-800/30">
    {Array.from({ length: 8 }).map((_, i) => (
      <td key={i} className="px-4 py-3"><div className="h-4 bg-zinc-800 rounded animate-pulse w-16" /></td>
    ))}
  </tr>
);

const StrategyLeaderboardPage = () => {
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState("total_return");
  const [sortOrder, setSortOrder] = useState("desc");

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/marketplace/strategies/leaderboard?sort_by=${sortBy}&order=${sortOrder}`);
      if (res.ok) {
        const data = await res.json();
        setStrategies(data.strategies || []);
      }
    } catch {
      /* silent — keep existing data */
    }
    setLoading(false);
  }, [sortBy, sortOrder]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const toggleSort = (key) => {
    if (sortBy === key) {
      setSortOrder(prev => prev === "desc" ? "asc" : "desc");
    } else {
      setSortBy(key);
      setSortOrder("desc");
    }
  };

  const SortIcon = ({ col }) => {
    if (sortBy !== col) return <ChevronDown className="w-3 h-3 text-zinc-700" />;
    return sortOrder === "desc"
      ? <ChevronDown className="w-3 h-3 text-[#7B61FF]" />
      : <ChevronUp className="w-3 h-3 text-[#7B61FF]" />;
  };

  return (
    <div className="min-h-screen pt-28 pb-20 px-4" data-testid="strategy-leaderboard-page">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 rounded-xl bg-[#7B61FF]/10 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-[#7B61FF]" />
            </div>
            <h1 className="text-2xl md:text-3xl font-bold font-['Outfit']" data-testid="leaderboard-title">Strategy Leaderboard</h1>
          </div>
          <p className="text-zinc-500 text-sm max-w-lg">All public AI strategies ranked by performance. Click any row to view full details.</p>
        </motion.div>

        {/* Table */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50 overflow-hidden" data-testid="leaderboard-table-card">
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full text-sm" data-testid="leaderboard-table">
                  <thead>
                    <tr className="border-b border-zinc-800/50 text-zinc-500 text-xs uppercase tracking-wider">
                      <th className="px-4 py-3 text-left font-medium">#</th>
                      <th className="px-4 py-3 text-left font-medium">Strategy</th>
                      <th className="px-4 py-3 text-left font-medium">Risk</th>
                      {SORT_COLS.map(col => (
                        <th
                          key={col.key}
                          className="px-4 py-3 text-right font-medium cursor-pointer hover:text-zinc-300 transition-colors select-none"
                          onClick={() => toggleSort(col.key)}
                          data-testid={`sort-${col.key}`}
                        >
                          <span className="inline-flex items-center gap-1">
                            {col.label}<SortIcon col={col.key} />
                          </span>
                        </th>
                      ))}
                      <th className="px-4 py-3 text-right font-medium">Category</th>
                      <th className="px-4 py-3 text-center font-medium">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {loading ? (
                      Array.from({ length: 6 }).map((_, i) => <RowSkeleton key={i} />)
                    ) : strategies.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="px-4 py-12 text-center text-zinc-600">No strategies found</td>
                      </tr>
                    ) : (
                      strategies.map((s, i) => {
                        const p = s._perf || {};
                        return (
                          <motion.tr
                            key={s.id}
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: i * 0.03 }}
                            className="border-b border-zinc-800/20 hover:bg-zinc-900/50 transition-colors group"
                            data-testid={`leaderboard-row-${i}`}
                          >
                            <td className="px-4 py-3 text-zinc-600 font-mono text-xs">{i + 1}</td>
                            <td className="px-4 py-3">
                              <Link to={`/marketplace/${s.id}`} className="group-hover:text-[#7B61FF] transition-colors">
                                <div className="font-semibold text-zinc-200 text-sm" data-testid={`row-name-${i}`}>{s.name}</div>
                                <div className="text-[11px] text-zinc-600 mt-0.5">by {s.creator_name}</div>
                              </Link>
                            </td>
                            <td className="px-4 py-3" data-testid={`row-risk-${i}`}>{riskBadge(s.risk_label)}</td>
                            <td className="px-4 py-3 text-right" data-testid={`row-return-${i}`}>{fmtVal(p.total_return, "%")}</td>
                            <td className="px-4 py-3 text-right">{fmtVal(p.sharpe_ratio)}</td>
                            <td className="px-4 py-3 text-right">{fmtVal(p.win_rate, "%")}</td>
                            <td className="px-4 py-3 text-right">{fmtVal(p.max_drawdown, "%")}</td>
                            <td className="px-4 py-3 text-right">
                              <Badge className="bg-zinc-800 text-zinc-400 text-[10px]">{s.category}</Badge>
                            </td>
                            <td className="px-4 py-3 text-center">
                              <Link to={`/marketplace/${s.id}`}>
                                <Button size="sm" variant="ghost" className="h-7 rounded-full text-xs text-zinc-400 hover:text-[#7B61FF]" data-testid={`row-view-${i}`}>
                                  <Eye className="w-3.5 h-3.5 mr-1" />View
                                </Button>
                              </Link>
                            </td>
                          </motion.tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="font-mono text-[11px] text-zinc-700">
            Simulated results. Past performance does not guarantee future returns.
          </p>
        </div>
      </div>
    </div>
  );
};

export default StrategyLeaderboardPage;
