import React from "react";
import { Linking, ScrollView, StyleSheet, Text, View, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { RouteProp, useRoute } from "@react-navigation/native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getDirections, postFeedback, getForecastAll, getTouristFlags, getLiveMusic,
  VoteType, Top3Item, ForecastItem, TouristFlagItem, LiveMusicItem,
} from "@/lib/api";
import { colors, radius, spacing } from "@/theme";
import { DEFAULT_LOCATION } from "@/config";
import { VibeScoreBadge, CrowdDot, Sparkline } from "@/components/VibeScoreBadge";
import { Chip, LiveMusicBadge, TouristFlagBadge, TrendBadge } from "@/components/Chip";
import { GlowButton } from "@/components/GlowButton";

type RouteParams = { VenueDetail: { venue: Top3Item } };

export default function VenueDetailScreen() {
  const { params } = useRoute<RouteProp<RouteParams, "VenueDetail">>();
  const venue = params.venue;
  const qc = useQueryClient();

  const forecastQ = useQuery({ queryKey: ["forecast"], queryFn: getForecastAll });
  const touristQ = useQuery({ queryKey: ["tourist-flags"], queryFn: getTouristFlags });
  const liveQ = useQuery({ queryKey: ["live-music-all"], queryFn: () => getLiveMusic(true) });

  const forecast = forecastQ.data?.items.find((x) => x.venue_id === venue.id) as ForecastItem | undefined;
  const tourist = touristQ.data?.items.find((x) => x.venue_id === venue.id) as TouristFlagItem | undefined;
  const live = liveQ.data?.items.find((x) => x.venue_id === venue.id) as LiveMusicItem | undefined;

  const voteM = useMutation({
    mutationFn: (vote: VoteType) => postFeedback(venue.id, vote),
    onSuccess: (res) => {
      Alert.alert("Thanks!", `New vibe score: ${res.new_vibe_score.toFixed(2)}`);
      qc.invalidateQueries();
    },
    onError: (e: any) => Alert.alert("Vote failed", e?.message || "Try again"),
  });

  const go = async () => {
    try {
      const d = await getDirections(venue.id, DEFAULT_LOCATION.lat, DEFAULT_LOCATION.lng);
      await Linking.openURL(d.deeplink);
    } catch (e: any) {
      Alert.alert("No directions", e?.message || "Try again.");
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <ScrollView contentContainerStyle={{ padding: spacing.md, paddingBottom: spacing.xxl }}>
        <Text style={styles.kicker}>Venue detail</Text>
        <Text style={styles.title}>{venue.name.toUpperCase()}</Text>
        <Text style={styles.sub}>
          {venue.category.replace("_", " ")}
          {venue.distance_km != null ? ` · ${venue.distance_km.toFixed(1)} km` : ""}
        </Text>

        <View style={styles.hero}>
          <VibeScoreBadge score={forecast?.current_vibe_score ?? venue.vibe_score} size="lg" />
          <View style={{ flex: 1, marginLeft: spacing.md, gap: 8 }}>
            <CrowdDot score={venue.vibe_score} />
            {forecast && <TrendBadge trend={forecast.trend} />}
            {live?.live_music && <LiveMusicBadge />}
            {tourist && <TouristFlagBadge label={tourist.label} />}
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Trajectory (placeholder)</Text>
          <Sparkline width={280} height={38} />
        </View>

        <GlowButton
          label="Go here now"
          variant="primary"
          size="lg"
          onPress={go}
          style={{ marginTop: spacing.md }}
        />

        <Text style={[styles.sectionLabel, { marginTop: spacing.lg }]}>
          What's the vibe right now?
        </Text>
        <View style={{ flexDirection: "row", gap: 10, marginTop: spacing.sm }}>
          <GlowButton
            label="Busy"
            variant="primary"
            size="md"
            onPress={() => voteM.mutate("busy")}
            loading={voteM.isPending && voteM.variables === "busy"}
            style={{ flex: 1 }}
            testID="vote-busy"
          />
          <GlowButton
            label="Good"
            variant="pink"
            size="md"
            onPress={() => voteM.mutate("good")}
            loading={voteM.isPending && voteM.variables === "good"}
            style={{ flex: 1 }}
            testID="vote-good"
          />
          <GlowButton
            label="Dead"
            variant="secondary"
            size="md"
            onPress={() => voteM.mutate("dead")}
            loading={voteM.isPending && voteM.variables === "dead"}
            style={{ flex: 1 }}
            testID="vote-dead"
          />
        </View>

        {tourist?.reason && (
          <View style={[styles.card, { marginTop: spacing.md }]}>
            <Text style={styles.sectionLabel}>Why this flag?</Text>
            <Text style={{ color: colors.textMuted, marginTop: 4 }}>{tourist.reason}</Text>
          </View>
        )}

        <View style={{ flexDirection: "row", gap: 6, marginTop: spacing.md, flexWrap: "wrap" }}>
          <Chip tone="purple" label="Vibe Score Engine" />
          <Chip tone="aqua" label="Live signals" />
          <Chip tone="neutral" label="Updated moments ago" />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  kicker: {
    color: colors.primaryGlow, fontSize: 10, letterSpacing: 3,
    textTransform: "uppercase", marginBottom: 4,
  },
  title: { color: colors.text, fontSize: 28, fontWeight: "900", letterSpacing: 1.5 },
  sub: { color: colors.textMuted, fontSize: 12, marginTop: 4, letterSpacing: 1.5, textTransform: "uppercase" },
  hero: {
    marginTop: spacing.md,
    padding: spacing.md,
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    borderWidth: 1, borderColor: colors.border,
    flexDirection: "row", alignItems: "center",
  },
  card: {
    marginTop: spacing.md,
    padding: spacing.md,
    backgroundColor: "rgba(255,255,255,0.02)",
    borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border,
  },
  sectionLabel: {
    color: colors.primaryGlow, fontSize: 10, letterSpacing: 2.5, textTransform: "uppercase",
  },
});
