import React, { useState } from "react";
import { Linking, Modal, Pressable, ScrollView, StyleSheet, Text, TextInput, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors, radius, spacing } from "@/theme";
import { API_BASE } from "@/config";
import { Logo, LogoPin } from "@/components/Logo";
import { GlowButton } from "@/components/GlowButton";
import { useAdminSession } from "@/lib/adminSession";
import BrandKitScreen from "@/screens/BrandKitScreen";
import OwnerScreen from "@/screens/OwnerScreen";

export default function SettingsScreen() {
  const admin = useAdminSession();
  const [showLogin, setShowLogin] = useState(false);
  const [showBrand, setShowBrand] = useState(false);
  const [showOwner, setShowOwner] = useState(false);

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

        {/* ---------------------------------------------------------------- */}
        {/* Owner console — public entry point (opt-in, auth via owner key)  */}
        {/* ---------------------------------------------------------------- */}
        <View style={[styles.card, styles.ownerCard]} testID="mobile-owner-card">
          <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
            <Ionicons name="shield-checkmark-outline" size={14} color={colors.pink} />
            <Text style={[styles.sectionLabel, { color: colors.pink }]}>Venue owners</Text>
          </View>
          <Text style={[styles.body, { color: colors.textFaint, fontSize: 12 }]}>
            Verified your claim? Open the owner console to see your venue's live signals, handles and inbox.
          </Text>
          <GlowButton
            label="Open owner console"
            variant="pink"
            size="md"
            style={{ marginTop: spacing.sm }}
            onPress={() => setShowOwner(true)}
            testID="mobile-open-owner-btn"
          />
        </View>

        {/* ------------------------------------------------------------ */}
        {/* Admin section — collapsed for regular users, expanded only   */}
        {/* once an admin session is active. Non-admin UI is untouched.   */}
        {/* ------------------------------------------------------------ */}
        {admin.ready && (
          <View style={[styles.card, styles.adminCard]} testID="mobile-admin-settings-card">
            <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
              <Ionicons name="shield-checkmark" size={14} color={colors.primaryGlow} />
              <Text style={styles.sectionLabel}>Admin tools</Text>
            </View>
            {admin.active ? (
              <>
                <Text style={[styles.body, { color: colors.textMuted, fontSize: 12 }]}>
                  Signed in as admin. Internal design & settings surfaces are unlocked.
                </Text>
                <GlowButton
                  label="Open Brand Kit"
                  variant="primary"
                  size="md"
                  style={{ marginTop: spacing.sm }}
                  onPress={() => setShowBrand(true)}
                  testID="mobile-open-brandkit-btn"
                />
                <GlowButton
                  label="Sign out of admin"
                  variant="ghost"
                  size="sm"
                  style={{ marginTop: spacing.xs }}
                  onPress={() => admin.logout()}
                  testID="mobile-admin-logout-btn"
                />
              </>
            ) : (
              <>
                <Text style={[styles.body, { color: colors.textFaint, fontSize: 12 }]}>
                  Curators & designers: unlock internal tools (Brand Kit, settings).
                </Text>
                <GlowButton
                  label="Enter admin mode"
                  variant="secondary"
                  size="md"
                  style={{ marginTop: spacing.sm }}
                  onPress={() => setShowLogin(true)}
                  testID="mobile-admin-login-btn"
                />
              </>
            )}
          </View>
        )}

        <Text style={{ textAlign: "center", color: colors.textFaint, marginTop: spacing.xl }}>
          v1.0.0 · © Vibe2Nite
        </Text>
      </ScrollView>

      {/* Admin login modal */}
      <AdminLoginModal
        visible={showLogin}
        onClose={() => setShowLogin(false)}
        onSubmit={async (u, p) => {
          const ok = await admin.login(u, p);
          if (ok) setShowLogin(false);
          return ok;
        }}
      />

      {/* Brand Kit fullscreen modal (admin only) */}
      <Modal visible={showBrand && admin.active} animationType="slide" onRequestClose={() => setShowBrand(false)}>
        <View style={{ flex: 1, backgroundColor: colors.bg }}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>BRAND KIT</Text>
            <Pressable onPress={() => setShowBrand(false)} testID="mobile-brandkit-close">
              <Ionicons name="close" size={24} color={colors.text} />
            </Pressable>
          </View>
          <BrandKitScreen />
        </View>
      </Modal>

      {/* Owner console fullscreen modal (public opt-in) */}
      <Modal visible={showOwner} animationType="slide" onRequestClose={() => setShowOwner(false)}>
        <View style={{ flex: 1, backgroundColor: colors.bg }}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>OWNER CONSOLE</Text>
            <Pressable onPress={() => setShowOwner(false)} testID="mobile-owner-close">
              <Ionicons name="close" size={24} color={colors.text} />
            </Pressable>
          </View>
          <OwnerScreen />
        </View>
      </Modal>
    </SafeAreaView>
  );
}

