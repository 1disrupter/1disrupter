import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Badge } from "../ui/badge";
import { Zap } from "lucide-react";

const SignalsTable = ({ signals = [] }) => {
  if (signals.length === 0) return null;

  return (
    <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="signals-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <Zap className="w-4 h-4 text-[#7B61FF]" /> Recent Signals ({signals.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-xs" data-testid="signals-table">
            <thead>
              <tr className="border-b border-zinc-800/50">
                <th className="text-left py-2 px-3 text-zinc-600 font-medium">Time</th>
                <th className="text-left py-2 px-3 text-zinc-600 font-medium">Symbol</th>
                <th className="text-left py-2 px-3 text-zinc-600 font-medium">Signal</th>
                <th className="text-right py-2 px-3 text-zinc-600 font-medium">Price</th>
              </tr>
            </thead>
            <tbody>
              {signals.slice(0, 10).map((sig, i) => (
                <tr key={i} className="border-b border-zinc-800/20 hover:bg-white/[0.02]">
                  <td className="py-2 px-3 text-zinc-500 font-mono">
                    {sig.created_at ? new Date(sig.created_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—"}
                  </td>
                  <td className="py-2 px-3 text-zinc-300 font-mono">{sig.symbol || sig.pair || "—"}</td>
                  <td className="py-2 px-3">
                    <Badge className={`text-[10px] ${(sig.action || sig.signal_type || "").toUpperCase().includes("BUY") ? "bg-[#00FF94]/15 text-[#00FF94]" : "bg-red-400/15 text-red-400"}`}>
                      {sig.action || sig.signal_type || "SIGNAL"}
                    </Badge>
                  </td>
                  <td className="py-2 px-3 text-right text-zinc-300 font-mono">{sig.price != null ? `$${Number(sig.price).toLocaleString()}` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

export default SignalsTable;
