import { useState } from "react";
import { motion } from "framer-motion";
import {
  Beaker, Play, FileCode, ScrollText, Target, RefreshCw
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { ScrollArea } from "../components/ui/scroll-area";
import { PageHeader, StatsRow } from "../components/PlaceholderUI";
import { mockResearchQueries } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";

const ResearchEnginePage = () => {
  const { isDemoMode, demoResearch } = useDemoMode();
  const researchQueries = isDemoMode ? demoResearch : mockResearchQueries;
  const [query, setQuery] = useState('');

  const stats = [
    { label: 'Queries Today', value: '12', change: '+4', positive: true },
    { label: 'Tokens Used', value: '8.4K', change: 'of 50K limit', positive: true },
    { label: 'Avg Response', value: '3.2s', change: '-0.8s', positive: true },
    { label: 'Saved Reports', value: '7', change: '+2 this week', positive: true },
  ];

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="research-page">
      <div className="max-w-5xl mx-auto">
        <PageHeader
          icon={Beaker}
          title="Research Engine"
          description="AI-powered market research and analysis at your fingertips"
          badge="GPT-5.2"
          testId="research-header"
        />

        <StatsRow stats={stats} />

        {/* Search Input */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-8">
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-5">
              <div className="flex gap-3">
                <Input
                  placeholder="Ask anything about crypto markets, technicals, or on-chain data..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="bg-[#050505] border-zinc-800 text-sm h-12 rounded-xl"
                  data-testid="research-input"
                />
                <Button disabled className="rounded-xl bg-[#7B61FF]/20 text-[#7B61FF]/60 border border-[#7B61FF]/10 h-12 px-6">
                  <Play className="w-4 h-4 mr-2" /> Research
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Recent Queries */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <ScrollText className="w-4 h-4 text-[#7B61FF]" /> Recent Research
              </CardTitle>
            </CardHeader>
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

                  {/* Sample Research Output */}
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
      </div>
    </div>
  );
};

export default ResearchEnginePage;
