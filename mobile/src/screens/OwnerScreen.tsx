/**
 * Owner-scoped screen for mobile.
 * - Auth: `X-Owner-Key` header, persisted via AsyncStorage.
 * - Mirrors the CRA /owner page shape: vibe card, external signals, inbox,
 *   social-handle editor.
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import {
  ActivityIndicator, FlatList, Pressable, RefreshControl,
  ScrollView, StyleSheet, Text, TextInput, View,
} from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius, spacing } from "@/theme";
import { API_BASE } from "@/config";
import { GlowButton } from "@/components/GlowButton";
import { useOwnerKey } from "@/lib/ownerKey";

type OwnerMe = {
  owner: { email: string; name: string; claim_id: string; verified_at: string | null };
  venues: Array<{
    id: string; name: string; category: string;
    vibe_score: number;
    crowd_level: string | null;
    last_updated: string | null;
    external_signals: Record<string, number> | null;
    social_handles: { instagram?: string; tiktok?: string };
  }>;
};

type InboxItem = {
  id: string; kind: string; title: string; body: string;
  data: Record<string, any>; created_at: string;
};

async function fetchOwner<T>(path: string, key: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Owner-Key": key,
      ...(init.headers || {}),
    },
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
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [igHandle, setIgHandle] = useState("");
  const [ttHandle, setTtHandle] = useState("");
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
      const h = m.venues?.[0]?.social_handles || {};
      setIgHandle(h.instagram || "");
      setTtHandle(h.tiktok || "");
    } catch (e: any) {
      setError(e.message || "Invalid key");
      setMe(null);
    } finally {
      setLoading(false); setRefreshing(false);
    }
  }, []);

  useEffect(() => { if (key) load(key); }, [key, load]);

  const signIn = async () => {
    const k = input.trim();
    if (!k) { setError("Paste your owner key"); return; }
    await save(k);
  };

  const onRefresh = async () => {
    if (!key) return;
    setRefreshing(true); await load(key);
  };

  const saveHandles = async () => {
    if (!key) return;
    setSaving(true);
    try {
      await fetchOwner("/owner/venue/handles", key, {
        method: "PUT",
        body: JSON.stringify({
          instagram: igHandle.trim() || null,
          tiktok: ttHandle.trim() || null,
        }),
      });
      await load(key);
    } catch (e: any) {
      setError(e.message || "Couldn't save");
    } finally {
      setSaving(false);
    }
  };

  const venue = me?.venues?.[0];
  const signalRows = useMemo(() => {
    const s = venue?.external_signals || null;
    if (!s) return [];
    return [
      ["Google busyness", s.google_score],
      ["Social", s.social_score],
      ["Events", s.event_score],
      ["Time-of-day", s.time_score],
      ["User votes", s.user_votes_score],
    ] as const;
  }, [venue]);

  // ---- render guard states --------------------------------------------------
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
            value={input}
            onChangeText={setInput}
            placeholder="vk_xxxxxxxxxxxx…"
            placeholderTextColor={colors.textFaint}
            autoCapitalize="none"
            autoCorrect={false}
            style={styles.input}
            testID="owner-key-input"
          />
          {error && <Text style={styles.err}>{error}</Text>}
          <GlowButton
            label="Sign in"
            variant="pink"
            size="md"
            onPress={signIn}
            style={{ marginTop: spacing.md }}
            testID="owner-key-submit"
          />
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
            <Text style={{ color: colors.textMuted, fontSize: 12, textTransform: "uppercase", letterSpacing: 2 }}>
              Sign out
            </Text>
          </Pressable>
        </View>

        {loading && !me && (
          <ActivityIndicator color={colors.primaryGlow} style={{ marginTop: spacing.lg }} />
        )}
        {error && !me && <Text style={styles.err}>{error}</Text>}

        {venue && (
          <>
            <Text style={styles.h1}>{venue.name}</Text>
            <Text style={[styles.body, { color: colors.textMuted, textTransform: "uppercase", letterSpacing: 2 }]}>
              {venue.category}
            </Text>

            <View style={styles.vibeCard} testID="owner-vibe-card-mobile">
              <Text style={styles.vibeNum}>{(venue.vibe_score ?? 0).toFixed(2)}</Text>
              <Text style={styles.vibeLabel}>LIVE VIBE SCORE</Text>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 8, marginTop: 6 }}>
                <View style={[styles.chip, { backgroundColor: colors.primary + "33", borderColor: colors.primaryGlow }]}>
                  <Text style={{ color: colors.text, fontSize: 10, letterSpacing: 2, textTransform: "uppercase" }}>
                    {venue.crowd_level || "—"}
                  </Text>
                </View>
                <Text style={{ color: colors.textFaint, fontSize: 11, fontFamily: "Courier" }}>
                  {venue.last_updated ? new Date(venue.last_updated).toLocaleTimeString() : "—"}
                </Text>
              </View>
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
            <Text style={[styles.body, { color: colors.textFaint, fontSize: 12 }]}>
              Wire IG / TikTok to feed the real signal engine (used when platform keys are configured).
            </Text>
            <TextInput
              value={igHandle}
              onChangeText={setIgHandle}
              placeholder="@laterraza"
              placeholderTextColor={colors.textFaint}
              autoCapitalize="none"
              style={[styles.input, { marginTop: spacing.sm }]}
              testID="owner-handle-ig"
            />
            <TextInput
              value={ttHandle}
              onChangeText={setTtHandle}
              placeholder="@terraza"
              placeholderTextColor={colors.textFaint}
              autoCapitalize="none"
              style={[styles.input, { marginTop: spacing.xs }]}
              testID="owner-handle-tt"
            />
            <GlowButton
              label={saving ? "…" : "Save handles"}
              variant="primary"
              size="md"
              disabled={saving}
              onPress={saveHandles}
              style={{ marginTop: spacing.sm }}
              testID="owner-handles-save"
            />

            <Text style={styles.section}>INBOX</Text>
            {inbox.length === 0 ? (
              <Text style={[styles.body, { color: colors.textFaint }]}>No messages yet.</Text>
            ) : (
              <FlatList
                scrollEnabled={false}
                data={inbox}
                keyExtractor={(i) => i.id}
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
  h1: { color: colors.text, fontSize: 30, fontWeight: "900", letterSpacing: 2, marginTop: 4 },
  body: { color: colors.text, marginTop: 6, lineHeight: 20 },
  err: { color: colors.pink, marginTop: 8, fontSize: 12 },
  input: {
    marginTop: spacing.sm, padding: 12, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border, backgroundColor: "rgba(255,255,255,0.03)",
    color: colors.text, fontSize: 14,
  },
  vibeCard: {
    marginTop: spacing.lg, padding: spacing.lg,
    backgroundColor: colors.card,
    borderRadius: radius.xl,
    borderWidth: 1, borderColor: colors.primaryGlow,
  },
  vibeNum: { color: colors.text, fontFamily: "Courier", fontSize: 46 },
  vibeLabel: { color: colors.textMuted, fontSize: 10, letterSpacing: 2.5, textTransform: "uppercase", marginTop: 2 },
  chip: {
    borderRadius: 999, paddingHorizontal: 10, paddingVertical: 4,
    borderWidth: 1,
  },
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
    padding: spacing.sm,
    backgroundColor: colors.card,
    borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border,
  },
  inboxKind: {
    color: colors.primaryGlow, fontSize: 9, letterSpacing: 2, textTransform: "uppercase",
  },
  inboxTitle: { color: colors.text, fontSize: 14, fontWeight: "700", marginTop: 2 },
  inboxBody: { color: colors.textMuted, fontSize: 12, marginTop: 4, lineHeight: 18 },
});
