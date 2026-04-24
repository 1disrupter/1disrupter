/**
 * Owner API key storage helper for mobile.
 * Mirrors the CRA localStorage pattern using AsyncStorage.
 */
import AsyncStorage from "@react-native-async-storage/async-storage";
import { useCallback, useEffect, useState } from "react";

const KEY = "v2n_owner_key";

export function useOwnerKey() {
  const [key, setKey] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    let alive = true;
    AsyncStorage.getItem(KEY)
      .then((v) => { if (alive) setKey(v); })
      .catch(() => null)
      .finally(() => { if (alive) setReady(true); });
    return () => { alive = false; };
  }, []);

  const save = useCallback(async (k: string) => {
    await AsyncStorage.setItem(KEY, k);
    setKey(k);
  }, []);

  const clear = useCallback(async () => {
    await AsyncStorage.removeItem(KEY);
    setKey(null);
  }, []);

  return { key, ready, save, clear };
}
