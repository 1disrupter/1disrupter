import React from "react";
import { View, Text } from "react-native";
import { colors, radius } from "@/theme";
import type { Trend, TouristLabel } from "@/lib/api";

export function Chip({
  label, tone = "neutral", small = false,
}: { label: string; tone?: "neutral" | "purple" | "pink" | "aqua" | "amber" | "lavender"; small?: boolean }) {
  const map = {
    neutral: { bg: "rgba(255,255,255,0.05)", border: colors.border, fg: colors.text },
    purple: { bg: "rgba(138,43,226,0.22)", border: colors.primaryGlow, fg: "#fff" },
    pink: { bg: "rgba(255,46,196,0.22)", border: colors.pink, fg: "#fff" },
    aqua: { bg: "rgba(0,245,255,0.18)", border: colors.aqua, fg: "#fff" },
    amber: { bg: "rgba(255,154,31,0.20)", border: colors.amber, fg: "#fff" },
    lavender: { bg: "rgba(199,167,255,0.18)", border: colors.lavender, fg: "#fff" },
  }[tone];
  return (
    <View
      style={{
        backgroundColor: map.bg,
        borderColor: map.border,
        borderWidth: 1,
        paddingHorizontal: small ? 8 : 10,
        paddingVertical: small ? 3 : 5,
        borderRadius: radius.pill,
      }}
    >
      <Text
        style={{
          color: map.fg,
          fontSize: small ? 9 : 10,
          fontWeight: "700",
          letterSpacing: 1.5,
          textTransform: "uppercase",
        }}
      >
        {label}
      </Text>
    </View>
  );
}

const TREND_MAP: Record<Trend, { tone: "aqua" | "pink" | "neutral" | "amber"; label: string; arrow: string }> = {
  rising: { tone: "aqua", label: "Rising", arrow: "↗" },
  peaking: { tone: "pink", label: "Peaking", arrow: "⚡" },
  falling: { tone: "neutral", label: "Falling", arrow: "↘" },
  steady: { tone: "neutral", label: "Steady", arrow: "—" },
};

export function TrendBadge({ trend }: { trend: Trend }) {
  const m = TREND_MAP[trend];
  return <Chip tone={m.tone} label={`${m.arrow}  ${m.label}`} />;
}

const TOURIST_MAP: Record<TouristLabel, { tone: "amber" | "aqua" | "neutral"; label: string } | null> = {
  tourist_trap: { tone: "amber", label: "⚠ Tourist Trap" },
  local_gem: { tone: "aqua", label: "💎 Local Gem" },
  neutral: null,
};

export function TouristFlagBadge({ label }: { label: TouristLabel }) {
  const m = TOURIST_MAP[label];
  if (!m) return null;
  return <Chip tone={m.tone} label={m.label} />;
}

export function LiveMusicBadge() {
  return <Chip tone="pink" label="🎶 Live Now" />;
}
