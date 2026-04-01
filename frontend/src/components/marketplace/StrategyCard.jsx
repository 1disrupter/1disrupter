import { Link } from "react-router-dom";
import { Star, Users, ArrowUpRight } from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";

const StrategyCard = ({ strategy, index = 0 }) => {
  const s = strategy;
  return (
    <Link to={`/marketplace/${s.id}`} data-testid={`strategy-card-${index}`}>
      <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-[#7B61FF]/30 transition-all cursor-pointer group h-full">
        <CardContent className="p-5">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-zinc-200 group-hover:text-white transition-colors truncate">{s.name}</h3>
              <p className="text-[11px] text-zinc-600 mt-0.5">by {s.creator_name}</p>
            </div>
            <ArrowUpRight className="w-4 h-4 text-zinc-700 group-hover:text-[#7B61FF] transition-colors shrink-0 ml-2" />
          </div>
          <p className="text-xs text-zinc-500 mb-3 line-clamp-2">{s.description || "No description"}</p>

          {/* Metrics row */}
          <div className="flex items-center gap-4 mb-3 text-[10px] font-mono">
            {s._perf?.win_rate != null && (
              <div className="text-[#00FF94]">
                <span className="text-zinc-600 mr-1">WR</span>{s._perf.win_rate}%
              </div>
            )}
            {s._perf?.sharpe_ratio != null && (
              <div className="text-white">
                <span className="text-zinc-600 mr-1">Sharpe</span>{s._perf.sharpe_ratio}
              </div>
            )}
            {s._perf?.total_return != null && (
              <div className={s._perf.total_return >= 0 ? "text-[#00FF94]" : "text-red-400"}>
                <span className="text-zinc-600 mr-1">Return</span>{s._perf.total_return}%
              </div>
            )}
          </div>

          {/* Tags + meta */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge className="bg-zinc-800 text-zinc-400 text-[10px]">{s.category}</Badge>
            {s.avg_rating > 0 && (
              <div className="flex items-center gap-0.5 text-amber-400">
                <Star className="w-3 h-3 fill-current" />
                <span className="text-[10px] font-mono">{s.avg_rating}</span>
              </div>
            )}
            <div className="flex items-center gap-1 text-zinc-600 text-[10px]">
              <Users className="w-3 h-3" />{s.subscriber_count}
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};

export default StrategyCard;
