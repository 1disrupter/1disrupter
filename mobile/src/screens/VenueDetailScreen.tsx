import React from "react";
import { Linking, ScrollView, StyleSheet, Text, View, Alert } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { RouteProp, useRoute } from "@react-navigation/native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getDirections, postFeedback, getForecastAll, getTouristFlags, getLiveMusic,
  getTrajectory, listVenueOffers, getIntelScore, getVenueForecast, getTouristFlagsV2,
  VoteType, Top3Item, ForecastItem, TouristFlagItem, LiveMusicItem, ForecastTrend,
} from "@/lib/api";
import { colors, radius, spacing } from "@/theme";
import { DEFAULT_LOCATION } from "@/config";
import { VibeScoreBadge, CrowdDot, Sparkline } from "@/components/VibeScoreBadge";
import { Chip, LiveMusicBadge, TouristFlagBadge, TrendBadge } from "@/components/Chip";
import { GlowButton } from "@/components/GlowButton";
import { awardCredits, useCreditToast, useWallet } from "@/lib/rewards";
import { useVibePulse } from "@/lib/useVibePulse";

const TREND_ICON: Record<ForecastTrend, string> = {
  rising: "🔺",
  falling: "🔻",
  steady: "➖",
  peaking: "⭐",
};
const TREND_COLOR: Record<ForecastTrend, string> = {
  rising: colors.aqua,
  falling: colors.pink,
  steady: colors.textMuted,
  peaking: "#FFC857",
};

type RouteParams = { VenueDetail: { venue: Top3Item } };

