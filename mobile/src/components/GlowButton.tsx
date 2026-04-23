import React from "react";
import { Pressable, Text, ActivityIndicator, View, StyleProp, ViewStyle } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, radius, shadow } from "@/theme";

type Variant = "primary" | "pink" | "aqua" | "secondary" | "ghost";
type Size = "sm" | "md" | "lg";

interface Props {
  label: string;
  onPress?: () => void;
  variant?: Variant;
  size?: Size;
  loading?: boolean;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
  leftIcon?: React.ReactNode;
  testID?: string;
}

const GRADIENTS: Record<Variant, [string, string]> = {
  primary: [colors.primary, colors.primaryGlow],
  pink: [colors.pink, colors.magenta],
  aqua: [colors.aqua, colors.teal],
  secondary: ["rgba(255,255,255,0.06)", "rgba(255,255,255,0.03)"],
  ghost: ["transparent", "transparent"],
};

const TEXT_COLOR: Record<Variant, string> = {
  primary: "#fff",
  pink: "#fff",
  aqua: "#05050A",
  secondary: colors.text,
  ghost: colors.textMuted,
};

const GLOW: Record<Variant, any> = {
  primary: shadow.neonPurple,
  pink: shadow.neonPink,
  aqua: shadow.neonAqua,
  secondary: {},
  ghost: {},
};

const PADDING: Record<Size, { px: number; py: number; fs: number }> = {
  sm: { px: 12, py: 8, fs: 12 },
  md: { px: 18, py: 12, fs: 14 },
  lg: { px: 24, py: 16, fs: 16 },
};

export function GlowButton({
  label, onPress, variant = "primary", size = "md",
  loading, disabled, style, leftIcon, testID,
}: Props) {
  const pad = PADDING[size];
  const opacity = disabled || loading ? 0.5 : 1;
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      testID={testID}
      style={({ pressed }) => [
        {
          opacity,
          transform: [{ scale: pressed ? 0.97 : 1 }],
          borderRadius: radius.pill,
          ...GLOW[variant],
        },
        style,
      ]}
    >
      <LinearGradient
        colors={GRADIENTS[variant]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={{
          borderRadius: radius.pill,
          paddingHorizontal: pad.px,
          paddingVertical: pad.py,
          borderWidth: variant === "secondary" ? 1 : 0,
          borderColor: "rgba(255,255,255,0.1)",
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
        }}
      >
        {loading ? (
          <ActivityIndicator color={TEXT_COLOR[variant]} />
        ) : (
          <>
            {leftIcon ? <View>{leftIcon}</View> : null}
            <Text style={{ color: TEXT_COLOR[variant], fontSize: pad.fs, fontWeight: "700", letterSpacing: 0.5 }}>
              {label}
            </Text>
          </>
        )}
      </LinearGradient>
    </Pressable>
  );
}
