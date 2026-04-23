import React from "react";
import { motion } from "framer-motion";
import { Users, Music2, Sparkles, MapPin } from "lucide-react";
import { cx } from "@/lib/cx";
import { BannerChip, Chip } from "./Chip";
import { VibeScoreBadge, StatusIndicator } from "./VibeScore";
import { Button } from "./Button";

const bannerMap = {
  best_overall: { label: "BEST OVERALL", tone: "purple", ring: "ring-primary-glow/40", glow: "shadow-softPurple" },
  live_music: { label: "LIVE MUSIC", tone: "pink", ring: "ring-accent-pink/40", glow: "shadow-[0_20px_60px_-20px_rgba(255,46,196,0.55)]" },
  hidden_gem: { label: "HIDDEN GEM", tone: "aqua", ring: "ring-glow-aqua/40", glow: "shadow-[0_20px_60px_-20px_rgba(0,245,255,0.5)]" },
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
 * Hero venue card matching the VIBE2NITE promo:
 *  [BANNER]
 *  [hero image]
 *  Venue title · walking time        [VIBE SCORE]
 *  [status] [category chip]           [GO HERE]
 */
export function VenueHeroCard({ slot, data, onGo, index = 0, className }) {
  if (!data) return null;
  const { venue, vibe, distance_km } = data;
  const cfg = bannerMap[slot] ?? bannerMap.best_overall;
  const img = HERO_IMAGE[slot];
  const status = statusForScore(vibe.vibe_score);
  const catLabel = {
    club: "Live DJ",
    bar: "Chill Vibes",
    live_music: "Live Band",
  }[venue.category] || "Venue";

  return (
    <motion.article
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: index * 0.08, ease: [0.2, 0.8, 0.2, 1] }}
      data-testid={`venue-card-${slot}`}
      className={cx(
        "relative overflow-hidden rounded-xl2 bg-background-dark/80 border border-white/10",
        "ring-1", cfg.ring, cfg.glow,
        className
      )}
    >
      {/* Hero image */}
      <div className="relative aspect-[16/9] w-full overflow-hidden">
        <img
          src={img}
          alt={venue.name}
          className="h-full w-full object-cover opacity-80"
          loading="lazy"
        />
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-transparent via-background-dark/10 to-background-dark" />
        <div className="absolute left-4 top-4">
          <BannerChip label={cfg.label} tone={cfg.tone} />
        </div>
      </div>

      {/* Body */}
      <div className="flex items-start justify-between gap-3 p-5">
        <div className="min-w-0 flex-1">
          <h3 className="font-display text-2xl tracking-wider text-white truncate">
            {venue.name.toUpperCase()}
          </h3>
          <p className="mt-1 flex items-center gap-1.5 text-xs text-white/55">
            <MapPin size={12} className="text-primary-glow" />
            <span>{minutesAway(distance_km) || `${distance_km?.toFixed(1) ?? "?"} km away`}</span>
          </p>

          <div className="mt-3 flex flex-wrap items-center gap-3">
            <StatusIndicator status={status} icon={<Users size={14} />} />
            <StatusIndicator status="locals" icon={<Music2 size={14} />} label={catLabel} />
          </div>
        </div>

        <VibeScoreBadge score={vibe.vibe_score} size="md" />
      </div>

      {/* Footer CTA */}
      <div className="flex items-center justify-between border-t border-white/5 px-5 py-3">
        <div className="flex items-center gap-2 text-[11px] text-white/40 uppercase tracking-[0.22em]">
          <Sparkles size={12} className="text-primary-glow" />
          <span>Updated moments ago</span>
        </div>
        <Button
          size="sm"
          variant={cfg.tone === "aqua" ? "aqua" : cfg.tone === "pink" ? "pink" : "primary"}
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
