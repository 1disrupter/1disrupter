import React from "react";
import { Linking, ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { colors, radius, spacing } from "@/theme";
import { API_BASE } from "@/config";
import { Logo, LogoPin } from "@/components/Logo";
import { GlowButton } from "@/components/GlowButton";

export default function SettingsScreen() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: spacing.md }}>
        <View style={{ alignItems: "center", marginTop: spacing.lg, gap: 12 }}>
          <LogoPin size={56} />
          <Logo size={32} />
          <Text style={styles.tag}>Find the vibe. <Text style={{ color: colors.pink }}>Go tonight.</Text></Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionLabel}>About</Text>
          <Text style={styles.body}>
            Vibe2Nite ranks bars, clubs and live-music spots in real time using a
            weighted Vibe Score. No guessing — just the three best places around you,
            tuned minute-by-minute by our Signal Engine.
          </Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Backend</Text>
          <Text style={[styles.body, { fontFamily: "Courier" }]}>{API_BASE}</Text>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Links</Text>
          <GlowButton
            label="Open API Docs"
            variant="secondary"
            size="md"
            style={{ marginTop: spacing.sm }}
            onPress={() => Linking.openURL(`${API_BASE}/api/docs`)}
          />
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Legal</Text>
          <Text style={styles.body}>Privacy Policy · Terms of Service · Contact</Text>
          <Text style={[styles.body, { color: colors.textFaint, marginTop: spacing.xs }]}>
            (placeholder — add real links when live)
          </Text>
        </View>

        <Text style={{ textAlign: "center", color: colors.textFaint, marginTop: spacing.xl }}>
          v1.0.0 · © Vibe2Nite
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  tag: { color: colors.textMuted, letterSpacing: 3, textTransform: "uppercase", fontSize: 11 },
  card: {
    marginTop: spacing.lg,
    padding: spacing.md,
    backgroundColor: colors.card,
    borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border,
  },
  sectionLabel: { color: colors.primaryGlow, fontSize: 10, letterSpacing: 2.5, textTransform: "uppercase" },
  body: { color: colors.text, marginTop: 6, lineHeight: 20 },
});
