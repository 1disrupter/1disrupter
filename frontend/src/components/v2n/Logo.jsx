import React from "react";
import { cx } from "@/lib/cx";

/**
 * VIBE2NITE wordmark — white text with gradient "2".
 * Variants: default (white), light, dark (purple "V2N"), icon (pin only).
 */
export function Logo({ size = "md", variant = "default", className, ...rest }) {
  const sizes = {
    xs: "text-xl",
    sm: "text-2xl",
    md: "text-4xl",
    lg: "text-6xl md:text-7xl",
    xl: "text-7xl md:text-8xl",
  };
  const base = "v2n-wordmark select-none inline-flex items-center";
  const colors = variant === "dark"
    ? "text-[#05050A]"
    : "text-white";
  return (
    <span
      data-testid="v2n-logo"
      className={cx(base, sizes[size], colors, className)}
      {...rest}
    >
      VIBE<span className="digit">2</span>NITE
    </span>
  );
}

/** Location-pin with V mark — icon logo */
export function LogoMark({ size = 28, className }) {
  return (
    <svg
      data-testid="v2n-logomark"
      viewBox="0 0 64 64"
      width={size}
      height={size}
      className={cx("drop-shadow-[0_0_14px_rgba(177,92,255,0.75)]", className)}
      aria-hidden
    >
      <defs>
        <linearGradient id="v2nPin" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#B15CFF" />
          <stop offset="1" stopColor="#FF2EC4" />
        </linearGradient>
      </defs>
      <path
        d="M32 4c-11 0-20 9-20 20 0 14 20 36 20 36s20-22 20-36c0-11-9-20-20-20z"
        fill="url(#v2nPin)"
      />
      <text
        x="32"
        y="34"
        fontFamily="Bebas Neue, Arial Black, sans-serif"
        fontSize="26"
        textAnchor="middle"
        fill="white"
      >
        V
      </text>
    </svg>
  );
}
