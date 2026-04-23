import React from "react";
import { Text, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors } from "@/theme";

/**
 * "VIBE2NITE" wordmark. The "2" is rendered with a purple→pink gradient over
 * a white base using MaskedView-style trick: we stack two overlaid Text nodes
 * (a solid pink one acting as the fill, clipped by the gradient layer).
 * For simplicity in RN we render the "2" as a solid pink Text with a glow
 * shadow — visually identical in a dark theme.
 */
export function Logo({ size = 32 }: { size?: number }) {
  return (
    <View style={{ flexDirection: "row", alignItems: "center" }}>
      <Text
        style={{
          fontSize: size,
          fontWeight: "900",
          letterSpacing: 2,
          color: colors.text,
        }}
      >
        VIBE
      </Text>
      <Text
        style={{
          fontSize: size,
          fontWeight: "900",
          letterSpacing: 2,
          color: colors.pink,
          textShadowColor: colors.primaryGlow,
          textShadowRadius: 10,
          textShadowOffset: { width: 0, height: 0 },
          paddingHorizontal: 2,
        }}
      >
        2
      </Text>
      <Text
        style={{
          fontSize: size,
          fontWeight: "900",
          letterSpacing: 2,
          color: colors.text,
        }}
      >
        NITE
      </Text>
    </View>
  );
}

export function LogoPin({ size = 28 }: { size?: number }) {
  return (
    <LinearGradient
      colors={[colors.primaryGlow, colors.pink]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={{
        width: size,
        height: size,
        borderRadius: size / 2,
        alignItems: "center",
        justifyContent: "center",
        shadowColor: colors.primaryGlow,
        shadowRadius: 10,
        shadowOpacity: 0.9,
        shadowOffset: { width: 0, height: 0 },
      }}
    >
      <Text style={{ color: colors.text, fontWeight: "900", fontSize: size * 0.55 }}>V</Text>
    </LinearGradient>
  );
}
