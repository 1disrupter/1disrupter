import React from "react";
import { Search } from "lucide-react";
import { cx } from "@/lib/cx";

export const Input = React.forwardRef(function Input(
  { label, hint, error, leftIcon, rightIcon, className, "data-testid": testId, ...rest },
  ref
) {
  return (
    <label className="block" data-testid={testId ? `${testId}-wrap` : undefined}>
      {label && (
        <span className="mb-1.5 block text-[11px] uppercase tracking-[0.22em] text-white/55">
          {label}
        </span>
      )}
      <span
        className={cx(
          "flex items-center gap-2 rounded-xl border bg-[#0f0a1a] px-3.5 py-2.5",
          error
            ? "border-accent-pink/70 shadow-[0_0_0_3px_rgba(255,46,196,0.12)]"
            : "border-white/10 focus-within:border-primary-glow/70 focus-within:shadow-[0_0_0_3px_rgba(177,92,255,0.15)]",
          "transition"
        )}
      >
        {leftIcon && <span className="text-white/50">{leftIcon}</span>}
        <input
          ref={ref}
          data-testid={testId}
          className={cx(
            "w-full bg-transparent text-sm text-white outline-none placeholder:text-white/35",
            className
          )}
          {...rest}
        />
        {rightIcon && <span className="text-white/50">{rightIcon}</span>}
      </span>
      {hint && !error && <span className="mt-1 block text-xs text-white/45">{hint}</span>}
      {error && <span className="mt-1 block text-xs text-accent-pink">{error}</span>}
    </label>
  );
});

export function SearchBar({ value, onChange, placeholder = "Search venues, vibes, music…", className, onSubmit }) {
  return (
    <form
      onSubmit={(e) => { e.preventDefault(); onSubmit?.(value); }}
      className={cx(
        "flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2.5",
        "focus-within:border-primary-glow/60 focus-within:shadow-[0_0_0_3px_rgba(177,92,255,0.18)]",
        className
      )}
    >
      <Search size={16} className="text-primary-glow" />
      <input
        className="w-full bg-transparent text-sm text-white outline-none placeholder:text-white/40"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        data-testid="search-input"
      />
    </form>
  );
}

export function Select({ label, options = [], value, onChange, className, ...rest }) {
  return (
    <label className="block">
      {label && (
        <span className="mb-1.5 block text-[11px] uppercase tracking-[0.22em] text-white/55">
          {label}
        </span>
      )}
      <select
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        className={cx(
          "w-full rounded-xl border border-white/10 bg-[#0f0a1a] px-3.5 py-2.5 text-sm text-white outline-none",
          "focus:border-primary-glow/70 focus:shadow-[0_0_0_3px_rgba(177,92,255,0.15)]",
          className
        )}
        {...rest}
      >
        {options.map((o) => (
          <option key={o.value ?? o} value={o.value ?? o} className="bg-background-dark">
            {o.label ?? o}
          </option>
        ))}
      </select>
    </label>
  );
}

export function Slider({ label, min = 0, max = 10, step = 0.1, value = 0, onChange, valueLabel, className }) {
  return (
    <label className={cx("block", className)}>
      <span className="mb-1 flex items-center justify-between text-[11px] uppercase tracking-[0.22em] text-white/55">
        <span>{label}</span>
        <span className="font-mono text-primary-glow">{valueLabel ?? Number(value).toFixed(2)}</span>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange?.(Number(e.target.value))}
        className="v2n-range w-full accent-[#B15CFF]"
      />
    </label>
  );
}
