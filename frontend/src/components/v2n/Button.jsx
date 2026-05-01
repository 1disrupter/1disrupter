import React from "react";
import { cx } from "../lib/cx";

const variants = {
  primary:
    "bg-gradient-to-br from-primary to-primary-glow text-white shadow-neonPurple hover:shadow-[0_0_20px_#8A2BE2,0_0_40px_#8A2BE2]",
  pink:
    "bg-gradient-to-br from-accent-pink to-accent-magenta text-white shadow-neonPink hover:shadow-[0_0_20px_#FF2EC4,0_0_40px_#FF2EC4]",
  aqua:
    "bg-gradient-to-br from-glow-aqua to-glow-teal text-[#05050A] shadow-neonAqua hover:shadow-[0_0_20px_#00F5FF,0_0_40px_#00F5FF]",
  secondary:
    "bg-white/5 text-white border border-white/15 hover:bg-white/10 hover:border-primary-glow/70",
  ghost:
    "bg-transparent text-white/80 hover:text-white hover:bg-white/5",
  danger:
    "bg-gradient-to-br from-[#ff4d6d] to-[#ff7aa1] text-white",
};
const sizes = {
  sm: "text-xs px-3 py-1.5 rounded-full",
  md: "text-sm px-4 py-2.5 rounded-full",
  lg: "text-base px-6 py-3.5 rounded-full",
};

export const Button = React.forwardRef(function Button(
  { variant = "primary", size = "md", className, loading, disabled, children, leftIcon, rightIcon, ...rest },
  ref
) {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cx(
        "relative inline-flex items-center justify-center gap-2 font-semibold tracking-wide",
        "transition-all duration-200 active:scale-[0.97] focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-glow/60",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className
      )}
      {...rest}
    >
      {leftIcon}
      <span>{children}</span>
      {rightIcon}
      {loading && (
        <span className="absolute inset-0 flex items-center justify-center rounded-full bg-black/30 backdrop-blur-[1px]">
          <span className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />
        </span>
      )}
    </button>
  );
});

export function IconButton({ className, children, ...rest }) {
  return (
    <button
      className={cx(
        "inline-flex h-10 w-10 items-center justify-center rounded-full",
        "bg-white/5 text-white/80 border border-white/10",
        "hover:text-white hover:bg-white/10 hover:border-primary-glow/60 transition",
        className
      )}
      {...rest}
    >
      {children}
    </button>
  );
}
