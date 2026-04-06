import { Bot } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { useSystemMode } from "../contexts/DemoModeContext";
import LiveAgentPerformance from "../components/LiveAgentPerformance";

const AgentsPage = () => {
  const { isDemo, isLive } = useSystemMode();

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="agents-page">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/20">
              <Bot className="w-6 h-6 text-[#7B61FF]" />
            </div>
            <div>
              <h1 className="text-2xl font-bold font-['Outfit'] text-zinc-100" data-testid="agents-title">
                Trading Agents
              </h1>
              <p className="text-sm text-zinc-500 mt-0.5">
                {isLive
                  ? "Real-time performance metrics from 4 AI agents"
                  : "Agent performance unavailable in demo mode"}
              </p>
            </div>
          </div>

          <Badge
            className={`text-[10px] font-mono px-3 py-1.5 ${
              isLive
                ? "bg-[#00FF94]/10 text-[#00FF94] border border-[#00FF94]/20"
                : "bg-[#7B61FF]/10 text-[#7B61FF] border border-[#7B61FF]/20"
            }`}
            data-testid={isLive ? "agents-live-badge" : "agents-demo-badge"}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full mr-1.5 inline-block ${
                isLive ? "bg-[#00FF94] animate-pulse" : "bg-[#7B61FF]"
              }`}
            />
            {isLive ? "LIVE" : "DEMO"}
          </Badge>
        </div>

        {/* Content */}
        {isLive ? (
          <LiveAgentPerformance />
        ) : (
          <div
            className="rounded-xl border border-zinc-800/50 bg-[#0A0A0A] py-20 text-center"
            data-testid="agents-demo-placeholder"
          >
            <Bot className="w-12 h-12 text-zinc-800 mx-auto mb-4" />
            <p className="text-sm text-zinc-500 font-medium">Demo mode — no live agent stats</p>
            <p className="text-xs text-zinc-700 mt-1">
              Switch to Live mode in the admin panel to view real agent performance
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentsPage;
