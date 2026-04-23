import { useEffect, useRef, useState } from "react";
import { API_BASE } from "@/config";

type VibeUpdate = {
  type: "snapshot" | "vibe_update" | "heartbeat";
  venue_id?: string;
  name?: string;
  vibe_score?: number;
  crowd_level?: string;
  external_signals?: Record<string, number>;
  last_updated?: string;
};

function toWs(url: string): string {
  return url.replace(/^http:/, "ws:").replace(/^https:/, "wss:");
}

/** Connect to /ws/vibe/{venue_id}. Returns latest frame + connection status.
 * Auto-reconnects with linear backoff. Safe to unmount — sockets are closed. */
export function useVibePulse(venue_id: string | undefined): {
  live: boolean;
  last: VibeUpdate | null;
} {
  const [live, setLive] = useState(false);
  const [last, setLast] = useState<VibeUpdate | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const cancelled = useRef(false);

  useEffect(() => {
    if (!venue_id) return;
    cancelled.current = false;

    const connect = () => {
      if (cancelled.current) return;
      const url = `${toWs(API_BASE)}/ws/vibe/${venue_id}`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => setLive(true);
      ws.onmessage = (e) => {
        try {
          const frame = JSON.parse(typeof e.data === "string" ? e.data : "") as VibeUpdate;
          if (frame.type === "heartbeat") return;
          setLast(frame);
        } catch { /* ignore bad frames */ }
      };
      ws.onerror = () => { /* swallow — onclose will retry */ };
      ws.onclose = () => {
        setLive(false);
        if (!cancelled.current) {
          timer.current = setTimeout(connect, 2500);
        }
      };
    };

    connect();

    return () => {
      cancelled.current = true;
      if (timer.current) clearTimeout(timer.current);
      try { wsRef.current?.close(); } catch { /* noop */ }
    };
  }, [venue_id]);

  return { live, last };
}
