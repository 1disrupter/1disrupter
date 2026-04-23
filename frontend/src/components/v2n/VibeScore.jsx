import React from "react";
import { cx } from "@/lib/cx";

/** Big vibe score number with coloured label ring. */
export function VibeScoreBadge({ score = 0, size = "md", className }) {
  const n = Number(score).toFixed(1);
  const sizes = {
    sm: "text-2xl",
    md: "text-4xl",
    lg: "text-6xl",
  };
  return (
    <div data-testid="vibe-score" className={cx("flex flex-col items-end leading-none", className)}>
      <span
        className={cx(
          "font-display font-bold bg-gradient-to-br from-white to-primary-glow bg-clip-text text-transparent",
          sizes[size]
        )}
        style={{ WebkitTextStroke: "0.5px rgba(255,255,255,0.15)" }}
      >
        {n}
      </span>
      <span className="mt-1 text-[10px] tracking-[0.28em] text-white/50 uppercase">Vibe Score</span>
    </div>
  );
}

/** Status indicator: busy / medium / dead / packed */
const statusMap = {
  busy: { label: "Busy", dot: "bg-status-busy shadow-neonAmber", text: "text-white" },
  packed: { label: "Packed", dot: "bg-accent-pink shadow-neonPink", text: "text-white" },
  medium: { label: "Medium", dot: "bg-status-medium", text: "text-white" },
  dead: { label: "Dead", dot: "bg-status-dead", text: "text-white/70" },
  locals: { label: "Locals", dot: "bg-glow-aqua shadow-neonAqua", text: "text-white" },
};

export function StatusIndicator({ status = "medium", label, icon, size = "md", className }) {
  const s = statusMap[status] || statusMap.medium;
  const sz = size === "sm" ? "text-[11px]" : "text-xs";
  return (
    <span
      data-testid={`status-${status}`}
      className={cx("inline-flex items-center gap-2 font-medium", sz, s.text, className)}
    >
      {icon ? (
        <span className="opacity-90">{icon}</span>
      ) : (
        <span className={cx("h-2 w-2 rounded-full", s.dot)} />
      )}
      <span className="uppercase tracking-widest">{label || s.label}</span>
    </span>
  );
}
