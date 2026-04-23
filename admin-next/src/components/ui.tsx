"use client";
import * as React from "react";
import { cn } from "@/lib/cn";

type Variant = "primary" | "pink" | "aqua" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

const V: Record<Variant, string> = {
  primary: "bg-gradient-to-br from-primary to-primary-glow text-white shadow-neonPurple",
  pink: "bg-gradient-to-br from-accent-pink to-accent-magenta text-white shadow-neonPink",
  aqua: "bg-gradient-to-br from-glow-aqua to-glow-teal text-background-deep shadow-neonAqua",
  secondary: "bg-white/5 text-white border border-white/10 hover:bg-white/10 hover:border-primary-glow/60",
  ghost: "bg-transparent text-white/75 hover:text-white hover:bg-white/5",
};
const S: Record<Size, string> = {
  sm: "text-xs px-3 py-1.5",
  md: "text-sm px-4 py-2.5",
  lg: "text-base px-6 py-3.5",
};

export function Button({
  variant = "primary", size = "md", className, children, leftIcon, loading, disabled, ...rest
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant; size?: Size; leftIcon?: React.ReactNode; loading?: boolean;
}) {
  return (
    <button
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-full font-semibold tracking-wide transition-all active:scale-[0.97] disabled:opacity-50 disabled:cursor-not-allowed",
        V[variant], S[size], className
      )}
      {...rest}
    >
      {loading ? <span className="h-4 w-4 rounded-full border-2 border-current border-t-transparent animate-spin" /> : leftIcon}
      <span>{children}</span>
    </button>
  );
}

type ChipTone = "neutral" | "purple" | "pink" | "aqua" | "amber" | "lavender";
const C: Record<ChipTone, string> = {
  neutral: "border-white/15 bg-white/5 text-white/85",
  purple: "border-primary-glow/60 bg-primary/20 text-white",
  pink: "border-accent-pink/60 bg-accent-pink/20 text-white",
  aqua: "border-glow-aqua/60 bg-glow-aqua/15 text-white",
  amber: "border-status-busy/60 bg-status-busy/15 text-white",
  lavender: "border-status-medium/60 bg-status-medium/15 text-white",
};

export function Chip({ tone = "neutral", children, className }: { tone?: ChipTone; children: React.ReactNode; className?: string }) {
  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em]",
      C[tone], className
    )}>
      {children}
    </span>
  );
}

export function Input({ label, error, className, ...rest }: React.InputHTMLAttributes<HTMLInputElement> & { label?: string; error?: string }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-[11px] uppercase tracking-[0.22em] text-white/55">{label}</span>}
      <input
        className={cn(
          "w-full rounded-xl border bg-[#0f0a1a] px-3.5 py-2.5 text-sm text-white outline-none transition",
          error
            ? "border-accent-pink/70 shadow-[0_0_0_3px_rgba(255,46,196,0.12)]"
            : "border-white/10 focus:border-primary-glow/70 focus:shadow-[0_0_0_3px_rgba(177,92,255,0.15)]",
          className
        )}
        {...rest}
      />
      {error && <span className="mt-1 block text-xs text-accent-pink">{error}</span>}
    </label>
  );
}

export function Select({ label, children, className, ...rest }: React.SelectHTMLAttributes<HTMLSelectElement> & { label?: string }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-[11px] uppercase tracking-[0.22em] text-white/55">{label}</span>}
      <select
        className={cn(
          "w-full rounded-xl border border-white/10 bg-[#0f0a1a] px-3.5 py-2.5 text-sm text-white outline-none focus:border-primary-glow/70",
          className
        )}
        {...rest}
      >
        {children}
      </select>
    </label>
  );
}

export function Slider({ label, value, onChange, min = 0, max = 10, step = 0.1 }: { label: string; value: number; onChange: (v: number) => void; min?: number; max?: number; step?: number }) {
  return (
    <label className="block">
      <span className="mb-1 flex items-center justify-between text-[11px] uppercase tracking-[0.22em] text-white/55">
        <span>{label}</span>
        <span className="font-mono text-primary-glow">{Number(value).toFixed(2)}</span>
      </span>
      <input
        type="range" min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-[#B15CFF]"
      />
    </label>
  );
}
