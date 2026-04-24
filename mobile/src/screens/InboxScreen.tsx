import React from "react";
import { FlatList, RefreshControl, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useQuery } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";
import { getInbox, InboxItem } from "@/lib/api";
import { useUserId } from "@/lib/rewards";
import { colors, radius, spacing } from "@/theme";

const KIND_META: Record<string, { icon: keyof typeof Ionicons.glyphMap; tone: string }> = {
  daily_login:       { icon: "sunny-outline",       tone: colors.primaryGlow },
  first_visit_bonus: { icon: "gift-outline",        tone: colors.pink },
  vibe_spike:        { icon: "flash-outline",       tone: colors.aqua },
  offer_drop:        { icon: "pricetag-outline",    tone: colors.pink },
  tonight_hotspots:  { icon: "flame-outline",       tone: "#FFB347" },
  milestone:         { icon: "trophy-outline",      tone: colors.aqua },
};

export default function InboxScreen() {
  const uid = useUserId();
  const q = useQuery({
    queryKey: ["inbox", uid],
    enabled: !!uid,
    queryFn: () => getInbox(uid!),
    refetchInterval: 30_000,
  });

  const items = q.data?.items ?? [];

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <FlatList
        data={items}
        keyExtractor={(i) => i.id}
        contentContainerStyle={{ padding: spacing.md, paddingBottom: spacing.xxl }}
        refreshControl={<RefreshControl refreshing={q.isRefetching} onRefresh={q.refetch} tintColor={colors.primaryGlow} />}
        ListHeaderComponent={
          <View>
            <Text style={styles.kicker}>Activity</Text>
            <Text style={styles.title}>INBOX</Text>
            <Text style={styles.sub}>Your last 20 push-worthy moments.</Text>
          </View>
        }
        renderItem={({ item }) => <InboxRow item={item} />}
        ListEmptyComponent={
          <Text style={styles.empty}>
            {q.isPending ? "Loading…" : "Nothing yet. Vote, visit a venue, or wait for Tonight's Hotspots at 21:00."}
          </Text>
        }
      />
    </SafeAreaView>
  );
}

function InboxRow({ item }: { item: InboxItem }) {
  const meta = KIND_META[item.kind] || { icon: "notifications-outline" as const, tone: colors.primaryGlow };
  const when = new Date(item.created_at);
  return (
    <View style={styles.row} testID={`inbox-row-${item.id}`}>
      <View style={[styles.iconWrap, { borderColor: meta.tone }]}>
        <Ionicons name={meta.icon} size={20} color={meta.tone} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={styles.itemTitle}>{item.title}</Text>
        <Text style={styles.itemBody} numberOfLines={3}>{item.body}</Text>
        <Text style={styles.itemTs}>{when.toLocaleString()}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  kicker: { color: colors.primaryGlow, fontSize: 10, letterSpacing: 3, textTransform: "uppercase" },
  title: { color: colors.text, fontSize: 32, fontWeight: "900", letterSpacing: 2, marginTop: 2 },
  sub: { color: colors.textMuted, fontSize: 12, marginTop: 4, marginBottom: spacing.md },
  row: {
    flexDirection: "row", gap: spacing.md, marginBottom: spacing.sm,
    padding: spacing.md, borderRadius: radius.lg,
    borderWidth: 1, borderColor: colors.border, backgroundColor: "rgba(255,255,255,0.02)",
  },
  iconWrap: {
    width: 42, height: 42, borderRadius: radius.pill,
    borderWidth: 1, alignItems: "center", justifyContent: "center",
    backgroundColor: "rgba(255,255,255,0.02)",
  },
  itemTitle: { color: colors.text, fontWeight: "800", fontSize: 14 },
  itemBody: { color: colors.textMuted, fontSize: 12, marginTop: 2 },
  itemTs: { color: colors.textFaint, fontSize: 10, letterSpacing: 1.2, textTransform: "uppercase", marginTop: 6 },
  empty: { color: colors.textFaint, textAlign: "center", marginTop: 60 },
});