export default function VenueDetailScreen() {
  const { params } = useRoute<RouteProp<RouteParams, "VenueDetail">>();
  const venue = params.venue;
  const qc = useQueryClient();

  const forecastQ = useQuery({ queryKey: ["forecast"], queryFn: getForecastAll });
  const touristQ = useQuery({ queryKey: ["tourist-flags"], queryFn: getTouristFlags });
  const liveQ = useQuery({ queryKey: ["live-music-all"], queryFn: () => getLiveMusic(true) });
  const trajQ = useQuery({
    queryKey: ["trajectory", venue.id],
    queryFn: () => getTrajectory(venue.id, 6),
  });
  const offersQ = useQuery({
    queryKey: ["venue-offers", venue.id],
    queryFn: () => listVenueOffers(venue.id),
  });
  const travelQ = useQuery({
    queryKey: ["travel", venue.id, DEFAULT_LOCATION.lat, DEFAULT_LOCATION.lng],
    queryFn: () => getIntelScore(venue.id, DEFAULT_LOCATION.lat, DEFAULT_LOCATION.lng),
  });
  const aiForecastQ = useQuery({
    queryKey: ["ai-forecast", venue.id],
    queryFn: () => getVenueForecast(venue.id),
  });
  const touristV2Q = useQuery({
    queryKey: ["tourist-flags-v2"],
    queryFn: getTouristFlagsV2,
  });
  const intelLabel = touristV2Q.data?.items.find((x) => x.venue_id === venue.id);
  const walletQ = useWallet();
  const toast = useCreditToast();
  const pulse = useVibePulse(venue.id);

  const forecast = forecastQ.data?.items.find((x) => x.venue_id === venue.id) as ForecastItem | undefined;
  const tourist = touristQ.data?.items.find((x) => x.venue_id === venue.id) as TouristFlagItem | undefined;
  const live = liveQ.data?.items.find((x) => x.venue_id === venue.id) as LiveMusicItem | undefined;

  // Prefer live score over the initial prop when the socket is up.
  const liveScore = pulse.last?.vibe_score ?? forecast?.current_vibe_score ?? venue.vibe_score;

  const voteM = useMutation({
    mutationFn: async (vote: VoteType) => {
      const res = await postFeedback(venue.id, vote);
      const credits = await awardCredits("feedback");
      return { res, credits };
    },
    onSuccess: ({ res, credits }) => {
      toast.show(credits != null ? `+1 Vibe Credit · ${credits} total` : `Thanks!`);
      qc.invalidateQueries();
    },
    onError: (e: any) => Alert.alert("Vote failed", e?.message || "Try again"),
  });

  const go = async () => {
    try {
      const d = await getDirections(venue.id, DEFAULT_LOCATION.lat, DEFAULT_LOCATION.lng);
      await Linking.openURL(d.deeplink);
      const credits = await awardCredits("navigate");
      if (credits != null) toast.show(`+1 Vibe Credit · ${credits} total`);
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
          <VibeScoreBadge score={liveScore} size="lg" />
          <View style={{ flex: 1, marginLeft: spacing.md, gap: 8 }}>
            <CrowdDot score={liveScore} />
            {pulse.live && <Chip tone="aqua" label="● LIVE" small />}
            {forecast && <TrendBadge trend={forecast.trend} />}
            {live?.live_music && <LiveMusicBadge />}
            {tourist && <TouristFlagBadge label={tourist.label} />}
            {intelLabel && intelLabel.label !== "neutral" && (
              <Chip
                tone={intelLabel.label === "local_gem" ? "aqua" : "pink"}
                small
                label={intelLabel.label === "local_gem" ? "💎 LOCAL GEM" : "⚠️ TOURIST TRAP"}
              />
            )}
          </View>
        </View>

        {aiForecastQ.data && (
          <View style={styles.card} testID="ai-forecast-card">
            <Text style={styles.sectionLabel}>AI Forecast · next 3h</Text>
            <View style={{ flexDirection: "row", alignItems: "baseline", gap: 8, marginTop: 6, flexWrap: "wrap" }}>
              <Text style={{ color: TREND_COLOR[aiForecastQ.data.trend], fontSize: 26, fontWeight: "900" }}>
                {TREND_ICON[aiForecastQ.data.trend]} {aiForecastQ.data.forecast_score.toFixed(1)}
              </Text>
              <Text style={{ color: colors.textMuted, fontSize: 11, letterSpacing: 1.4, textTransform: "uppercase" }}>
                {aiForecastQ.data.trend} · {Math.round(aiForecastQ.data.confidence * 100)}% confidence
              </Text>
            </View>
            <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 4 }}>
              Current {aiForecastQ.data.current_score.toFixed(1)} · momentum {aiForecastQ.data.momentum.toFixed(2)}
            </Text>
          </View>
        )}

        <View style={styles.card}>
          <Text style={styles.sectionLabel}>Trajectory</Text>
          <TrajectorySvg data={trajQ.data ?? []} />
        </View>

        {travelQ.data && (
          <View style={styles.card} testID="travel-time-card">
            <Text style={styles.sectionLabel}>Travel time</Text>
            <View style={{ flexDirection: "row", gap: spacing.md, marginTop: 6, flexWrap: "wrap" }}>
              <View style={{ flexDirection: "row", alignItems: "baseline", gap: 6 }}>
                <Text style={{ color: colors.aqua, fontSize: 22, fontWeight: "900" }}>
                  {Math.round(travelQ.data.walking_time_minutes ?? 0)}
                </Text>
                <Text style={{ color: colors.textMuted, fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase" }}>min walk</Text>
              </View>
              <View style={{ flexDirection: "row", alignItems: "baseline", gap: 6 }}>
                <Text style={{ color: colors.pink, fontSize: 22, fontWeight: "900" }}>
                  {Math.round(travelQ.data.driving_time_minutes ?? 0)}
                </Text>
                <Text style={{ color: colors.textMuted, fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase" }}>min drive</Text>
              </View>
              <Chip tone="neutral" small label={(travelQ.data.travel_provider || "stub").toUpperCase()} />
            </View>
          </View>
        )}

        {(offersQ.data ?? []).length > 0 && (
          <View style={styles.card}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
              <Text style={styles.sectionLabel}>Earn Vibe Credits</Text>
              <Chip tone="aqua" label={`${walletQ.data?.credits ?? 0} credits`} small />
            </View>
            {(offersQ.data ?? []).slice(0, 3).map((o) => (
              <View key={o.id} style={styles.offerRow} testID={`venue-offer-${o.id}`}>
                <View style={{ flex: 1 }}>
                  <Text style={{ color: colors.text, fontWeight: "700" }}>{o.name}</Text>
                  {!!o.description && (
                    <Text style={{ color: colors.textMuted, fontSize: 11 }}>{o.description}</Text>
                  )}
                </View>
                <Text style={{ color: colors.aqua, fontWeight: "900" }}>{o.cost_credits}c</Text>
              </View>
            ))}
            <Text style={{ color: colors.textFaint, fontSize: 11, marginTop: 6 }}>
              Redeem from the Wallet tab after you earn enough credits.
            </Text>
          </View>
        )}

        {toast.msg && (
          <View style={styles.toast} testID="credit-toast">
            <Text style={styles.toastText}>{toast.msg}</Text>
          </View>
        )}

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

function TrajectorySvg({ data }: { data: { timestamp: string; vibe_score: number }[] }) {
  const values = data.length ? data.map((d) => d.vibe_score) : undefined;
  return <Sparkline values={values} width={280} height={38} />;
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
  offerRow: {
    flexDirection: "row", alignItems: "center", gap: spacing.md,
    paddingVertical: 8, borderTopWidth: 1, borderTopColor: colors.border, marginTop: 6,
  },
  toast: {
    marginTop: spacing.md, alignSelf: "center",
    paddingHorizontal: 14, paddingVertical: 8,
    backgroundColor: "rgba(0,245,255,0.12)",
    borderColor: colors.aqua, borderWidth: 1, borderRadius: radius.pill,
  },
  toastText: { color: colors.aqua, fontSize: 12, fontWeight: "800", letterSpacing: 1.5, textTransform: "uppercase" },
});
