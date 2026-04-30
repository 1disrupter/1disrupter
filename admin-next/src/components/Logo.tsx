import React from "react";
import { cn } from "../lib/cn";

export function Logo({ size = "md", className }: { size?: "sm" | "md" | "lg"; className?: string }) {
  const fs = { sm: "text-xl", md: "text-3xl", lg: "text-5xl" }[size];
  return (
    <span className={cn("font-display tracking-widest select-none inline-flex items-center", fs, className)}>
      <span className="text-white">VIBE</span>
      <span
        className="px-[2px]"
        style={{
          background: "linear-gradient(180deg, #B15CFF, #FF2EC4)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          filter: "drop-shadow(0 0 10px rgba(177,92,255,0.8))",
        }}
      >
        2
      </span>
      <span className="text-white">NITE</span>
    </span>
  );
}

export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" aria-hidden
      className="drop-shadow-[0_0_14px_rgba(177,92,255,0.8)]">
      <defs>
        <linearGradient id="v2nMark" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#B15CFF" />
          <stop offset="1" stopColor="#FF2EC4" />
        </linearGradient>
      </defs>
      <path d="M32 4c-11 0-20 9-20 20 0 14 20 36 20 36s20-22 20-36c0-11-9-20-20-20z" fill="url(#v2nMark)" />
      <text x="32" y="34" textAnchor="middle" fontFamily="Arial Black" fontSize="22" fill="white">V</text>
    </svg>
  );
}
