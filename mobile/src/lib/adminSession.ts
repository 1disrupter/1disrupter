/**
 * Tiny admin-session helper for mobile. Mirrors the CRA/Next.js creds
 * (vibe2nite / nightowl) and persists a session flag in AsyncStorage so
 * the admin-only Brand Kit viewer stays unlocked across app restarts.
 * Non-admin users never see admin UI — the rest of the app is untouched.
 */
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useCallback, useEffect, useState } from "react";

const KEY = "v2n_admin_session";
const ADMIN_USER = "vibe2nite";
const ADMIN_PASS = "nightowl";

export function useAdminSession() {
  const [active, setActive] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let alive = true;
    AsyncStorage.getItem(KEY)
      .then((v) => { if (alive) setActive(!!v); })
      .catch(() => null)
      .finally(() => { if (alive) setReady(true); });
    return () => { alive = false; };
  }, []);

  const login = useCallback(async (user: string, pass: string) => {
    if (user.trim() === ADMIN_USER && pass === ADMIN_PASS) {
      await AsyncStorage.setItem(KEY, JSON.stringify({ user, t: Date.now() }));
      setActive(true);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(async () => {
    await AsyncStorage.removeItem(KEY);
    setActive(false);
  }, []);

  return { active, ready, login, logout };
}
