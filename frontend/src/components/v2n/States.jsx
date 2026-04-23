import React from "react";
import { motion } from "framer-motion";
import { MapPin, AlertTriangle, Compass, Sparkles } from "lucide-react";
import { cx } from "@/lib/cx";
import { LogoMark } from "./Logo";
import { Button } from "./Button";

/** Full-page neon loader. */
export function LoadingScreen({ label = "Finding tonight's vibe…" }) {
  return (
    <div
      data-testid="loading-screen"
      className="relative flex min-h-[60vh] flex-col items-center justify-center gap-6 py-12 v2n-noise"
    >
      <motion.div
        animate={{ scale: [1, 1.05, 1], rotate: [0, 3, -3, 0] }}
        transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
      >
        <LogoMark size={72} />
      </motion.div>
      <p className="font-display text-xl tracking-[0.3em] text-white/70">
        {label.toUpperCase()}
      </p>
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            className="h-2 w-2 rounded-full bg-primary-glow"
            animate={{ opacity: [0.2, 1, 0.2] }}
            transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.18 }}
          />
        ))}
      </div>
    </div>
  );
}

/** Inline skeleton card. */
export function VenueCardSkeleton({ className }) {
  return (
    <div
      data-testid="venue-skeleton"
      className={cx(
        "overflow-hidden rounded-xl2 border border-white/10 bg-white/[0.02]",
        className
      )}
    >
      <div className="aspect-[16/9] w-full animate-pulse bg-gradient-to-br from-primary/20 via-accent-pink/10 to-glow-aqua/10" />
      <div className="space-y-3 p-5">
        <div className="h-6 w-2/3 animate-pulse rounded bg-white/10" />
        <div className="h-3 w-1/3 animate-pulse rounded bg-white/5" />
        <div className="flex gap-2">
          <div className="h-5 w-16 animate-pulse rounded-full bg-white/5" />
          <div className="h-5 w-20 animate-pulse rounded-full bg-white/5" />
        </div>
      </div>
    </div>
  );
}

/** Empty state. */
export function EmptyState({ title = "No vibes here yet", hint = "Try expanding your radius or check back later.", actionLabel, onAction, icon }) {
  return (
    <div
      data-testid="empty-state"
      className="relative flex flex-col items-center gap-3 rounded-xl3 border border-dashed border-white/15 bg-white/[0.02] px-6 py-14 text-center"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full border border-primary-glow/40 bg-primary/10 text-primary-glow">
        {icon || <Compass size={22} />}
      </div>
      <h4 className="font-display text-2xl tracking-wider text-white">{title}</h4>
      <p className="max-w-sm text-sm text-white/55">{hint}</p>
      {actionLabel && (
        <Button variant="secondary" size="sm" onClick={onAction} className="mt-2">
          {actionLabel}
        </Button>
      )}
    </div>
  );
}

/** Error state. */
export function ErrorState({ title = "Something went sideways", message, onRetry }) {
  return (
    <div
      data-testid="error-state"
      className="flex flex-col items-center gap-3 rounded-xl3 border border-accent-pink/30 bg-accent-pink/5 px-6 py-12 text-center"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-full border border-accent-pink/60 bg-accent-pink/10 text-accent-pink">
        <AlertTriangle size={22} />
      </div>
      <h4 className="font-display text-2xl tracking-wider text-white">{title}</h4>
      {message && <p className="max-w-sm text-sm text-white/60">{message}</p>}
      {onRetry && (
        <Button variant="pink" size="sm" onClick={onRetry}>
          Try again
        </Button>
      )}
    </div>
  );
}

/** Pagination (simple). */
export function Pagination({ page = 1, totalPages = 1, onChange, className }) {
  const canPrev = page > 1;
  const canNext = page < totalPages;
  return (
    <div className={cx("flex items-center justify-center gap-2", className)} data-testid="pagination">
      <Button variant="secondary" size="sm" disabled={!canPrev} onClick={() => onChange?.(page - 1)}>
        Prev
      </Button>
      <span className="text-xs uppercase tracking-[0.22em] text-white/60">
        Page <span className="text-white">{page}</span> / {totalPages}
      </span>
      <Button variant="secondary" size="sm" disabled={!canNext} onClick={() => onChange?.(page + 1)}>
        Next
      </Button>
    </div>
  );
}

/** A simple map-pin glyph for list previews. */
export function MapPinIcon({ tone = "purple", className, size = 32 }) {
  const color = {
    purple: "#B15CFF",
    pink: "#FF2EC4",
    aqua: "#00F5FF",
    amber: "#FF9A1F",
  }[tone] || "#B15CFF";
  return (
    <span
      data-testid="map-pin"
      style={{ color }}
      className={cx("inline-flex drop-shadow-[0_0_12px_currentColor]", className)}
    >
      <MapPin size={size} />
    </span>
  );
}

/** Sparkle divider. */
export function SectionDivider({ label }) {
  return (
    <div className="my-10 flex items-center gap-3">
      <div className="h-px flex-1 bg-gradient-to-r from-transparent via-primary-glow/40 to-transparent" />
      {label && (
        <span className="flex items-center gap-1.5 text-[11px] uppercase tracking-[0.28em] text-white/55">
          <Sparkles size={12} className="text-primary-glow" />
          {label}
        </span>
      )}
      <div className="h-px flex-1 bg-gradient-to-r from-transparent via-primary-glow/40 to-transparent" />
    </div>
  );
}
