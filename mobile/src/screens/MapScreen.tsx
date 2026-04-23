import React, { useMemo, useState } from "react";
import { Linking, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import MapView, { Marker } from "react-native-maps";
import { useQuery } from "@tanstack/react-query";
import {
  getHeatmap, getForecastAll, getLiveMusic, getTouristFlags, getDirections,
  HeatPoint, ForecastItem, LiveMusicItem, TouristFlagItem,
} from "@/lib/api";
import { colors, radius, spacing } from "@/theme";
import { DEFAULT_LOCATION } from "@/config";
import { Chip, LiveMusicBadge, TouristFlagBadge, TrendBadge } from "@/components/Chip";
import { VibeScoreBadge } from "@/components/VibeScoreBadge";
import { GlowButton } from "@/components/GlowButton";

const dark = [
  { elementType: "geometry", stylers: [{ color: "#0b0712" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#746391" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#05050A" }] },
  { featureType: "road", stylers: [{ color: "#1b0e33" }] },
  { featureType: "water", stylers: [{ color: "#05020f" }] },
  { featureType: "poi", stylers: [{ visibility: "off" }] },
];

export default function MapScreen() {
  const [selected, setSelected] = useState<HeatPoint | null>(null);
  const heatQ = useQuery({ queryKey: ["heatmap"], queryFn: getHeatmap });
  const forecastQ = useQuery({ queryKey: ["forecast"], queryFn: getForecastAll });
  const liveQ = useQuery({ queryKey: ["live-music-all"], queryFn: () => getLiveMusic(true) });
  const touristQ = useQuery({ queryKey: ["tourist-flags"], queryFn: getTouristFlags });

  const forecastMap = useMemo(() => {
    const m = new Map<string, ForecastItem>();
    forecastQ.data?.items.forEach((x) => m.set(x.venue_id, x));
    return m;
  }, [forecastQ.data]);
  const liveMap = useMemo(() => {
    const m = new Map<string, LiveMusicItem>();
    liveQ.data?.items.forEach((x) => m.set(x.venue_id, x));
    return m;
  }, [liveQ.data]);
  const touristMap = useMemo(() => {
    const m = new Map<string, TouristFlagItem>();
    touristQ.data?.items.forEach((x) => m.set(x.venue_id, x));
    return m;
  }, [touristQ.data]);

  const go = async (p: HeatPoint) => {
    try {
      const d = await getDirections(p.id, DEFAULT_LOCATION.lat, DEFAULT_LOCATION.lng);
      Linking.openURL(d.deeplink);
    } catch { /* noop */ }
  };

  const heatColor = (heat: number) => {
    if (heat >= 8) return colors.pink;
    if (heat >= 6) return colors.amber;
    if (heat >= 4) return colors.primaryGlow;
    return colors.aqua;
  };
  const heatSize = (heat: number) => 14 + Math.round(heat * 1.4);

  const live = selected ? liveMap.get(selected.id) : undefined;
  const tourist = selected ? touristMap.get(selected.id) : undefined;
  const forecast = selected ? forecastMap.get(selected.id) : undefined;

  return (
    <View style={{ flex: 1, backgroundColor: colors.bg }}>
      <MapView
        style={{ flex: 1 }}
        customMapStyle={dark}
        initialRegion={{
          latitude: DEFAULT_LOCATION.lat,
          longitude: DEFAULT_LOCATION.lng,
          latitudeDelta: 0.045,
          longitudeDelta: 0.045,
        }}
      >
        {heatQ.data?.points.map((p) => {
          const sz = heatSize(p.heat);
          const c = heatColor(p.heat);
          return (
            <Marker
              key={p.id}
              coordinate={{ latitude: p.lat, longitude: p.lng }}
              onPress={() => setSelected(p)}
              tracksViewChanges={false}
            >
              <View
                style={{
                  width: sz, height: sz, borderRadius: sz / 2,
                  backgroundColor: c,
                  opacity: 0.9,
                  shadowColor: c, shadowRadius: sz, shadowOpacity: 0.9, shadowOffset: { width: 0, height: 0 },
                  borderWidth: 2, borderColor: "#fff",
                }}
              />
            </Marker>
          );
        })}
      </MapView>

      <SafeAreaView pointerEvents="box-none" style={StyleSheet.absoluteFill} edges={["top"]}>
        <View style={styles.legend}>
          <Chip tone="pink" label="🔥 Packed" />
          <Chip tone="amber" label="Busy" />
          <Chip tone="purple" label="Medium" />
          <Chip tone="aqua" label="Chill" />
        </View>
      </SafeAreaView>

      {selected && (
        <SafeAreaView edges={["bottom"]} style={styles.sheetWrap} pointerEvents="box-none">
          <View style={styles.sheet}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
              <View style={{ flex: 1 }}>
                <Text style={styles.name}>{selected.name.toUpperCase()}</Text>
                <Text style={styles.sub}>
                  {selected.category.replace("_", " ")} · heat {selected.heat.toFixed(1)}
                </Text>
              </View>
              <VibeScoreBadge score={forecast?.current_vibe_score ?? selected.heat} />
            </View>
            <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 10 }}>
              {forecast && <TrendBadge trend={forecast.trend} />}
              {live?.live_music && <LiveMusicBadge />}
              {tourist && <TouristFlagBadge label={tourist.label} />}
            </View>
            <View style={{ flexDirection: "row", gap: 10, marginTop: 14 }}>
              <GlowButton
                label="Go here now"
                variant="pink"
                onPress={() => go(selected)}
                style={{ flex: 1 }}
              />
              <GlowButton
                label="Close"
                variant="secondary"
                onPress={() => setSelected(null)}
              />
            </View>
          </View>
        </SafeAreaView>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  legend: {
    flexDirection: "row",
    gap: 6,
    padding: spacing.sm,
    flexWrap: "wrap",
  },
  sheetWrap: {
    position: "absolute", left: 0, right: 0, bottom: 0,
  },
  sheet: {
    marginHorizontal: spacing.sm,
    marginBottom: spacing.md,
    backgroundColor: colors.card,
    borderWidth: 1, borderColor: colors.primaryGlow,
    borderRadius: radius.xl,
    padding: spacing.md,
    shadowColor: colors.primary,
    shadowRadius: 28, shadowOpacity: 0.7, shadowOffset: { width: 0, height: 0 },
  },
  name: { color: colors.text, fontSize: 18, fontWeight: "900", letterSpacing: 1 },
  sub: { color: colors.textMuted, fontSize: 11, letterSpacing: 1.5, marginTop: 2, textTransform: "uppercase" },
});
