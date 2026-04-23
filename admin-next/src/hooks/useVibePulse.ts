"use client";
import { useEffect, useRef, useState } from "react";
import { API_BASE } from "@/lib/api";

type VibeUpdate = {
  type: "snapshot" | "vibe_update" | "heartbeat";
  venue_id?: string;
  vibe_score?: number;
  crowd_level?: string;
  external_signals?: Record<string, number>;
  last_updated?: string;
};

function toWs(url: string): string {
  if (!url) return "";
  return url.replace(/^http:/, "ws:").replace(/^https:/, "wss:");
}

export function useVibePulse(venue_id: string | undefined) {
  const [live, setLive] = useState(false);
  const [last, setLast] = useState<VibeUpdate | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const retry = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelled = useRef(false);

  useEffect(() => {
    if (!venue_id || typeof window === "undefined") return;
    cancelled.current = false;

    const connect = () => {
      if (cancelled.current) return;
      try {
        const url = `${toWs(API_BASE || window.location.origin)}/ws/vibe/${venue_id}`;
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => setLive(true);
        ws.onmessage = (e) => {
          try {
            const frame = JSON.parse(e.data) as VibeUpdate;
            if (frame.type === "heartbeat") return;
            setLast(frame);
          } catch { /* ignore malformed */ }
        };
        ws.onerror = () => { /* onclose handles retry */ };
        ws.onclose = () => {
          setLive(false);
          if (!cancelled.current) retry.current = setTimeout(connect, 2500);
        };
      } catch {
        retry.current = setTimeout(connect, 2500);
      }
    };
    connect();
    return () => {
      cancelled.current = true;
      if (retry.current) clearTimeout(retry.current);
      try { wsRef.current?.close(); } catch { /* noop */ }
    };
  }, [venue_id]);

  return { live, last };
}
