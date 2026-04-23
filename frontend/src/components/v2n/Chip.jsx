import React from "react";
import { cx } from "@/lib/cx";

/** Pill-shaped category chip. */
const tones = {
  purple: "border-primary-glow/60 bg-primary/20 text-white",
  pink: "border-accent-pink/60 bg-accent-pink/20 text-white",
  aqua: "border-glow-aqua/60 bg-glow-aqua/15 text-white",
  amber: "border-status-busy/60 bg-status-busy/15 text-white",
  lavender: "border-status-medium/60 bg-status-medium/15 text-white",
  neutral: "border-white/15 bg-white/5 text-white/85",
};

export function Chip({ tone = "neutral", size = "md", icon, children, className, ...rest }) {
  const sz = size === "sm" ? "text-[10px] px-2.5 py-1" : "text-xs px-3 py-1.5";
  return (
    <span
      className={cx(
        "inline-flex items-center gap-1.5 rounded-full border uppercase tracking-[0.18em] font-semibold",
        sz,
        tones[tone],
        className
      )}
      {...rest}
    >
      {icon ? <span className="opacity-90">{icon}</span> : null}
      {children}
    </span>
  );
}

/** Banner chip used on cards (BEST OVERALL / LIVE MUSIC / HIDDEN GEM). */
export function BannerChip({ label, tone = "purple", className, ...rest }) {
  const bg = {
    purple: "bg-gradient-to-r from-primary to-primary-glow text-white shadow-neonPurple",
    pink: "bg-gradient-to-r from-accent-pink to-accent-magenta text-white shadow-neonPink",
    aqua: "bg-gradient-to-r from-glow-aqua to-glow-teal text-[#05050A] shadow-neonAqua",
  }[tone];
  return (
    <span
      className={cx(
        "inline-flex items-center rounded-full px-3.5 py-1 text-[11px] font-black uppercase tracking-[0.22em]",
        bg,
        className
      )}
      {...rest}
    >
      {label}
    </span>
  );
}
