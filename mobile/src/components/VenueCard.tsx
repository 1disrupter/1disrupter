import React from "react";
import { Pressable, Text, View, StyleSheet } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { colors, radius, shadow } from "@/theme";
import type { Top3Item, ForecastItem, TouristFlagItem, LiveMusicItem, Directions } from "@/lib/api";
import { Chip, TrendBadge, TouristFlagBadge, LiveMusicBadge } from "./Chip";
import { VibeScoreBadge, CrowdDot, Sparkline } from "./VibeScoreBadge";
import { GlowButton } from "./GlowButton";

const CATEGORY_LABEL: Record<string, string> = {
  bar: "Bar", club: "Club", live_music: "Live Music",
};

interface Props {
  item: Top3Item;
  forecast?: ForecastItem;
  touristFlag?: TouristFlagItem;
  live?: LiveMusicItem;
  directions?: Directions;
  onOpenDirections: () => void;
  onPress?: () => void;
  testID?: string;
}

export function VenueCard({
  item, forecast, touristFlag, live, directions,
  onOpenDirections, onPress, testID,
}: Props) {
  return (
    <Pressable onPress={onPress} testID={testID}>
      <View style={styles.card}>
        <LinearGradient
          colors={["rgba(138,43,226,0.18)", "rgba(255,46,196,0.06)", "transparent"]}
          start={{ x: 0, y: 0 }}
          end={{ x: 1, y: 1 }}
          style={StyleSheet.absoluteFill}
        />

        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
          <View style={{ flex: 1, paddingRight: 10 }}>
            <Text style={styles.name} numberOfLines={1}>
              {item.name.toUpperCase()}
            </Text>
            <Text style={styles.sub}>
              {CATEGORY_LABEL[item.category] || item.category}
              {item.distance_km != null ? ` · ${item.distance_km.toFixed(1)} km` : ""}
            </Text>
          </View>
          <VibeScoreBadge score={item.vibe_score} />
        </View>

        <View style={styles.row}>
          <CrowdDot score={item.vibe_score} />
          {forecast && <TrendBadge trend={forecast.trend} />}
          {live?.live_music && <LiveMusicBadge />}
          {touristFlag && <TouristFlagBadge label={touristFlag.label} />}
        </View>

        <View style={styles.footer}>
          <Sparkline />
          <GlowButton
            label={directions ? `${directions.duration_minutes} min · Go here` : "Go here now"}
            variant="pink"
            size="md"
            onPress={onOpenDirections}
            testID={`go-here-${item.id}`}
          />
        </View>
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.card,
    borderColor: colors.border,
    borderWidth: 1,
    borderRadius: radius.xl,
    padding: 16,
    marginBottom: 14,
    overflow: "hidden",
    ...shadow.neonPurple,
    shadowOpacity: 0.25,
    shadowRadius: 20,
  },
  name: {
    color: colors.text,
    fontSize: 18,
    fontWeight: "900",
    letterSpacing: 1,
  },
  sub: {
    color: colors.textMuted,
    fontSize: 11,
    marginTop: 2,
    letterSpacing: 1,
    textTransform: "uppercase",
  },
  row: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 12,
  },
  footer: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginTop: 14,
  },
});
