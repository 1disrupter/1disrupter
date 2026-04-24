/**
 * BrandKitScreen — read-only Brand Kit viewer for mobile admin mode.
 * Mirrors the CRA + Next.js versions: colours, typography, spacing, effects.
 * All values come from the shared theme module so they stay in sync.
 */
import React from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors, radius, shadow, spacing } from "@/theme";

const COLOR_TOKENS: Array<[string, string, string]> = [
  ["Primary / Neon Purple", colors.primary, "primary"],
  ["Primary / Glow Purple", colors.primaryGlow, "primaryGlow"],
  ["Accent / Electric Pink", colors.pink, "pink"],
  ["Accent / Magenta", colors.magenta, "magenta"],
  ["Glow / Aqua", colors.aqua, "aqua"],
  ["Glow / Teal", colors.teal, "teal"],
  ["Background / Midnight", colors.bgAlt, "bgAlt"],
  ["Background / Deep", colors.bg, "bg"],
  ["Status / Busy (Amber)", colors.amber, "amber"],
  ["Status / Medium (Lavender)", colors.lavender, "lavender"],
  ["Status / Dead (Grey)", colors.dead, "dead"],
];

const SPACES = [
  ["xxs", spacing.xxs],
  ["xs", spacing.xs],
  ["sm", spacing.sm],
  ["md", spacing.md],
  ["lg", spacing.lg],
  ["xl", spacing.xl],
  ["xxl", spacing.xxl],
] as const;

const RADII = [
  ["sm", radius.sm],
  ["md", radius.md],
  ["lg", radius.lg],
  ["xl", radius.xl],
  ["pill", 24], // preview-only, actual pill value is 999
] as const;

const SHADOWS: Array<[string, any]> = [
  ["neonPurple", shadow.neonPurple],
  ["neonPink", shadow.neonPink],
  ["neonAqua", shadow.neonAqua],
];

export default function BrandKitScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: spacing.md, paddingBottom: spacing.xxl }}>
        <Text style={styles.kicker}>The Brand Kit</Text>
        <Text style={styles.title}>VIBE<Text style={{ color: colors.pink }}>2</Text>NITE</Text>
        <Text style={styles.tag}>
          Find the vibe. <Text style={{ color: colors.pink }}>Go tonight.</Text>
        </Text>

        {/* Colours */}
        <SectionHeader kicker="01 — tokens" title="COLOUR STYLES" />
        <View style={styles.grid}>
          {COLOR_TOKENS.map(([n, hex, token]) => (
            <View key={token} style={styles.swatchCard} testID={`mobile-swatch-${token}`}>
              <View style={[styles.swatchBlock, { backgroundColor: hex }]} />
              <Text style={styles.swatchName}>{n}</Text>
              <Text style={styles.swatchHex}>{hex}</Text>
              <Text style={styles.swatchToken}>{token}</Text>
            </View>
          ))}
        </View>

        {/* Typography */}
        <SectionHeader kicker="02 — type" title="TYPOGRAPHY" />
        <View style={styles.card}>
          <Text style={styles.smallLabel}>Display</Text>
          <Text style={styles.displayXl}>TONIGHT.</Text>
          <Text style={styles.displayMd}>HEADLINES.</Text>
        </View>
        <View style={styles.card}>
          <Text style={styles.smallLabel}>Body</Text>
          <Text style={{ color: colors.text, fontSize: 16, marginTop: 6 }}>
            The weighted Vibe Score ranks venues live, every minute.
          </Text>
          <Text style={{ color: colors.textMuted, fontSize: 13, marginTop: 6 }}>
            Captions, labels, tabular text.
          </Text>
        </View>

        {/* Effects */}
        <SectionHeader kicker="03 — glow" title="EFFECTS" />
        <View style={styles.grid}>
          {SHADOWS.map(([name, sh]) => (
            <View
              key={name}
              testID={`mobile-shadow-${name}`}
              style={[styles.shadowCard, sh]}
            >
              <Text style={styles.shadowLabel}>{name}</Text>
            </View>
          ))}
        </View>

        {/* Spacing */}
        <SectionHeader kicker="04 — grid" title="SPACING" />
        <View style={[styles.card, { flexDirection: "row", alignItems: "flex-end", gap: 8 }]}>
          {SPACES.map(([name, val]) => (
            <View key={name} style={{ alignItems: "center", gap: 4 }}>
              <View style={{
                width: 18, height: val, backgroundColor: colors.primary,
                borderRadius: 2,
              }} />
              <Text style={styles.spaceLabel}>{val}</Text>
              <Text style={styles.spaceName}>{name}</Text>
            </View>
          ))}
        </View>

        {/* Radii */}
        <SectionHeader kicker="05 — shape" title="RADII" />
        <View style={[styles.grid, { justifyContent: "flex-start" }]}>
          {RADII.map(([name, val]) => (
            <View key={name} style={styles.radiiCard}>
              <View style={{
                width: 44, height: 44, backgroundColor: colors.primaryGlow,
                borderRadius: val as number,
              }} />
              <Text style={styles.spaceLabel}>{name}</Text>
            </View>
          ))}
        </View>

        <Text style={styles.footer}>Brand Kit · read-only · admin surface</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