function AdminLoginModal({
  visible, onClose, onSubmit,
}: { visible: boolean; onClose: () => void; onSubmit: (u: string, p: string) => Promise<boolean> }) {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    setBusy(true); setErr(null);
    const ok = await onSubmit(user, pass);
    setBusy(false);
    if (!ok) setErr("Invalid credentials.");
    else { setUser(""); setPass(""); }
  };

  return (
    <Modal visible={visible} transparent animationType="fade" onRequestClose={onClose}>
      <Pressable style={styles.modalBackdrop} onPress={onClose}>
        <Pressable style={styles.loginCard} onPress={(e) => e.stopPropagation()}>
          <Text style={styles.modalTitle}>ADMIN CONSOLE</Text>
          <Text style={{ color: colors.textFaint, fontSize: 12, marginTop: 6 }}>
            Same credentials as the web console.
          </Text>
          <TextInput
            value={user}
            onChangeText={(t) => { setUser(t); setErr(null); }}
            placeholder="username"
            placeholderTextColor={colors.textFaint}
            autoCapitalize="none"
            autoCorrect={false}
            style={styles.loginInput}
            testID="mobile-admin-user"
          />
          <TextInput
            value={pass}
            onChangeText={(t) => { setPass(t); setErr(null); }}
            placeholder="password"
            placeholderTextColor={colors.textFaint}
            secureTextEntry
            autoCapitalize="none"
            style={[styles.loginInput, { marginTop: 10 }]}
            testID="mobile-admin-pass"
          />
          {err && <Text style={{ color: colors.pink, fontSize: 12, marginTop: 6 }}>{err}</Text>}
          <View style={{ flexDirection: "row", gap: 10, marginTop: spacing.md }}>
            <GlowButton label="Cancel" variant="secondary" size="md" onPress={onClose} style={{ flex: 1 }} />
            <GlowButton
              label={busy ? "…" : "Enter"}
              variant="primary"
              size="md"
              disabled={busy}
              onPress={submit}
              style={{ flex: 1 }}
              testID="mobile-admin-submit"
            />
          </View>
        </Pressable>
      </Pressable>
    </Modal>
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
  adminCard: {
    borderColor: colors.primaryGlow,
    backgroundColor: "rgba(138,43,226,0.10)",
  },
  ownerCard: {
    borderColor: colors.pink,
    backgroundColor: "rgba(255,46,196,0.08)",
  },
  sectionLabel: { color: colors.primaryGlow, fontSize: 10, letterSpacing: 2.5, textTransform: "uppercase" },
  body: { color: colors.text, marginTop: 6, lineHeight: 20 },

  modalHeader: {
    flexDirection: "row", justifyContent: "space-between", alignItems: "center",
    paddingHorizontal: spacing.md, paddingTop: spacing.xl, paddingBottom: spacing.sm,
    borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  modalTitle: { color: colors.text, fontSize: 22, fontWeight: "900", letterSpacing: 3 },

  modalBackdrop: {
    flex: 1, alignItems: "center", justifyContent: "center",
    backgroundColor: "rgba(5,5,10,0.82)", padding: spacing.md,
  },
  loginCard: {
    width: "100%", maxWidth: 420, padding: spacing.lg,
    backgroundColor: colors.bg, borderRadius: radius.xl,
    borderWidth: 1, borderColor: colors.primaryGlow,
  },
  loginInput: {
    marginTop: spacing.md, padding: 12, borderRadius: radius.md,
    borderWidth: 1, borderColor: colors.border, backgroundColor: "rgba(255,255,255,0.03)",
    color: colors.text, fontSize: 14,
  },
});
