"use client";
import { useEffect, useState, useCallback } from "react";

const KEY = "v2n_admin_session";

export interface Session {
  user: string;
  t: number;
}

export function useAuth() {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem(KEY) : null;
      setSession(raw ? (JSON.parse(raw) as Session) : null);
    } catch {
      setSession(null);
    } finally {
      setReady(true);
    }
  }, []);

  const login = useCallback((user: string, pass: string) => {
    if (user === "vibe2nite" && pass === "nightowl") {
      const s: Session = { user, t: Date.now() };
      localStorage.setItem(KEY, JSON.stringify(s));
      setSession(s);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(KEY);
    setSession(null);
  }, []);

  return { session, ready, login, logout };
}
