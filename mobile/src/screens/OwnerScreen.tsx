/**
 * OwnerScreen — mobile dashboard for verified venue owners.
 * Iteration 15 parity: multi-venue picker + integrations (Slack / Discord).
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator, FlatList, Pressable, RefreshControl,
  ScrollView, StyleSheet, Text, TextInput, View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius, spacing } from "@/theme";
import { API_BASE } from "@/config";
import { GlowButton } from "@/components/GlowButton";
import { useOwnerKey } from "@/lib/ownerKey";

const LAST_VENUE_KEY = "v2n_owner_last_venue";
const SLACK_PREFIX = "https://hooks.slack.com/";
const DISCORD_PREFIX = "https://discord.com/api/webhooks/";

type VenueSummary = {
  id: string; name: string; category: string;
  is_verified?: boolean;
  vibe_score: number;
  crowd_level: string | null;
  last_updated: string | null;
  external_signals: Record<string, number> | null;
  social_handles: { instagram?: string; tiktok?: string };
  webhooks: { slack_webhook_url?: string; discord_webhook_url?: string };
};
type OwnerMe = {
  owner: { email: string; name: string; claim_id: string; verified_at: string | null; venue_count: number };
  venues: VenueSummary[];
};
type InboxItem = {
  id: string; kind: string; title: string; body: string;
  data: Record<string, any>; created_at: string;
};

async function fetchOwner<T>(path: string, key: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", "X-Owner-Key": key, ...(init.headers || {}) },
  });
  const txt = await res.text();
  if (!res.ok) {
    let msg = txt;
    try { msg = JSON.parse(txt)?.detail ?? txt; } catch {}
    throw new Error(typeof msg === "string" ? msg : "Request failed");
  }
  return txt ? JSON.parse(txt) : ({} as T);
}

export default function OwnerScreen() {
  const { key, ready, save, clear } = useOwnerKey();
  const [input, setInput] = useState("");
  const [me, setMe] = useState<OwnerMe | null>(null);
  const [inbox, setInbox] = useState<InboxItem[]>([]);
  const [activeVenueId, setActiveVenueId] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [igHandle, setIgHandle] = useState("");
  const [ttHandle, setTtHandle] = useState("");
  const [slackUrl, setSlackUrl] = useState("");
  const [discordUrl, setDiscordUrl] = useState("");
  const [saving, setSaving] = useState(false);

  const load = useCallback(async (k: string) => {
    setLoading(true); setError(null);
    try {
      const [m, ib] = await Promise.all([
        fetchOwner<OwnerMe>("/owner/me", k),
        fetchOwner<{ items: InboxItem[] }>("/owner/inbox?limit=10", k),
      ]);
      setMe(m);
      setInbox(ib.items || []);
      const stored = await AsyncStorage.getItem(LAST_VENUE_KEY);
      const owned = m.venues.map((v) => v.id);
      const next = (stored && owned.includes(stored) && stored) || owned[0] || "";
      setActiveVenueId(next);
      if (next) await AsyncStorage.setItem(LAST_VENUE_KEY, next);
    } catch (e: any) {
      setError(e.message || "Invalid key");
      setMe(null);
    } finally {
      setLoading(false); setRefreshing(false);
    }
  }, []);

  useEffect(() => { if (key) load(key); }, [key, load]);

  // Sync editor state whenever active venue changes.
  useEffect(() => {
    if (!me || !activeVenueId) return;
    const v = me.venues.find((x) => x.id === activeVenueId);
    if (!v) return;
    setIgHandle(v.social_handles?.instagram || "");
    setTtHandle(v.social_handles?.tiktok || "");
    setSlackUrl(v.webhooks?.slack_webhook_url || "");
    setDiscordUrl(v.webhooks?.discord_webhook_url || "");
  }, [me, activeVenueId]);

  const signIn = async () => {
    const k = input.trim();
    if (!k) { setError("Paste your owner key"); return; }
    await save(k);
  };

  const onRefresh = async () => { if (!key) return; setRefreshing(true); await load(key); };

  const pickVenue = async (id: string) => {
    setActiveVenueId(id);
    await AsyncStorage.setItem(LAST_VENUE_KEY, id);
  };

  const saveHandles = async () => {
    if (!key || !activeVenueId) return;
    setSaving(true);
    try {
      await fetchOwner(`/owner/venue/${activeVenueId}/handles`, key, {
        method: "PUT",
        body: JSON.stringify({
          instagram: igHandle.trim() || null,
          tiktok: ttHandle.trim() || null,
        }),
      });
      await load(key);
    } catch (e: any) { setError(e.message || "Couldn't save"); }
    finally { setSaving(false); }
  };

  const saveHooks = async () => {
    if (!key || !activeVenueId) return;
    const s = slackUrl.trim(); const d = discordUrl.trim();
    if (s && !s.startsWith(SLACK_PREFIX)) { setError(`Slack URL must start with ${SLACK_PREFIX}`); return; }
    if (d && !d.startsWith(DISCORD_PREFIX)) { setError(`Discord URL must start with ${DISCORD_PREFIX}`); return; }
    setSaving(true);
    try {
      await fetchOwner(`/owner/venue/${activeVenueId}/webhooks`, key, {
        method: "PUT",
        body: JSON.stringify({ slack_webhook_url: s || null, discord_webhook_url: d || null }),
      });
      await load(key);
    } catch (e: any) { setError(e.message || "Couldn't save"); }
    finally { setSaving(false); }
  };

  const testHook = async () => {
    if (!key || !activeVenueId) return;
    setSaving(true);
    try {
      await fetchOwner(`/owner/venue/${activeVenueId}/webhooks/test`, key, { method: "POST" });
    } catch (e: any) { setError(e.message || "Test failed"); }
    finally { setSaving(false); }
  };

  const activeVenue = useMemo(
    () => (me?.venues || []).find((v) => v.id === activeVenueId) || null,
    [me, activeVenueId]
  );
  const signalRows = useMemo(() => {
    const s = activeVenue?.external_signals || null;
    if (!s) return [];
    return [
      ["Google busyness", s.google_score], ["Social", s.social_score],
      ["Events", s.event_score], ["Time-of-day", s.time_score], ["User votes", s.user_votes_score],
    ] as const;
  }, [activeVenue]);

  if (!ready) {
    return <SafeAreaView style={styles.container}><ActivityIndicator color={colors.primaryGlow} /></SafeAreaView>;
  }

  if (!key) {
    return (
      <SafeAreaView style={styles.container}>
        <ScrollView contentContainerStyle={{ padding: spacing.md }}>
          <Text style={styles.kicker}>Owner Console</Text>
          <Text style={styles.h1}>Sign in with your <Text style={{ color: colors.pink }}>owner key</Text></Text>
          <Text style={styles.body}>Paste the vk_… key you received after verifying your claim.</Text>
          <TextInput
            value={input} onChangeText={setInput}
            placeholder="vk_xxxxxxxxxxxx…" placeholderTextColor={colors.textFaint}
            autoCapitalize="none" autoCorrect={false}
            style={styles.input} testID="owner-key-input"
          />
          {error && <Text style={styles.err}>{error}</Text>}
          <GlowButton label="Sign in" variant="pink" size="md" onPress={signIn} style={{ marginTop: spacing.md }} testID="owner-key-submit" />
        </ScrollView>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={{ padding: spacing.md, paddingBottom: spacing.xxl }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primaryGlow} />}
      >
        <View style={{ flexDirection: "row", alignItems: "center" }}>
          <Text style={styles.kicker}>Owner Console</Text>
          <Pressable onPress={clear} style={{ marginLeft: "auto" }} testID="owner-logout">
            <Text style={{ color: colors.textMuted, fontSize: 12, textTransform: "uppercase", letterSpacing: 2 }}>Sign out</Text>
          </Pressable>
        </View>

        {loading && !me && <ActivityIndicator color={colors.primaryGlow} style={{ marginTop: spacing.lg }} />}
        {error && <Text style={styles.err}>{error}</Text>}

        {me && (
          <>
            <Text style={styles.h1}>{me.owner.name}</Text>
            <Text style={[styles.body, { color: colors.textMuted, fontSize: 12 }]}>
              {me.owner.email} · {me.owner.venue_count} venue{me.owner.venue_count === 1 ? "" : "s"}
            </Text>

            {/* Venue switcher */}
            {me.venues.length > 1 && (
              <View testID="owner-venue-switcher-mobile" style={{ marginTop: spacing.md }}>
                <Text style={styles.section}>YOUR VENUES</Text>
                <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                  <View style={{ flexDirection: "row", gap: 8 }}>
                    {me.venues.map((v) => (
                      <Pressable
                        key={v.id}
                        onPress={() => pickVenue(v.id)}
                        testID={`owner-venue-pick-${v.id}`}
                        style={[
                          styles.pillBtn,
                          activeVenueId === v.id && styles.pillBtnActive,
                        ]}
                      >
                        <Text style={[styles.pillText, activeVenueId === v.id && { color: colors.text }]}>
                          {v.name}
                        </Text>
                      </Pressable>
                    ))}
                  </View>
                </ScrollView>
              </View>
            )}

            {activeVenue && (
              <>
                <View style={styles.vibeCard} testID="owner-vibe-card-mobile">
                  <View style={{ flexDirection: "row", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
                    <Text style={{ color: colors.text, fontSize: 15, fontWeight: "700", letterSpacing: 1 }}>
                      {activeVenue.name}
                    </Text>
                    {activeVenue.is_verified && (
                      <View style={[styles.chip, { backgroundColor: colors.aqua + "22", borderColor: colors.aqua }]}>
                        <Text style={{ color: colors.aqua, fontSize: 9, letterSpacing: 2, textTransform: "uppercase" }}>verified ✓</Text>
                      </View>
                    )}
                  </View>
                  <Text style={styles.vibeNum}>{(activeVenue.vibe_score ?? 0).toFixed(2)}</Text>
                  <Text style={styles.vibeLabel}>LIVE VIBE SCORE</Text>
                </View>

                <Text style={styles.section}>EXTERNAL SIGNALS</Text>
                <View style={{ gap: 10 }}>
                  {signalRows.map(([label, val]) => (
                    <View key={label} style={styles.signalRow} testID={`owner-signal-${label}`}>
                      <Text style={styles.signalLabel}>{label}</Text>
                      <Text style={styles.signalValue}>{(val ?? 0).toFixed(2)}</Text>
                      <View style={styles.signalBar}>
                        <View style={[styles.signalFill, { width: `${Math.min(100, ((val ?? 0) / 10) * 100)}%` }]} />
                      </View>
                    </View>
                  ))}
                </View>

                <Text style={styles.section}>SOCIAL HANDLES</Text>
                <TextInput
                  value={igHandle} onChangeText={setIgHandle}
                  placeholder="@laterraza" placeholderTextColor={colors.textFaint}
                  autoCapitalize="none" style={styles.input} testID="owner-handle-ig"
                />
                <TextInput
                  value={ttHandle} onChangeText={setTtHandle}
                  placeholder="@terraza" placeholderTextColor={colors.textFaint}
                  autoCapitalize="none" style={[styles.input, { marginTop: spacing.xs }]} testID="owner-handle-tt"
                />
                <GlowButton label={saving ? "…" : "Save handles"} variant="primary" size="md" disabled={saving} onPress={saveHandles} style={{ marginTop: spacing.sm }} testID="owner-handles-save" />

                <Text style={styles.section}>INTEGRATIONS</Text>
                <Text style={[styles.body, { color: colors.textFaint, fontSize: 12 }]}>
                  Pipe events into your team's Slack/Discord.
                </Text>
                <TextInput
                  value={slackUrl} onChangeText={setSlackUrl}
                  placeholder="https://hooks.slack.com/services/…" placeholderTextColor={colors.textFaint}
                  autoCapitalize="none" autoCorrect={false} style={[styles.input, { marginTop: spacing.sm }]}
                  testID="owner-slack-url"
                />
                <TextInput
                  value={discordUrl} onChangeText={setDiscordUrl}
                  placeholder="https://discord.com/api/webhooks/…" placeholderTextColor={colors.textFaint}
                  autoCapitalize="none" autoCorrect={false} style={[styles.input, { marginTop: spacing.xs }]}
                  testID="owner-discord-url"
                />
                <View style={{ flexDirection: "row", gap: 8, marginTop: spacing.sm }}>
                  <GlowButton label="Save webhooks" variant="primary" size="md" disabled={saving} onPress={saveHooks} style={{ flex: 1 }} testID="owner-hooks-save" />
                  <GlowButton
                    label="Test"
                    variant="aqua"
                    size="md"
                    disabled={saving || (!slackUrl && !discordUrl)}
                    onPress={testHook}
                    style={{ flex: 1 }}
                    testID="owner-hooks-test"
                  />
                </View>
              </>
            )}

            <Text style={styles.section}>INBOX</Text>
            {inbox.length === 0 ? (
              <Text style={[styles.body, { color: colors.textFaint }]}>No messages yet.</Text>
            ) : (
              <FlatList
                scrollEnabled={false} data={inbox} keyExtractor={(i) => i.id}
                renderItem={({ item }) => (
                  <View style={styles.inboxCard} testID={`owner-inbox-${item.kind}`}>
                    <Text style={styles.inboxKind}>{item.kind.replace("_", " ")}</Text>
                    <Text style={styles.inboxTitle}>{item.title}</Text>
                    <Text style={styles.inboxBody}>{item.body}</Text>
                  </View>
                )}
                ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
              />
            )}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bg },
  kicker: { color: colors.primaryGlow, fontSize: 11, letterSpacing: 3, textTransform: "uppercase" },
  h1: { color: colors.text, fontSize: 28, fontWeight: "900", letterSpacing: 2, marginTop: 4 },
  body: { color: colors.text, marginTop: 6, lineHeight: 20 },
  err: { color: colors.pink, marginTop: 8, fontSize: 12 },
  input: {
    marginTop: spacing.sm, padding: 12, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border, backgroundColor: "rgba(255,255,255,0.03)",
    color: colors.text, fontSize: 14,
  },
  vibeCard: {
    marginTop: spacing.lg, padding: spacing.lg,
    backgroundColor: colors.card, borderRadius: radius.xl,
    borderWidth: 1, borderColor: colors.primaryGlow,
  },
  vibeNum: { color: colors.text, fontFamily: "Courier", fontSize: 44, marginTop: 8 },
  vibeLabel: { color: colors.textMuted, fontSize: 10, letterSpacing: 2.5, textTransform: "uppercase", marginTop: 2 },
  chip: { borderRadius: 999, paddingHorizontal: 8, paddingVertical: 3, borderWidth: 1 },
  section: {
    color: colors.primaryGlow, fontSize: 11, letterSpacing: 3, textTransform: "uppercase",
    marginTop: spacing.xl, marginBottom: spacing.sm,
  },
  signalRow: {
    padding: spacing.sm, backgroundColor: colors.card,
    borderRadius: radius.md, borderWidth: 1, borderColor: colors.border,
  },
  signalLabel: { color: colors.textMuted, fontSize: 10, letterSpacing: 2, textTransform: "uppercase" },
  signalValue: { color: colors.text, fontSize: 22, fontFamily: "Courier", marginTop: 2 },
  signalBar: { marginTop: 6, height: 4, borderRadius: 2, backgroundColor: colors.border, overflow: "hidden" },
  signalFill: { height: "100%", backgroundColor: colors.primary },
  inboxCard: {
    padding: spacing.sm, backgroundColor: colors.card,
    borderRadius: radius.md, borderWidth: 1, borderColor: colors.border,
  },
  inboxKind: { color: colors.primaryGlow, fontSize: 9, letterSpacing: 2, textTransform: "uppercase" },
  inboxTitle: { color: colors.text, fontSize: 14, fontWeight: "700", marginTop: 2 },
  inboxBody: { color: colors.textMuted, fontSize: 12, marginTop: 4, lineHeight: 18 },
  pillBtn: {
    paddingVertical: 8, paddingHorizontal: 14, borderRadius: 999,
    borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card,
  },
  pillBtnActive: { borderColor: colors.primaryGlow, backgroundColor: colors.primary + "22" },
  pillText: { color: colors.textMuted, fontSize: 11, letterSpacing: 1.5, textTransform: "uppercase" },
});
