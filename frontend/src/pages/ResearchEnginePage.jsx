import { useState } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { Beaker, Play, FileCode, ScrollText } from "lucide-react";
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

const ResearchEnginePage = () => {
  const { isDemoMode, demoResearch } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const [query, setQuery] = useState('');

  const { data: apiReports, loading, error, refetch } = useApiData('/research/reports', { skip: isDemoMode, token });
  const { data: metrics } = useApiData('/research/metrics', { skip: isDemoMode, token });

  const researchQueries = isDemoMode ? demoResearch : (apiReports?.reports || apiReports || mockResearchQueries).map(r => ({
    query: r.query || r.title || r.name || 'Research query',
    status: r.status || 'completed',
    time: r.time || (r.created_at ? new Date(r.created_at).toLocaleString() : 'recent'),
    tokens: r.tokens || r.token_count || 0,
  }));

  const stats = [
    { label: 'Queries Today', value: String(metrics?.queries_today ?? researchQueries.length), change: 'Recent', positive: true },
    { label: 'Tokens Used', value: metrics?.tokens_used ? `${(metrics.tokens_used / 1000).toFixed(1)}K` : '8.4K', change: 'of 50K limit', positive: true },
    { label: 'Avg Response', value: metrics?.avg_response_time ? `${metrics.avg_response_time.toFixed(1)}s` : '3.2s', change: 'Latency', positive: true },
    { label: 'Saved Reports', value: String(metrics?.saved_reports ?? researchQueries.length), change: 'Total', positive: true },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="research-page">
      <div className="max-w-5xl mx-auto">
        <PageHeader icon={Beaker} title="Research Engine" description="AI-powered market research and analysis at your fingertips" badge="GPT-5.2" testId="research-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load research data" onRetry={refetch} /> : (
          <>
            <StatsRow stats={stats} />

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-5">
                  <div className="flex gap-3">
                    <Input placeholder="Ask anything about crypto markets, technicals, or on-chain data..." value={query} onChange={(e) => setQuery(e.target.value)} className="bg-[#050505] border-zinc-800 text-sm h-12 rounded-xl" data-testid="research-input" />
                    <Button onClick={() => toast.info("AI research engine coming soon")} className="rounded-xl bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white border border-[#7B61FF]/30 h-12 px-6" data-testid="research-btn"><Play className="w-4 h-4 mr-2" /> Research</Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader><CardTitle className="text-sm font-medium flex items-center gap-2"><ScrollText className="w-4 h-4 text-[#7B61FF]" /> Recent Research</CardTitle></CardHeader>
                <CardContent>
                  <ScrollArea className="h-[300px]">
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

                      <div className="p-4 rounded-lg bg-gradient-to-b from-[#7B61FF]/5 to-transparent border border-[#7B61FF]/10">
                        <div className="flex items-center gap-2 mb-3">
                          <FileCode className="w-4 h-4 text-[#7B61FF]" />
                          <span className="text-xs text-[#7B61FF] font-medium">Sample Research Output</span>
                        </div>
                        <div className="text-xs text-zinc-500 leading-relaxed space-y-2">
                          <p><span className="text-zinc-300 font-medium">BTC Support Analysis:</span> Bitcoin is currently testing the $65,200 support level after a rejection at $68,500. The 200-day EMA sits at $64,800, providing confluence support.</p>
                          <p><span className="text-zinc-300 font-medium">Key Levels:</span> Support: $65,200 / $64,800 / $62,400. Resistance: $68,500 / $71,200 / $73,800.</p>
                          <p><span className="text-zinc-300 font-medium">On-chain:</span> Exchange reserves down 2.1% this week. Long-term holder supply at ATH. Funding rates neutral.</p>
                        </div>
                      </div>
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
