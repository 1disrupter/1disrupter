import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import axios from "axios";
import { Beaker, Play, FileCode, ScrollText, TrendingUp, TrendingDown, Minus, AlertTriangle, Loader2, X, Brain, Shield } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { mockResearchQueries } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";
import { API } from "../lib/constants";

const trendIcon = { bullish: TrendingUp, bearish: TrendingDown, neutral: Minus };
const trendColor = { bullish: "text-[#00FF94]", bearish: "text-red-400", neutral: "text-yellow-400" };
const riskColor = { low: "bg-[#00FF94]/15 text-[#00FF94]", medium: "bg-yellow-400/15 text-yellow-400", high: "bg-red-400/15 text-red-400" };

const DEMO_RESULT = {
  summary: "Bitcoin is consolidating near the $67,000 level after a strong rally. On-chain data shows increasing accumulation by long-term holders, while exchange reserves continue to decline — a bullish signal.",
  trend: "bullish",
  confidence: 78,
  indicators: ["Exchange outflows accelerating", "RSI at 58 — room to run", "200-day MA acting as strong support"],
  risk_level: "medium",
  timeframe: "medium-term"
};

const ResearchEnginePage = () => {
  const { isDemoMode, demoResearch } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const [query, setQuery] = useState("");
  const [selectedAsset, setSelectedAsset] = useState("BTC");
  const [isResearching, setIsResearching] = useState(false);
  const [result, setResult] = useState(null);

  const { data: apiReports, loading, error, refetch } = useApiData("/research/reports", { skip: isDemoMode, token });
  const { data: metrics } = useApiData("/research/metrics", { skip: isDemoMode, token });

  const researchQueries = isDemoMode ? demoResearch : (apiReports?.reports || apiReports || mockResearchQueries).map(r => ({
    query: r.query || r.title || r.name || "Research query",
    status: r.status || "completed",
    time: r.time || (r.created_at ? new Date(r.created_at).toLocaleString() : "recent"),
    tokens: r.tokens || r.token_count || 0,
  }));

  const stats = [
    { label: "Queries Today", value: String(metrics?.queries_today ?? researchQueries.length), change: "Recent", positive: true },
    { label: "Tokens Used", value: metrics?.tokens_used ? `${(metrics.tokens_used / 1000).toFixed(1)}K` : "8.4K", change: "of 50K limit", positive: true },
    { label: "Avg Response", value: metrics?.avg_response_time ? `${metrics.avg_response_time.toFixed(1)}s` : "3.2s", change: "Latency", positive: true },
    { label: "Saved Reports", value: String(metrics?.saved_reports ?? researchQueries.length), change: "Total", positive: true },
  ];

  const runResearch = async () => {
    const q = query.trim() || `What is the current ${selectedAsset} market outlook?`;
    if (isDemoMode) {
      setIsResearching(true);
      await new Promise(r => setTimeout(r, 1200));
      setResult({ ...DEMO_RESULT, query: q, asset: selectedAsset });
      setIsResearching(false);
      return;
    }
    setIsResearching(true);
    try {
      const res = await axios.post(`${API}/research/ai-query`, { query: q, asset: selectedAsset });
      if (res.data?.success) {
        setResult({ ...res.data.result, query: q, asset: selectedAsset, model: res.data.model });
      } else {
        toast.error("Research query failed");
      }
    } catch (e) {
      toast.error("Research query failed");
    }
    setIsResearching(false);
  };

  const TrendIcon = result ? (trendIcon[result.trend] || Minus) : Minus;

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="research-page">
      <div className="max-w-5xl mx-auto">
        <PageHeader icon={Beaker} title="Research Engine" description="AI-powered market research and analysis at your fingertips" badge="GPT-5.2" testId="research-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load research data" onRetry={refetch} /> : (
          <>
            <StatsRow stats={stats} />

            {/* Query Input */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-5">
                  <div className="flex gap-2 mb-3">
                    {["BTC", "ETH", "SOL"].map(a => (
                      <button key={a} onClick={() => setSelectedAsset(a)} className={`px-3 py-1 rounded-full text-xs font-mono font-medium transition-all ${selectedAsset === a ? "bg-[#7B61FF] text-white" : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"}`} data-testid={`asset-${a.toLowerCase()}`}>{a}</button>
                    ))}
                  </div>
                  <div className="flex gap-3">
                    <Input placeholder={`Ask anything about ${selectedAsset} markets, technicals, or on-chain data...`} value={query} onChange={e => setQuery(e.target.value)} onKeyDown={e => e.key === "Enter" && !isResearching && runResearch()} className="bg-[#050505] border-zinc-800 text-sm h-12 rounded-xl" data-testid="research-input" />
                    <Button onClick={runResearch} disabled={isResearching} className="rounded-xl bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white border border-[#7B61FF]/30 h-12 px-6" data-testid="research-btn">
                      {isResearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Play className="w-4 h-4 mr-2" /> Research</>}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* AI Result Panel */}
            <AnimatePresence>
              {result && (
                <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="mb-8">
                  <Card className="bg-[#0A0A0A] border-[#7B61FF]/30" data-testid="research-result">
                    <CardHeader className="pb-3 border-b border-zinc-800/50">
                      <div className="flex items-center justify-between">
                        <CardTitle className="text-sm font-medium flex items-center gap-2"><Brain className="w-4 h-4 text-[#7B61FF]" /> AI Analysis — {result.asset}</CardTitle>
                        <button onClick={() => setResult(null)} className="p-1 rounded hover:bg-white/5"><X className="w-4 h-4 text-zinc-500" /></button>
                      </div>
                      <p className="text-xs text-zinc-600 mt-1">Query: {result.query}</p>
                    </CardHeader>
                    <CardContent className="p-5 space-y-5">
                      {/* Summary */}
                      <p className="text-sm text-zinc-300 leading-relaxed">{result.summary}</p>

                      {/* Metrics Row */}
                      <div className="grid grid-cols-3 gap-3">
                        <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                          <p className="text-[10px] text-zinc-600 uppercase tracking-wider mb-1">Trend</p>
                          <div className={`flex items-center justify-center gap-1 ${trendColor[result.trend] || "text-zinc-400"}`}>
                            <TrendIcon className="w-4 h-4" />
                            <span className="text-sm font-semibold capitalize">{result.trend}</span>
                          </div>
                        </div>
                        <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                          <p className="text-[10px] text-zinc-600 uppercase tracking-wider mb-1">Confidence</p>
                          <span className="text-lg font-bold font-mono text-white">{result.confidence}%</span>
                        </div>
                        <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                          <p className="text-[10px] text-zinc-600 uppercase tracking-wider mb-1">Risk</p>
                          <Badge className={riskColor[result.risk_level] || "bg-zinc-600/15 text-zinc-400"}>{result.risk_level}</Badge>
                        </div>
                      </div>

                      {/* Indicators */}
                      {result.indicators?.length > 0 && (
                        <div>
                          <p className="text-xs text-zinc-500 mb-2 flex items-center gap-1"><Shield className="w-3 h-3" /> Key Indicators</p>
                          <div className="space-y-1.5">
                            {result.indicators.map((ind, i) => (
                              <div key={i} className="flex items-center gap-2 text-xs text-zinc-400">
                                <div className="w-1 h-1 rounded-full bg-[#7B61FF]" />
                                {ind}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <p className="text-[10px] text-zinc-700 text-right">Timeframe: {result.timeframe} {result.model && `| Model: ${result.model}`}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Recent Research */}
            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader><CardTitle className="text-sm font-medium flex items-center gap-2"><ScrollText className="w-4 h-4 text-[#7B61FF]" /> Recent Research</CardTitle></CardHeader>
                <CardContent>
                  <ScrollArea className="h-[260px]">
                    <div className="space-y-3">
                      {researchQueries.map((q, i) => (
                        <div key={i} className="p-4 rounded-lg bg-[#050505] border border-zinc-800/30 hover:border-zinc-700/50 transition-colors cursor-pointer" data-testid={`research-query-${i}`}>
                          <div className="flex items-start justify-between mb-2">
                            <p className="text-sm text-zinc-300 font-medium">{q.query}</p>
                            <Badge className="bg-[#00FF94]/10 text-[#00FF94] text-[10px] shrink-0 ml-3">{q.status}</Badge>
                          </div>
                          <div className="flex items-center gap-4 text-xs text-zinc-600">
                            <span>{q.time}</span>
                            <span>{q.tokens} tokens</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
};

export default ResearchEnginePage;
