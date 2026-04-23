"use client";
import { useEffect, useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { X, Activity, Radar, CalendarClock, Clock, ThumbsUp, TrendingUp, TrendingDown, Minus, Zap, AlertTriangle, Gem, Music2, Coins, Radio, Navigation } from "lucide-react";
import { cn } from "@/lib/cn";
import {
  AdminVenueRow, updateSignals, triggerSignalRefresh,
  getForecast, getTouristFlags, getLiveMusic, TouristLabel, Trend,
  listOffers, listRedemptions, getTrajectory, getIntelScore,
} from "@/lib/api";
import { Button, Chip, Slider } from "./ui";
import { useVibePulse } from "@/hooks/useVibePulse";

const SIGNAL_META = {
  google_score:     { label: "Google busyness", icon: <Radar size={14} />, tone: "text-primary-glow", bar: "bg-primary-glow" },
  social_score:     { label: "Social activity", icon: <Activity size={14} />, tone: "text-accent-pink", bar: "bg-accent-pink" },
  event_score:      { label: "Live events",     icon: <CalendarClock size={14} />, tone: "text-status-busy", bar: "bg-status-busy" },
  time_score:       { label: "Time pattern",    icon: <Clock size={14} />, tone: "text-glow-aqua", bar: "bg-glow-aqua" },
  user_votes_score: { label: "Recent votes",    icon: <ThumbsUp size={14} />, tone: "text-status-medium", bar: "bg-status-medium" },
} as const;

const TREND: Record<Trend, { icon: React.ReactNode; tone: string; label: string }> = {
  rising:  { icon: <TrendingUp size={14} />,   tone: "text-glow-aqua",  label: "Rising" },
  peaking: { icon: <Zap size={14} />,          tone: "text-accent-pink",label: "Peaking" },
  falling: { icon: <TrendingDown size={14} />, tone: "text-white/55",   label: "Falling" },
  steady:  { icon: <Minus size={14} />,        tone: "text-white/70",   label: "Steady" },
};
const LABEL: Record<TouristLabel, { icon: React.ReactNode; tone: string; label: string }> = {
  tourist_trap: { icon: <AlertTriangle size={14} />, tone: "text-status-busy", label: "Tourist trap" },
  local_gem:    { icon: <Gem size={14} />,           tone: "text-glow-aqua",   label: "Local gem" },
  neutral:      { icon: <Minus size={14} />,         tone: "text-white/65",    label: "Neutral" },
};

export function InspectorModal({ row, onClose, onSaved }: { row: AdminVenueRow; onClose: () => void; onSaved: () => void }) {
  const [signals, setSignals] = useState(row.vibe.signals);
  const save = useMutation({
    mutationFn: () => updateSignals(row.venue.id, {
      manual_score: signals.manual_score,
      social_activity: signals.social_activity,
      time_prediction: signals.time_prediction,
      venue_boost: signals.venue_boost,
    }),
    onSuccess: () => { onSaved(); onClose(); },
  });
  const refresh = useMutation({
    mutationFn: triggerSignalRefresh,
    onSuccess: () => onSaved(),
  });

  const forecastQ = useQuery({ queryKey: ["forecast-all"], queryFn: getForecast });
  const flagsQ = useQuery({ queryKey: ["tourist-flags"], queryFn: getTouristFlags });
  const liveQ = useQuery({ queryKey: ["live-music-all"], queryFn: getLiveMusic });
  const offersQ = useQuery({
    queryKey: ["offers", row.venue.id],
    queryFn: () => listOffers(row.venue.id, false),
  });
  const redemptionsQ = useQuery({
    queryKey: ["redemptions", row.venue.id],
    queryFn: () => listRedemptions({ venue_id: row.venue.id, limit: 10 }),
  });
  const trajQ = useQuery({
    queryKey: ["trajectory", row.venue.id],
    queryFn: () => getTrajectory(row.venue.id, 6),
  });
  const travelQ = useQuery({
    queryKey: ["travel", row.venue.id],
    queryFn: () => getIntelScore(row.venue.id, 40.73, -73.99),
  });
  const pulse = useVibePulse(row.venue.id);

  const forecast = forecastQ.data?.items.find((x) => x.venue_id === row.venue.id);
  const flag = flagsQ.data?.items.find((x: any) => x.venue_id === row.venue.id);
  const live = liveQ.data?.items.find((x: any) => x.venue_id === row.venue.id);

  const localScore = useMemo(() => {
    const s = signals;
    const v = s.manual_score * 0.25 + s.social_activity * 0.25 + s.user_votes * 0.25 +
      s.time_prediction * 0.15 + s.venue_boost * 0.10;
    return Math.max(0, Math.min(10, v));
  }, [signals]);
  const crowd = localScore >= 8 ? "Busy" : localScore >= 5 ? "Medium" : "Dead";

  useEffect(() => {
    const k = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", k);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", k);
      document.body.style.overflow = "";
    };
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[#05050A]/80 backdrop-blur-md" onClick={onClose} />
      <div className="relative w-full max-w-5xl max-h-[90vh] overflow-y-auto rounded-xl3 border border-primary-glow/30 bg-background-dark shadow-softPurple">
        <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
          <h3 className="font-display text-2xl tracking-wider text-white">{row.venue.name.toUpperCase()}</h3>
          <div className="flex items-center gap-3">
            {pulse.live ? (
              <Chip tone="aqua" className="animate-pulse" data-testid="inspector-live-chip">
                <Radio size={10} /> LIVE
              </Chip>
            ) : (
              <Chip tone="neutral">OFFLINE</Chip>
            )}
            <button onClick={onClose} aria-label="Close" className="rounded-full p-2 text-white/60 hover:text-white hover:bg-white/10">
              <X size={18} />
            </button>
          </div>
        </div>

        <div className="grid gap-6 p-5 md:grid-cols-3">
          {/* LEFT — editable */}
          <div className="space-y-4">
            <h4 className="text-[11px] uppercase tracking-[0.28em] text-primary-glow">Edit</h4>
            <Slider label="Manual score"     value={signals.manual_score}    onChange={(v) => setSignals({ ...signals, manual_score: v })} />
            <Slider label="Social activity"  value={signals.social_activity} onChange={(v) => setSignals({ ...signals, social_activity: v })} />
            <Slider label="Time prediction"  value={signals.time_prediction} onChange={(v) => setSignals({ ...signals, time_prediction: v })} />
            <Slider label="Venue boost"      value={signals.venue_boost}     onChange={(v) => setSignals({ ...signals, venue_boost: v })} />
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3 text-xs text-white/55">
              <span className="text-white/75">user_votes</span> driven by <code className="text-primary-glow">/feedback</code>. Current:
              {" "}<b className="text-white">{signals.user_votes.toFixed(2)}</b>
            </div>
          </div>

          {/* MIDDLE — signal engine */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-[11px] uppercase tracking-[0.28em] text-primary-glow">Signal engine</h4>
              <span className="text-[10px] text-white/45">
                {row.external_signals?.updated_at ? new Date(row.external_signals.updated_at).toLocaleTimeString() : "—"}
              </span>
            </div>
            <div className="space-y-2.5">
              {(Object.keys(SIGNAL_META) as (keyof typeof SIGNAL_META)[]).map((k) => {
                const v = Number(row.external_signals?.[k] ?? 0);
                const pct = Math.max(0, Math.min(100, (v / 10) * 100));
                const m = SIGNAL_META[k];
                return (
                  <div key={k} className="space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className={cn("flex items-center gap-1.5", m.tone)}>
                        {m.icon} {m.label}
                      </span>
                      <span className="font-mono text-white">{v.toFixed(2)}</span>
                    </div>
                    <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                      <div className={cn("h-full rounded-full transition-all", m.bar)} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* RIGHT — live preview + intel */}
          <div className="space-y-4">
            <div className="flex flex-col items-center gap-3 rounded-xl2 border border-primary-glow/30 bg-primary/5 p-5 text-center">
              <Chip tone="purple">Live preview</Chip>
              <span
                className="font-display text-6xl leading-none text-white"
                style={{ textShadow: "0 0 18px rgba(177,92,255,0.8)" }}
              >
                {(pulse.last?.vibe_score ?? localScore).toFixed(1)}
              </span>
              <span className="text-[11px] uppercase tracking-[0.26em] text-white/55">
                Vibe score · {(pulse.last?.crowd_level ?? crowd).toString()}
              </span>
              {pulse.last?.last_updated && (
                <span className="text-[10px] text-white/40">
                  updated {new Date(pulse.last.last_updated).toLocaleTimeString()}
                </span>
              )}
            </div>

            {travelQ.data && (
              <div className="rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid="inspector-travel-panel">
                <div className="mb-2 flex items-center justify-between">
                  <h4 className="text-[11px] uppercase tracking-[0.28em] text-primary-glow"><Navigation size={12} className="inline mr-1" /> Travel time</h4>
                  <Chip tone="neutral">{(travelQ.data.travel_provider || "stub").toUpperCase()}</Chip>
                </div>
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.22em] text-white/45">Walking</p>
                    <p className="mt-1 font-display text-2xl text-glow-aqua">{Math.round(travelQ.data.walking_time_minutes ?? 0)}<span className="ml-1 text-xs text-white/55">min</span></p>
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-[0.22em] text-white/45">Driving</p>
                    <p className="mt-1 font-display text-2xl text-accent-pink">{Math.round(travelQ.data.driving_time_minutes ?? 0)}<span className="ml-1 text-xs text-white/55">min</span></p>
                  </div>
                </div>
              </div>
            )}

            <div className="space-y-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-4">
              <h4 className="text-[11px] uppercase tracking-[0.28em] text-primary-glow">Intelligence</h4>
              <Intel label="Forecast" icon={forecast ? TREND[forecast.trend].icon : undefined}
                     value={forecast ? TREND[forecast.trend].label : "—"} tone={forecast ? TREND[forecast.trend].tone : ""}
                     sub={forecast ? `Δ next hr ${forecast.delta_next_hour.toFixed(2)}` : ""} />
              <Intel label="Crowd type" icon={flag ? LABEL[flag.label as TouristLabel].icon : undefined}
                     value={flag ? LABEL[flag.label as TouristLabel].label : "—"} tone={flag ? LABEL[flag.label as TouristLabel].tone : ""}
                     sub={flag?.reason} />
              <Intel label="Live music" icon={<Music2 size={14} />}
                     value={live?.live_music ? "Likely tonight" : "Not tonight"}
                     tone={live?.live_music ? "text-accent-pink" : "text-white/55"}
                     sub={`conf ${Math.round((live?.confidence || 0) * 100)}%`} />
            </div>

            {/* Vibe Credits panel */}
            <div className="space-y-3 rounded-xl2 border border-white/10 bg-white/[0.02] p-4" data-testid="inspector-credits-panel">
              <div className="flex items-center justify-between">
                <h4 className="text-[11px] uppercase tracking-[0.28em] text-primary-glow">Vibe Credits</h4>
                <Chip tone="amber"><Coins size={10} /> {offersQ.data?.length ?? 0} offers</Chip>
              </div>
              <Trajectory data={trajQ.data ?? []} />
              {(offersQ.data ?? []).slice(0, 3).map((o) => (
                <div key={o.id} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.02] px-3 py-2 text-xs">
                  <span className="truncate text-white/85">{o.name}</span>
                  <span className={cn("font-mono", o.active ? "text-glow-aqua" : "text-white/35")}>{o.cost_credits}c</span>
                </div>
              ))}
              {(offersQ.data ?? []).length === 0 && (
                <p className="text-[11px] text-white/45">No offers — add one in the Credits tab.</p>
              )}
              <p className="text-[10px] uppercase tracking-[0.22em] text-white/45">
                {redemptionsQ.data?.length ?? 0} redemptions (last 10)
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between gap-3 border-t border-white/10 px-5 py-4">
          <Button variant="ghost" size="sm" onClick={() => refresh.mutate()} loading={refresh.isPending}>
            Refresh signals
          </Button>
          <div className="flex gap-3">
            <Button variant="secondary" onClick={onClose}>Cancel</Button>
            <Button variant="pink" loading={save.isPending} onClick={() => save.mutate()}>
              Save
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

function Intel({ label, icon, value, tone, sub }: { label: string; icon?: React.ReactNode; value: string; tone?: string; sub?: string }) {
  return (
    <div>
      <p className="text-[10px] uppercase tracking-[0.22em] text-white/45">{label}</p>
      <p className={cn("mt-0.5 flex items-center gap-1.5 font-semibold", tone)}>
        {icon} {value}
      </p>
      {sub && <p className="mt-0.5 text-[10px] text-white/45 line-clamp-2">{sub}</p>}
    </div>
  );
}

function Trajectory({ data }: { data: { timestamp: string; vibe_score: number }[] }) {
  if (!data.length) {
    return <p className="text-[10px] text-white/45">No trajectory yet — awaiting first snapshot.</p>;
  }
  const w = 220, h = 38, pad = 2;
  const xs = data.map((_, i) => (i / Math.max(1, data.length - 1)) * (w - pad * 2) + pad);
  const ys = data.map((d) => h - pad - (Math.max(0, Math.min(10, d.vibe_score)) / 10) * (h - pad * 2));
  const path = xs.map((x, i) => `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${ys[i].toFixed(1)}`).join(" ");
  return (
    <div>
      <div className="mb-1 flex items-center justify-between text-[10px] uppercase tracking-[0.22em] text-white/45">
        <span>6h vibe trajectory</span>
        <span className="font-mono text-primary-glow">{data[data.length - 1].vibe_score.toFixed(2)}</span>
      </div>
      <svg viewBox={`0 0 ${w} ${h}`} className="h-10 w-full">
        <path d={path} fill="none" stroke="#B15CFF" strokeWidth={1.5} />
      </svg>
    </div>
  );
}
