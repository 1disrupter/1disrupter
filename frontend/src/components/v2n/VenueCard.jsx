import React from "react";
import { motion } from "framer-motion";
import { Users, Music2, Footprints } from "lucide-react";
import { cx } from "@/lib/cx";
import { BannerChip, Chip } from "./Chip";
import { VibeScoreBadge, StatusIndicator } from "./VibeScore";
import { Button } from "./Button";

const bannerMap = {
  best_overall: {
    label: "BEST OVERALL",
    tone: "purple",
    border: "border-primary-glow/55",
    glow: "shadow-[0_24px_70px_-24px_rgba(177,92,255,0.65)]",
    score: "text-primary-glow",
    button: "primary",
  },
  live_music: {
    label: "LIVE MUSIC",
    tone: "pink",
    border: "border-accent-pink/55",
    glow: "shadow-[0_24px_70px_-24px_rgba(255,46,196,0.6)]",
    score: "text-accent-pink",
    button: "pink",
  },
  hidden_gem: {
    label: "HIDDEN GEM",
    tone: "aqua",
    border: "border-glow-aqua/55",
    glow: "shadow-[0_24px_70px_-24px_rgba(0,245,255,0.55)]",
    score: "text-glow-aqua",
    button: "aqua",
  },
};

const HERO_IMAGE = {
  best_overall:
    "https://images.unsplash.com/photo-1519214605650-76a613ee3245?auto=format&fit=crop&w=1400&q=60",
  live_music:
    "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?auto=format&fit=crop&w=1400&q=60",
  hidden_gem:
    "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?auto=format&fit=crop&w=1400&q=60",
};

function minutesAway(km) {
  if (km == null) return null;
  // ~5 km/h walking speed
  const mins = Math.max(1, Math.round((km / 5) * 60));
  return `${mins} min away`;
}

function statusForScore(score) {
  if (score >= 8.5) return "packed";
  if (score >= 8) return "busy";
  if (score >= 5) return "locals";
  return "dead";
}

/**
 * Hero venue card matching the VIBE2NITE promo layout:
 *  ┌───────────────────────────────┐
 *  │ [BANNER]                       │
 *  │       hero image (16/9)        │
 *  ├───────────────────────────────┤
 *  │ TITLE                  9.2     │
 *  │ 🚶 6 min away      VIBE SCORE  │
 *  ├───────────────────────────────┤
 *  │ 👥 Busy  🎵 Live DJ    [GO HERE]│
 *  └───────────────────────────────┘
 */
