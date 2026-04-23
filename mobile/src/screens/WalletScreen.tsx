import React from "react";
import { FlatList, StyleSheet, Text, View, Alert, RefreshControl } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  listActiveOffers, listMyRedemptions, redeemOffer, RewardOffer,
} from "@/lib/api";
import { useUserId, useWallet } from "@/lib/rewards";
import { colors, radius, spacing } from "@/theme";
import { Chip } from "@/components/Chip";
import { GlowButton } from "@/components/GlowButton";

export default function WalletScreen() {
  const uid = useUserId();
  const qc = useQueryClient();
  const walletQ = useWallet();

  // Simpler: list active offers by re-using /rewards/offers (no venue filter).
  const allOffersQ = useQuery<RewardOffer[]>({
    queryKey: ["offers-active"],
    queryFn: listActiveOffers,
  });

  const redemptionsQ = useQuery({
    queryKey: ["my-redemptions", uid],
    enabled: !!uid,
    queryFn: () => listMyRedemptions(uid!, 20),
  });

  const redeem = useMutation({
    mutationFn: (offer_id: string) => redeemOffer(uid!, offer_id),
    onSuccess: () => {
      Alert.alert("Redeemed!", "Show this at the venue to claim.");
      qc.invalidateQueries({ queryKey: ["wallet", uid] });
      qc.invalidateQueries({ queryKey: ["my-redemptions", uid] });
    },
    onError: (e: any) => Alert.alert("Can't redeem", e?.message || "Not enough credits?"),
  });

  const credits = walletQ.data?.credits ?? 0;
  const offers = allOffersQ.data ?? [];

  const refreshing =
    walletQ.isRefetching || allOffersQ.isRefetching || redemptionsQ.isRefetching;

  const onRefresh = () => {
    walletQ.refetch();
    allOffersQ.refetch();
    redemptionsQ.refetch();
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: colors.bg }}>
      <FlatList
        data={offers}
        keyExtractor={(o) => o.id}
        contentContainerStyle={{ padding: spacing.md, paddingBottom: spacing.xxl }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primaryGlow} />}
        ListHeaderComponent={
          <View>
            <Text style={styles.kicker}>Vibe Credits</Text>
            <Text style={styles.title}>WALLET</Text>
            <View style={styles.balance} testID="wallet-balance-card">
              <Text style={styles.balanceLabel}>Balance</Text>
              <Text style={styles.balanceValue}>{credits}</Text>
              <Text style={styles.balanceHint}>credits</Text>
            </View>
            <View style={{ flexDirection: "row", gap: 6, marginTop: spacing.sm, flexWrap: "wrap" }}>
              <Chip tone="purple" label="+1 per vote" />
              <Chip tone="aqua" label="+3 per visit" />
              <Chip tone="pink" label="+1 per Go" />
            </View>
            <Text style={[styles.sectionLabel, { marginTop: spacing.lg }]}>Spend your credits</Text>
          </View>
        }
        renderItem={({ item }) => (
          <View style={styles.offer} testID={`offer-${item.id}`}>
            <View style={{ flex: 1 }}>
              <Text style={styles.offerName}>{item.name}</Text>
              {!!item.description && <Text style={styles.offerDesc}>{item.description}</Text>}
            </View>
            <View style={{ alignItems: "flex-end" }}>
              <Text style={styles.offerCost}>{item.cost_credits}c</Text>
              <GlowButton
                label={credits >= item.cost_credits ? "Redeem" : "Save up"}
                variant={credits >= item.cost_credits ? "pink" : "secondary"}
                size="sm"
                disabled={credits < item.cost_credits || redeem.isPending}
                onPress={() => redeem.mutate(item.id)}
                style={{ marginTop: 6 }}
                testID={`redeem-${item.id}`}
              />
            </View>
          </View>
        )}
        ListEmptyComponent={
          <Text style={{ color: colors.textFaint, textAlign: "center", marginTop: 40 }}>
            No active offers yet. Earn credits and check back soon.
          </Text>
        }
        ListFooterComponent={
          <View style={{ marginTop: spacing.lg }}>
            <Text style={styles.sectionLabel}>Recent redemptions</Text>
            {(redemptionsQ.data ?? []).length === 0 && (
              <Text style={{ color: colors.textFaint, marginTop: 8 }}>Nothing yet — your first claim will land here.</Text>
            )}
            {(redemptionsQ.data ?? []).map((r) => (
              <View key={r.id} style={styles.redeemRow}>
                <Text style={{ color: colors.textMuted, fontSize: 11, letterSpacing: 1, textTransform: "uppercase" }}>
                  {new Date(r.timestamp).toLocaleString()}
                </Text>
                <Text style={{ color: colors.aqua, fontWeight: "800" }}>-{r.cost_credits}c</Text>
              </View>
            ))}
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  kicker: { color: colors.primaryGlow, fontSize: 10, letterSpacing: 3, textTransform: "uppercase" },
  title: { color: colors.text, fontSize: 32, fontWeight: "900", letterSpacing: 2, marginTop: 2 },
  balance: {
    marginTop: spacing.md, padding: spacing.lg, borderRadius: radius.xl,
    borderWidth: 1, borderColor: colors.primaryGlow, backgroundColor: "rgba(138,43,226,0.12)",
    alignItems: "center",
  },
  balanceLabel: { color: colors.textMuted, fontSize: 11, letterSpacing: 2.5, textTransform: "uppercase" },
  balanceValue: {
    color: colors.text, fontSize: 64, fontWeight: "900", letterSpacing: 3, marginTop: 4,
    textShadowColor: "rgba(177,92,255,0.8)", textShadowRadius: 18,
  },
  balanceHint: { color: colors.textFaint, fontSize: 11, letterSpacing: 2, textTransform: "uppercase" },
  sectionLabel: { color: colors.primaryGlow, fontSize: 10, letterSpacing: 2.5, textTransform: "uppercase" },
  offer: {
    flexDirection: "row", gap: spacing.md, padding: spacing.md, marginTop: spacing.sm,
    borderRadius: radius.lg, borderWidth: 1, borderColor: colors.border,
    backgroundColor: "rgba(255,255,255,0.02)", alignItems: "center",
  },
  offerName: { color: colors.text, fontWeight: "800", fontSize: 14 },
  offerDesc: { color: colors.textMuted, fontSize: 12, marginTop: 2 },
  offerCost: { color: colors.aqua, fontSize: 18, fontWeight: "900" },
  redeemRow: {
    flexDirection: "row", justifyContent: "space-between", alignItems: "center",
    paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
});
