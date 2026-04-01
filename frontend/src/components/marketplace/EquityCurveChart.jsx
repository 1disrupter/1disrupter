import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { TrendingUp } from "lucide-react";

const EquityCurveChart = ({ equityCurve = [] }) => {
  if (!equityCurve || equityCurve.length < 2) return null;

  const values = equityCurve.map(p => (typeof p === "number" ? p : p.value ?? p.equity ?? 0));
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const height = 120;
  const width = 100;

  const points = values.map((v, i) => {
    const x = (i / (values.length - 1)) * width;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  }).join(" ");

  const fillPoints = `0,${height} ${points} ${width},${height}`;
  const isPositive = values[values.length - 1] >= values[0];

  return (
    <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="equity-curve-card">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium text-zinc-400 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-[#7B61FF]" /> Equity Curve
        </CardTitle>
      </CardHeader>
      <CardContent>
        <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="w-full h-28">
          <defs>
            <linearGradient id={`eq-grad-${isPositive ? "up" : "down"}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={isPositive ? "#00FF94" : "#f87171"} stopOpacity="0.25" />
              <stop offset="100%" stopColor={isPositive ? "#00FF94" : "#f87171"} stopOpacity="0" />
            </linearGradient>
          </defs>
          <polygon points={fillPoints} fill={`url(#eq-grad-${isPositive ? "up" : "down"})`} />
          <polyline points={points} fill="none" stroke={isPositive ? "#00FF94" : "#f87171"} strokeWidth="1.5" vectorEffect="non-scaling-stroke" />
        </svg>
        <div className="flex justify-between text-[10px] text-zinc-600 font-mono mt-1">
          <span>{values[0]?.toFixed(2)}</span>
          <span className={isPositive ? "text-[#00FF94]" : "text-red-400"}>{values[values.length - 1]?.toFixed(2)}</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default EquityCurveChart;
