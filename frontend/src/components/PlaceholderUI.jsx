import { motion } from "framer-motion";
import { Lock } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

export const PageHeader = ({ icon: Icon, title, description, badge, testId }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4 }}
    className="mb-8"
    data-testid={testId}
  >
    <div className="flex items-center gap-3 mb-2">
      {Icon && (
        <div className="p-2 rounded-lg bg-[#7B61FF]/10">
          <Icon className="w-6 h-6 text-[#7B61FF]" />
        </div>
      )}
      <h1 className="text-3xl md:text-4xl font-bold font-['Outfit'] tracking-tight">{title}</h1>
      {badge && (
        <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] border border-[#7B61FF]/30 text-xs">{badge}</Badge>
      )}
    </div>
    {description && (
      <p className="text-zinc-500 text-sm md:text-base ml-0 md:ml-14">{description}</p>
    )}
  </motion.div>
);

export const StatsRow = ({ stats }) => (
  <motion.div
    initial={{ opacity: 0, y: 15 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4, delay: 0.1 }}
    className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
  >
    {stats.map((stat, i) => (
      <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-colors">
        <CardContent className="p-5">
          <p className="text-xs text-zinc-500 mb-1.5 uppercase tracking-wider">{stat.label}</p>
          <p className="text-xl md:text-2xl font-bold font-['JetBrains_Mono'] text-white">{stat.value}</p>
          {stat.change && (
            <p className={`text-xs mt-1 font-mono ${stat.positive ? 'text-[#00FF94]' : 'text-red-400'}`}>
              {stat.change}
            </p>
          )}
        </CardContent>
      </Card>
    ))}
  </motion.div>
);

export const ComingSoonCard = ({ title, description, buttonLabel, icon: Icon }) => (
  <motion.div
    initial={{ opacity: 0, y: 15 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4, delay: 0.2 }}
  >
    <Card className="bg-[#0A0A0A] border-zinc-800/50 border-dashed">
      <CardContent className="p-8 flex flex-col items-center text-center">
        <div className="p-4 rounded-2xl bg-[#7B61FF]/5 border border-[#7B61FF]/10 mb-4">
          {Icon ? <Icon className="w-8 h-8 text-[#7B61FF]/60" /> : <Lock className="w-8 h-8 text-[#7B61FF]/60" />}
        </div>
        <h3 className="text-lg font-semibold font-['Outfit'] mb-2 text-zinc-300">{title}</h3>
        <p className="text-sm text-zinc-600 max-w-md mb-5">{description}</p>
        {buttonLabel && (
          <Button disabled className="rounded-full bg-[#7B61FF]/20 text-[#7B61FF]/60 border border-[#7B61FF]/10 cursor-not-allowed">
            {buttonLabel}
          </Button>
        )}
      </CardContent>
    </Card>
  </motion.div>
);

export const MockTable = ({ headers, rows }) => (
  <motion.div
    initial={{ opacity: 0, y: 15 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.4, delay: 0.15 }}
  >
    <Card className="bg-[#0A0A0A] border-zinc-800/50 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-zinc-800/50">
              {headers.map((h, i) => (
                <th key={i} className="px-5 py-3 text-left text-xs font-medium text-zinc-500 uppercase tracking-wider">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-zinc-800/30">
            {rows.map((row, i) => (
              <tr key={i} className="hover:bg-white/[0.02] transition-colors">
                {row.map((cell, j) => (
                  <td key={j} className="px-5 py-4 text-sm font-mono text-zinc-300 whitespace-nowrap">{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  </motion.div>
);

export const MiniChart = ({ data, color = '#7B61FF' }) => {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map(d => d.value));
  const min = Math.min(...data.map(d => d.value));
  const range = max - min || 1;
  const w = 200;
  const h = 60;
  const points = data.map((d, i) => `${(i / (data.length - 1)) * w},${h - ((d.value - min) / range) * h}`).join(' ');

  return (
    <svg width={w} height={h} className="opacity-60">
      <defs>
        <linearGradient id={`grad-${color.replace('#','')}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={`0,${h} ${points} ${w},${h}`} fill={`url(#grad-${color.replace('#','')})`} />
      <polyline points={points} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
};


export const LoadingSkeleton = ({ rows = 4 }) => (
  <div className="space-y-4 animate-pulse" data-testid="loading-skeleton">
    {Array.from({ length: rows }).map((_, i) => (
      <div key={i} className="h-16 rounded-xl bg-zinc-800/40" />
    ))}
  </div>
);

export const ErrorState = ({ message = 'Failed to load data', onRetry }) => (
  <div className="flex flex-col items-center justify-center py-16 text-center" data-testid="error-state">
    <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mb-4">
      <span className="text-red-400 text-xl">!</span>
    </div>
    <p className="text-sm text-zinc-400 mb-4">{message}</p>
    {onRetry && (
      <button onClick={onRetry} className="text-xs text-[#7B61FF] hover:underline">Try again</button>
    )}
  </div>
);
