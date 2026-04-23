import React from "react";
import { View, Text } from "react-native";
import { colors } from "@/theme";

export function VibeScoreBadge({
  score, size = "md",
}: { score: number; size?: "sm" | "md" | "lg" }) {
  const fontSize = size === "sm" ? 20 : size === "lg" ? 44 : 32;
  return (
    <View style={{ alignItems: "flex-end" }}>
      <Text
        style={{
          fontSize,
          fontWeight: "900",
          color: colors.text,
          letterSpacing: 1,
          textShadowColor: colors.primaryGlow,
          textShadowRadius: 8,
          textShadowOffset: { width: 0, height: 0 },
        }}
      >
        {Number(score ?? 0).toFixed(1)}
      </Text>
      <Text
        style={{
          color: colors.textFaint,
          fontSize: 9,
          letterSpacing: 2,
          marginTop: 2,
          textTransform: "uppercase",
        }}
      >
        Vibe Score
      </Text>
    </View>
  );
}

export function CrowdDot({ score }: { score: number }) {
  let label = "Dead";
  let color: string = colors.dead;
  if (score >= 8.5) { label = "Packed"; color = colors.pink; }
  else if (score >= 8) { label = "Busy"; color = colors.amber; }
  else if (score >= 5) { label = "Medium"; color = colors.lavender; }
  return (
    <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
      <View
        style={{
          width: 8, height: 8, borderRadius: 4, backgroundColor: color,
          shadowColor: color, shadowOpacity: 0.9, shadowRadius: 8, shadowOffset: { width: 0, height: 0 },
        }}
      />
      <Text style={{ color: colors.text, fontSize: 11, letterSpacing: 1.8, textTransform: "uppercase" }}>
        {label}
      </Text>
    </View>
  );
}

/** Placeholder sparkline — 12 bars of decreasing random heights. */
export function Sparkline({
  values, color = colors.primaryGlow, width = 80, height = 22,
}: { values?: number[]; color?: string; width?: number; height?: number }) {
  const v = values && values.length ? values : [3, 4, 4.5, 5, 6, 5.5, 7, 7.5, 8, 7, 8.5, 9];
  const max = Math.max(...v, 1);
  return (
    <View
      style={{
        flexDirection: "row", alignItems: "flex-end",
        width, height, gap: 2,
      }}
    >
      {v.map((n, i) => (
        <View
          key={i}
          style={{
            flex: 1,
            height: Math.max(2, (n / max) * height),
            backgroundColor: color,
            opacity: 0.35 + (i / v.length) * 0.65,
            borderRadius: 1,
          }}
        />
      ))}
    </View>
  );
}
