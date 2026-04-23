import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  FlatList, RefreshControl, Text, View, Linking, Alert, StyleSheet,
} from "react-native";
import * as Location from "expo-location";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { SafeAreaView } from "react-native-safe-area-context";
import { NavigationProp, useNavigation } from "@react-navigation/native";
import {
  getTop3, getForecastAll, getTouristFlags, getLiveMusic, getDirections,
  Top3Item, ForecastItem, TouristFlagItem, LiveMusicItem, VibeFilter, Category,
} from "@/lib/api";
import { colors, spacing } from "@/theme";
import { CITY_LABEL, DEFAULT_LOCATION } from "@/config";
import { VenueCard } from "@/components/VenueCard";
import { CategoryTabs } from "@/components/CategoryTabs";
import { Logo, LogoPin } from "@/components/Logo";

export default function TonightScreen() {
  const nav = useNavigation<NavigationProp<any>>();
  const qc = useQueryClient();
  const [filter, setFilter] = useState<VibeFilter>("all");
  const [loc, setLoc] = useState({ lat: DEFAULT_LOCATION.lat, lng: DEFAULT_LOCATION.lng });

  useEffect(() => {
    (async () => {
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status !== "granted") return;
        const pos = await Location.getCurrentPositionAsync({});
        setLoc({ lat: pos.coords.latitude, lng: pos.coords.longitude });
      } catch { /* ignore */ }
    })();
  }, []);

  const vibe = filter === "all" ? undefined : (filter as Category);

  const top3Q = useQuery({
    queryKey: ["top3", loc.lat, loc.lng, vibe],
    queryFn: () => getTop3({ user_lat: loc.lat, user_lng: loc.lng, vibe }),
  });
  const forecastQ = useQuery({ queryKey: ["forecast"], queryFn: getForecastAll });
  const touristQ = useQuery({ queryKey: ["tourist-flags"], queryFn: getTouristFlags });
  const liveQ = useQuery({ queryKey: ["live-music"], queryFn: () => getLiveMusic(true) });

  const forecastByVenue = useMemo(() => {
    const m = new Map<string, ForecastItem>();
    forecastQ.data?.items.forEach((x) => m.set(x.venue_id, x));
    return m;
  }, [forecastQ.data]);
  const touristByVenue = useMemo(() => {
    const m = new Map<string, TouristFlagItem>();
    touristQ.data?.items.forEach((x) => m.set(x.venue_id, x));
    return m;
  }, [touristQ.data]);
  const liveByVenue = useMemo(() => {
    const m = new Map<string, LiveMusicItem>();
    liveQ.data?.items.forEach((x) => m.set(x.venue_id, x));
    return m;
  }, [liveQ.data]);

  const handleGo = useCallback(
    async (item: Top3Item) => {
      try {
        const dir = await getDirections(item.id, loc.lat, loc.lng);
        await Linking.openURL(dir.deeplink);
      } catch (e: any) {
        Alert.alert("Couldn't get directions", e?.message || "Please try again.");
      }
    },
    [loc.lat, loc.lng]
  );

  const refreshing = top3Q.isFetching || forecastQ.isFetching;

  const renderItem = ({ item }: { item: Top3Item }) => (
    <VenueCard
      item={item}
      forecast={forecastByVenue.get(item.id)}
      touristFlag={touristByVenue.get(item.id)}
      live={liveByVenue.get(item.id)}
      onOpenDirections={() => handleGo(item)}
      onPress={() => nav.navigate("VenueDetail", { venue: item })}
      testID={`venue-card-${item.id}`}
    />
  );

  return (
    <SafeAreaView style={styles.root} edges={["top"]}>
      <View style={styles.header}>
        <View style={{ flexDirection: "row", alignItems: "center", gap: 10 }}>
          <LogoPin size={32} />
          <View>
            <Text style={styles.kicker}>Tonight in</Text>
            <Logo size={22} />
            <Text style={styles.city}>{CITY_LABEL.toUpperCase()}</Text>
          </View>
        </View>
      </View>

      <View style={{ paddingHorizontal: spacing.md, marginBottom: spacing.sm }}>
        <CategoryTabs value={filter} onChange={setFilter} />
      </View>

      {top3Q.isLoading ? (
        <LoadingState />
      ) : top3Q.error ? (
        <ErrorState message={(top3Q.error as Error).message} onRetry={() => top3Q.refetch()} />
      ) : !top3Q.data?.items.length ? (
        <EmptyState />
      ) : (
        <FlatList
          contentContainerStyle={{ paddingHorizontal: spacing.md, paddingBottom: spacing.xxl }}
          data={top3Q.data.items}
          keyExtractor={(x) => x.id}
          renderItem={renderItem}
          refreshControl={
            <RefreshControl
              tintColor={colors.primaryGlow}
              refreshing={refreshing}
              onRefresh={() => qc.invalidateQueries()}
            />
          }
        />
      )}
    </SafeAreaView>
  );
}

function LoadingState() {
  return (
    <View style={[styles.center, { paddingHorizontal: spacing.md }]}>
      <Text style={styles.msg}>Finding tonight's vibe…</Text>
    </View>
  );
}
function EmptyState() {
  return (
    <View style={[styles.center, { paddingHorizontal: spacing.md }]}>
      <Text style={styles.msg}>No vibes in this slice. Try another tab.</Text>
    </View>
  );
}
function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <View style={[styles.center, { paddingHorizontal: spacing.md }]}>
      <Text style={[styles.msg, { color: colors.pink }]}>
        Couldn't reach the vibe engine.
      </Text>
      <Text style={[styles.msg, { fontSize: 11 }]}>{message}</Text>
      <Text style={[styles.msg, { color: colors.aqua }]} onPress={onRetry}>Tap to retry</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.bg },
  header: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  kicker: {
    color: colors.primaryGlow,
    fontSize: 10,
    letterSpacing: 3,
    textTransform: "uppercase",
    marginBottom: 2,
  },
  city: {
    color: colors.textMuted,
    fontSize: 11,
    letterSpacing: 3,
    marginTop: 2,
  },
  center: { flex: 1, alignItems: "center", justifyContent: "center", gap: 10 },
  msg: { color: colors.textMuted, textAlign: "center", letterSpacing: 1 },
});
