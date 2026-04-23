import React from "react";
import { Pressable, Text, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, radius } from "@/theme";
import type { VibeFilter } from "@/lib/api";

const TABS: { key: VibeFilter; label: string }[] = [
  { key: "all", label: "All" },
  { key: "bar", label: "Bars" },
  { key: "club", label: "Clubs" },
  { key: "live_music", label: "Live Music" },
];

export function CategoryTabs({
  value, onChange,
}: { value: VibeFilter; onChange: (v: VibeFilter) => void }) {
  return (
    <View
      style={{
        flexDirection: "row",
        backgroundColor: "rgba(255,255,255,0.04)",
        borderRadius: radius.pill,
        padding: 4,
        borderWidth: 1,
        borderColor: colors.border,
      }}
    >
      {TABS.map((t) => {
        const active = value === t.key;
        const Wrapper: any = active ? LinearGradient : View;
        const extra = active
          ? { colors: [colors.primary, colors.primaryGlow], start: { x: 0, y: 0 }, end: { x: 1, y: 1 } }
          : {};
        return (
          <Pressable
            key={t.key}
            onPress={() => onChange(t.key)}
            style={{ flex: 1 }}
            testID={`tab-${t.key}`}
          >
            <Wrapper
              {...extra}
              style={{
                paddingVertical: 9,
                alignItems: "center",
                borderRadius: radius.pill,
              }}
            >
              <Text
                style={{
                  color: active ? "#fff" : colors.textMuted,
                  fontWeight: "700",
                  fontSize: 12,
                  letterSpacing: 1,
                  textTransform: "uppercase",
                }}
              >
                {t.label}
              </Text>
            </Wrapper>
          </Pressable>
        );
      })}
    </View>
  );
}
