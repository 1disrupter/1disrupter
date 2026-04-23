"use client";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Activity, Radar, CalendarClock, Clock, ThumbsUp } from "lucide-react";
import { listAdminVenues, triggerSignalRefresh, ExternalSignals } from "@/lib/api";
import { Topbar } from "@/components/Sidebar";
import { Button, Chip } from "@/components/ui";
import { cn } from "@/lib/cn";

const SIGNAL_META = {
  google_score:     { label: "Google",   icon: <Radar size={12} />, tone: "text-primary-glow", bar: "bg-primary-glow" },
  social_score:     { label: "Social",   icon: <Activity size={12} />, tone: "text-accent-pink", bar: "bg-accent-pink" },
  event_score:      { label: "Events",   icon: <CalendarClock size={12} />, tone: "text-status-busy", bar: "bg-status-busy" },
  time_score:       { label: "Time",     icon: <Clock size={12} />, tone: "text-glow-aqua", bar: "bg-glow-aqua" },
  user_votes_score: { label: "Votes",    icon: <ThumbsUp size={12} />, tone: "text-status-medium", bar: "bg-status-medium" },
} as const;

export default function SignalsPage() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["admin-venues"], queryFn: listAdminVenues });
  const refresh = useMutation({
    mutationFn: triggerSignalRefresh,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin-venues"] }),
  });

  const rows = q.data?.items ?? [];

  return (
    <>
      <Topbar
        title="SIGNALS"
        rightSlot={
          <>
            <Chip tone="purple">Live</Chip>
            <Chip>{rows.length} rows</Chip>
            <Button
              variant="pink" size="sm"
              leftIcon={<RefreshCw size={14} className={refresh.isPending ? "animate-spin" : ""} />}
              onClick={() => refresh.mutate()}
              loading={refresh.isPending}
            >
              {refresh.isPending ? "Refreshing…" : "Refresh all signals"}
            </Button>
          </>
        }
      />
      <main className="flex-1 space-y-4 p-6">
        <p className="text-xs uppercase tracking-[0.28em] text-white/45">
          Raw signal values · updated by the scheduler every 5 minutes · newest first
        </p>
        <div className="grid gap-3 lg:grid-cols-2">
          {rows
            .slice()
            .sort((a, b) => new Date(b.external_signals?.updated_at ?? 0).getTime() - new Date(a.external_signals?.updated_at ?? 0).getTime())
            .map((r) => (
              <div key={r.venue.id} className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-white">{r.venue.name}</p>
                    <p className="mt-1 text-[10px] font-mono text-white/45">
                      {r.external_signals?.updated_at ? new Date(r.external_signals.updated_at).toLocaleString() : "no signals yet"}
                    </p>
                  </div>
                  <span className="font-mono text-2xl text-primary-glow">{r.vibe.vibe_score.toFixed(2)}</span>
                </div>
                <div className="mt-3 space-y-1.5">
                  {(Object.keys(SIGNAL_META) as (keyof typeof SIGNAL_META)[]).map((k) => {
                    const v = Number(r.external_signals?.[k as keyof ExternalSignals] ?? 0);
                    const pct = (v / 10) * 100;
                    const m = SIGNAL_META[k];
                    return (
                      <div key={k} className="space-y-0.5">
                        <div className="flex items-center justify-between text-[11px]">
                          <span className={cn("flex items-center gap-1", m.tone)}>{m.icon} {m.label}</span>
                          <span className="font-mono text-white/80">{v.toFixed(2)}</span>
                        </div>
                        <div className="h-1 overflow-hidden rounded-full bg-white/5">
                          <div className={cn("h-full rounded-full", m.bar)} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
        </div>
      </main>
    </>
  );
}