function SectionHeader({ kicker, title }: { kicker: string; title: string }) {
  return (
    <View style={{ marginTop: spacing.xl, marginBottom: spacing.sm }}>
      <Text style={styles.kicker}>{kicker}</Text>
      <Text style={styles.sectionTitle}>{title}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  kicker: { color: colors.primaryGlow, fontSize: 10, letterSpacing: 3, textTransform: "uppercase" },
  title: { color: colors.text, fontSize: 42, fontWeight: "900", letterSpacing: 3, marginTop: 4 },
  sectionTitle: { color: colors.text, fontSize: 22, fontWeight: "900", letterSpacing: 2, marginTop: 2 },
  tag: { color: colors.textMuted, marginTop: 4, letterSpacing: 2, textTransform: "uppercase", fontSize: 11 },
  grid: {
    flexDirection: "row", flexWrap: "wrap", gap: 10, marginTop: spacing.sm,
  },
  swatchCard: {
    width: "31%",
    padding: 10,
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border,
  },
  swatchBlock: {
    height: 44, borderRadius: radius.md,
    borderWidth: 1, borderColor: "rgba(255,255,255,0.08)",
  },
  swatchName: { color: colors.textMuted, fontSize: 9, letterSpacing: 1.5, textTransform: "uppercase", marginTop: 6 },
  swatchHex: { color: colors.text, fontFamily: "Courier", fontSize: 11, marginTop: 2 },
  swatchToken: { color: colors.primaryGlow, fontSize: 9, marginTop: 2 },
  card: {
    marginTop: spacing.sm, padding: spacing.md,
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border,
  },
  smallLabel: { color: colors.textMuted, fontSize: 10, letterSpacing: 2, textTransform: "uppercase" },
  displayXl: { color: colors.text, fontSize: 52, fontWeight: "900", letterSpacing: 3, marginTop: 4 },
  displayMd: { color: colors.primaryGlow, fontSize: 28, fontWeight: "900", letterSpacing: 2, marginTop: 2 },
  shadowCard: {
    width: "31%", height: 72,
    borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border,
    backgroundColor: colors.card,
    alignItems: "center", justifyContent: "center",
  },
  shadowLabel: { color: colors.text, fontSize: 10, letterSpacing: 1.5, textTransform: "uppercase" },
  spaceLabel: { color: colors.textFaint, fontSize: 9, marginTop: 4 },
  spaceName: { color: colors.primaryGlow, fontSize: 9, letterSpacing: 1, textTransform: "uppercase" },
  radiiCard: {
    padding: 10, alignItems: "center",
    backgroundColor: colors.card,
    borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border,
    width: 72,
  },
  footer: {
    textAlign: "center", color: colors.textFaint, marginTop: spacing.xl,
    fontSize: 10, letterSpacing: 2, textTransform: "uppercase",
  },
});
