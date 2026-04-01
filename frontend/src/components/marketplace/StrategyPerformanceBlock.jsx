import { TrendingUp, Shield, Zap, BarChart3, Target } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";

const METRICS = [
  { key: "win_rate", label: "Win Rate", icon: Zap, fmt: v => `${v}%`, color: "text-[#00FF94]" },
  { key: "sharpe_ratio", label: "Sharpe Ratio", icon: TrendingUp, fmt: v => v?.toFixed(2), color: "text-white" },
  { key: "max_drawdown", label: "Max Drawdown", icon: Shield, fmt: v => `${v}%`, color: "text-white" },
  { key: "total_return", label: "Total Return", icon: Target, fmt: v => `${v}%`, color: v => v >= 0 ? "text-[#00FF94]" : "text-red-400" },
  { key: "total_trades", label: "Total Trades", icon: BarChart3, fmt: v => String(v), color: "text-white" },
];

const StrategyPerformanceBlock = ({ performance }) => {
  if (!performance) return null;

  return (
    <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="performance-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-[#7B61FF]" /> Performance
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {METRICS.map(m => {
            const val = performance[m.key];
            if (val == null) return null;
            const colorClass = typeof m.color === "function" ? m.color(val) : m.color;
            return (
              <div key={m.key} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
                <m.icon className="w-4 h-4 text-[#7B61FF] mx-auto mb-1.5" />
                <p className="text-[10px] text-zinc-600 mb-0.5">{m.label}</p>
                <p className={`text-base font-bold font-mono ${colorClass}`}>{m.fmt(val)}</p>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
};

export default StrategyPerformanceBlock;
