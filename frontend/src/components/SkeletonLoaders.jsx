/**
 * Skeleton loaders for Strategy Page performance polish.
 */
import { Card, CardContent, CardHeader } from "./ui/card";

const Pulse = ({ className = "" }) => (
  <div className={`animate-pulse rounded bg-zinc-800/60 ${className}`} />
);

export const ChartSkeleton = () => (
  <div data-testid="skeleton-chart" className="space-y-2">
    <Pulse className="h-3 w-24" />
    <div className="h-32 flex items-end gap-[2px]">
      {Array.from({ length: 20 }).map((_, i) => (
        <Pulse
          key={i}
          className="flex-1 rounded-t"
          style={{ height: `${20 + Math.random() * 70}%` }}
        />
      ))}
    </div>
  </div>
);

export const StatsSkeleton = () => (
  <div data-testid="skeleton-stats" className="grid grid-cols-2 md:grid-cols-4 gap-3">
    {Array.from({ length: 4 }).map((_, i) => (
      <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center">
        <Pulse className="h-2.5 w-16 mx-auto mb-2" />
        <Pulse className="h-6 w-12 mx-auto" />
      </div>
    ))}
  </div>
);

export const AlertCardSkeleton = () => (
  <div data-testid="skeleton-alert">
    <Card className="bg-[#0A0A0A] border-zinc-800/50">
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <Pulse className="w-9 h-9 rounded-lg shrink-0" />
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <Pulse className="h-4 w-14 rounded-full" />
              <Pulse className="h-3 w-10" />
            </div>
            <Pulse className="h-3 w-full" />
            <Pulse className="h-3 w-3/4" />
            <div className="flex gap-3 mt-1">
              <Pulse className="h-2.5 w-20" />
              <Pulse className="h-2.5 w-12" />
            </div>
          </div>
          <Pulse className="h-4 w-16 shrink-0" />
        </div>
      </CardContent>
    </Card>
  </div>
);

export const AlertListSkeleton = ({ count = 4 }) => (
  <div className="space-y-3" data-testid="skeleton-alert-list">
    {Array.from({ length: count }).map((_, i) => (
      <AlertCardSkeleton key={i} />
    ))}
  </div>
);

export const HeaderSkeleton = () => (
  <div data-testid="skeleton-header" className="mb-8">
    <div className="flex items-center gap-3 mb-2">
      <Pulse className="w-11 h-11 rounded-xl" />
      <Pulse className="h-7 w-48" />
    </div>
    <Pulse className="h-3.5 w-64 ml-14" />
  </div>
);

export const LeaderboardRowSkeleton = ({ count = 5 }) => (
  <div data-testid="skeleton-leaderboard-rows" className="divide-y divide-zinc-800/30">
    {Array.from({ length: count }).map((_, i) => (
      <div key={i} className="flex items-center gap-4 px-4 py-4">
        <Pulse className="w-7 h-7 rounded-full" />
        <Pulse className="h-4 w-32" />
        <Pulse className="h-5 w-16 rounded-full ml-2" />
        <Pulse className="h-3 w-12 ml-auto" />
        <Pulse className="h-3 w-10" />
        <Pulse className="h-3 w-10" />
        <Pulse className="h-3 w-10" />
        <Pulse className="h-7 w-20 rounded-full" />
      </div>
    ))}
  </div>
);

export const PodiumSkeleton = () => (
  <div data-testid="skeleton-podium" className="grid grid-cols-3 gap-4 mb-8">
    {[false, true, false].map((tall, i) => (
      <Card key={i} className={`bg-[#0A0A0A] border-zinc-800/30 ${tall ? "md:-mt-4" : ""}`}>
        <CardContent className="p-4 text-center space-y-2">
          <Pulse className="h-8 w-10 mx-auto" />
          <Pulse className="h-4 w-24 mx-auto" />
          <Pulse className="h-5 w-16 mx-auto rounded-full" />
          <div className="space-y-1.5 mt-3">
            <Pulse className="h-2.5 w-full" />
            <Pulse className="h-2.5 w-full" />
            <Pulse className="h-2.5 w-full" />
          </div>
        </CardContent>
      </Card>
    ))}
  </div>
);

export const StrategyDetailSkeleton = () => (
  <div data-testid="skeleton-strategy-detail" className="space-y-5">
    <StatsSkeleton />
    <ChartSkeleton />
    <div className="grid grid-cols-3 gap-3">
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800/30 text-center space-y-1.5">
          <Pulse className="w-4 h-4 mx-auto rounded" />
          <Pulse className="h-2.5 w-16 mx-auto" />
          <Pulse className="h-3 w-10 mx-auto" />
        </div>
      ))}
    </div>
    <Pulse className="h-9 w-full rounded-full" />
  </div>
);