export function VenueHeroCard({ slot, data, onGo, index = 0, className }) {
  if (!data) return null;
  const { venue, vibe, distance_km } = data;
  const cfg = bannerMap[slot] ?? bannerMap.best_overall;
  const img = HERO_IMAGE[slot];
  const status = statusForScore(vibe.vibe_score);
  const crowdLabel = {
    packed: "Packed",
    busy: "Busy",
    locals: "Locals",
    dead: "Quiet",
  }[status] || "Busy";
  const catLabel = {
    club: "Live DJ",
    bar: "Chill Vibes",
    live_music: "Live Band",
  }[venue.category] || "Vibes";
  const walking = minutesAway(distance_km);

  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08, ease: [0.2, 0.8, 0.2, 1] }}
      data-testid={`venue-card-${slot}`}
      className={cx(
        "relative flex flex-col overflow-hidden rounded-xl2 bg-background-deep/90",
        "border", cfg.border, cfg.glow,
        "transition-transform duration-300 hover:-translate-y-0.5",
        className
      )}
    >
      {/* Hero image */}
      <div className="relative aspect-[16/9] w-full overflow-hidden">
        <img
          src={img}
          alt={venue.name}
          className="h-full w-full object-cover"
          loading="lazy"
        />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-background-deep/10 via-background-deep/30 to-background-deep" />
        <div className="absolute left-3 top-3">
          <BannerChip label={cfg.label} tone={cfg.tone} />
        </div>
        {venue.is_verified && (
          <div
            data-testid={`verified-badge-${slot}`}
            title="Verified venue"
            className="absolute right-3 top-3 inline-flex items-center gap-1 rounded-full border border-glow-aqua/60 bg-glow-aqua/15 px-2.5 py-1 text-[10px] uppercase tracking-[0.24em] text-glow-aqua shadow-neonAqua backdrop-blur"
          >
            <svg width="10" height="10" viewBox="0 0 20 20" fill="currentColor" aria-hidden><path fillRule="evenodd" d="M10 1.944A11.953 11.953 0 012.166 5 12 12 0 0010 19 12 12 0 0017.834 5 11.953 11.953 0 0110 1.944zm4.207 6.263a.75.75 0 00-1.06-1.06l-4.147 4.146-1.646-1.646a.75.75 0 10-1.06 1.06l2.176 2.177a.75.75 0 001.06 0l4.677-4.677z" clipRule="evenodd"/></svg>
            Verified
          </div>
        )}
      </div>

      {/* Title row + big score */}
      <div className="flex items-start justify-between gap-3 px-5 pt-4">
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-xl tracking-wider text-white truncate sm:text-2xl">
            {venue.name.toUpperCase()}
          </h3>
          <p className="mt-1.5 flex items-center gap-1.5 text-[12px] text-white/65">
            <Footprints size={13} className="text-white/55" />
            <span>{walking || (distance_km != null ? `${distance_km.toFixed(1)} km away` : "Nearby")}</span>
          </p>
        </div>
        <div className="flex flex-col items-end leading-none">
          <span
            data-testid={`vibe-score-${slot}`}
            className={cx(
              "font-display text-5xl font-bold tracking-tight tabular-nums",
              cfg.score
            )}
          >
            {vibe.vibe_score.toFixed(1)}
          </span>
          <span className="mt-1 text-[10px] uppercase tracking-[0.28em] text-white/50">
            Vibe Score
          </span>
        </div>
      </div>

      {/* Footer row: crowd + music chips on the left, GO HERE button on the right */}
      <div className="mt-4 flex items-center justify-between gap-3 border-t border-white/5 px-5 py-3">
        <div className="flex items-center gap-3 text-xs text-white/75">
          <span className="inline-flex items-center gap-1.5">
            <Users size={14} className={cfg.score} />
            <span>{crowdLabel}</span>
          </span>
          <span className="text-white/20">·</span>
          <span className="inline-flex items-center gap-1.5">
            <Music2 size={14} className={cfg.score} />
            <span>{catLabel}</span>
          </span>
        </div>
        <Button
          size="sm"
          variant={cfg.button}
          data-testid={`go-here-${slot}`}
          onClick={() => onGo?.(data)}
        >
          Go here
        </Button>
      </div>
    </motion.article>
  );
}

/** Compact venue list item (for search/feed). */
export function VenueListItem({ data, onClick, className }) {
  if (!data) return null;
  const { venue, vibe, distance_km } = data;
  const status = statusForScore(vibe.vibe_score);
  return (
    <button
      onClick={() => onClick?.(data)}
      className={cx(
        "group flex w-full items-center gap-3 rounded-xl border border-white/10 bg-white/[0.02]",
        "p-3 text-left transition hover:border-primary-glow/60 hover:bg-white/[0.04]",
        className
      )}
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-gradient-to-br from-primary to-accent-pink text-white font-display text-2xl">
        {venue.name.slice(0, 1)}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <p className="truncate font-semibold text-white">{venue.name}</p>
          <Chip size="sm" tone="neutral">{venue.category.replace("_", " ")}</Chip>
        </div>
        <div className="mt-1 flex items-center gap-3 text-[11px] text-white/55">
          <StatusIndicator status={status} size="sm" />
          {distance_km != null && <span>· {distance_km.toFixed(1)} km</span>}
        </div>
      </div>
      <VibeScoreBadge score={vibe.vibe_score} size="sm" />
    </button>
  );
}
