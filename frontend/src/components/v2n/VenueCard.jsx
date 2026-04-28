import React from "react";
import { motion } from "framer-motion";
import { Users, Music2, Footprints, Share2 } from "lucide-react";
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
export function VenueHeroCard({ slot, data, onGo, onShare, index = 0, className }) {
  const venue = data?.venue;
  const cfg = bannerMap[slot] || bannerMap.best_overall;

  return (
    <div
      className={cx(
        "rounded-xl overflow-hidden border bg-black/20 backdrop-blur-md",
        cfg.border,
        cfg.glow,
        className
      )}
    >
      {/* Banner */}
      <BannerChip tone={cfg.tone}>{cfg.label}</BannerChip>

      {/* Hero Image */}
      <div className="relative aspect-video w-full overflow-hidden">
        <img
          src={HERO_IMAGE[slot]}
          alt={venue?.name}
          className="h-full w-full object-cover"
        />
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Title + Score */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-white">{venue?.name}</h3>
          <VibeScoreBadge score={data?.score} className={cfg.score} />
        </div>

        {/* Distance + Status */}
        <div className="flex items-center justify-between text-sm text-white/70">
          <div className="flex items-center gap-1">
            <Footprints size={14} />
            <span>{minutesAway(data?.distance_km)}</span>
          </div>
          <StatusIndicator status={statusForScore(data?.score)} />
        </div>

        {/* Tags */}
        <div className="flex items-center gap-2 text-xs">
          <Chip icon={<Users size={12} />}>{data?.crowd || "Busy"}</Chip>
          <Chip icon={<Music2 size={12} />}>{data?.music || "Live DJ"}</Chip>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-2">
          {onShare && (
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                onShare(data);
              }}
              data-testid={`share-${slot}`}
              aria-label={`Share ${venue?.name}`}
              title="Share this vibe"
              className={cx(
                "inline-flex h-8 w-8 items-center justify-center rounded-full border border-white/10 bg-white/[0.04] text-white/70",
                "transition hover:scale-105 hover:bg-white/10 hover:text-white active:scale-95"
              )}
            >
              <Share2 size={14} />
            </button>
          )}

          <Button
            size="sm"
            variant={cfg.button}
            data-testid={`go-here-${slot}`}
            onClick={() => onGo?.(data)}
          >
            Go here
          </Button>
        </div>
      </div>
    </div>
  );
}
