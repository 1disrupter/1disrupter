import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { BACKEND_URL } from "../lib/constants";
import { trackEvent } from "../lib/tracking";

const MAX_ALERTS = 50;
const RECONNECT_BASE_DELAY = 2000;
const MAX_RECONNECT_ATTEMPTS = 8;

const useStrategyAlerts = () => {
  const { isDemoMode } = useDemoMode();
  const { user, tokens, isAuthenticated } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const [upgradeRequired, setUpgradeRequired] = useState(false);
  const wsRef = useRef(null);
  const reconnectCount = useRef(0);
  const reconnectTimer = useRef(null);

  const clearAlerts = useCallback(() => setAlerts([]), []);

  useEffect(() => {
    let clientId;
    if (isDemoMode) {
      clientId = `demo-${Date.now()}`;
    } else if (isAuthenticated && user && tokens?.access_token) {
      const tier = user.user_tier || (user.is_pro || user.is_elite ? "pro" : "free");
      clientId = `${user.id}:${tier}`;
    } else {
      return;
    }

    const wsUrl = BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://");
    const fullUrl = `${wsUrl}/api/ws/alerts/${clientId}`;

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;

      const ws = new WebSocket(fullUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnected(true);
        setUpgradeRequired(false);
        reconnectCount.current = 0;
        trackEvent("ws_connect", { endpoint: "alerts" });
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "connected") return;
          if (data.type === "upgrade_required") { setUpgradeRequired(true); return; }
          if (data.type === "heartbeat" || data.type === "pong") return;

          if (data.type === "strategy_alert") {
            setAlerts((prev) => [data, ...prev].slice(0, MAX_ALERTS));
            trackEvent("signal", { strategy_id: data.strategy_id, action: data.action });
            toast(data.message, {
              description: data.asset || data.strategy_name || "",
              duration: 6000,
            });
          }
        } catch {
          // Ignore
        }
      };

      ws.onclose = (event) => {
        setConnected(false);
        wsRef.current = null;
        trackEvent("ws_disconnect", { endpoint: "alerts", code: event.code });

        if (event.code === 4003) { setUpgradeRequired(true); return; }

        // Exponential backoff reconnect
        if (reconnectCount.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectCount.current += 1;
          const delay = RECONNECT_BASE_DELAY * Math.pow(1.5, reconnectCount.current - 1);
          reconnectTimer.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {};
    };

    connect();

    // Ping every 45s
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "ping" }));
      }
    }, 45000);

    // Reconnect on visibility change (app resume)
    const visibilityHandler = () => {
      if (!document.hidden && wsRef.current?.readyState !== WebSocket.OPEN) {
        reconnectCount.current = 0;
        connect();
      }
    };
    document.addEventListener("visibilitychange", visibilityHandler);

    // Reconnect on network recovery
    const onlineHandler = () => {
      if (wsRef.current?.readyState !== WebSocket.OPEN) {
        reconnectCount.current = 0;
        connect();
      }
    };
    window.addEventListener("online", onlineHandler);

    return () => {
      clearInterval(pingInterval);
      clearTimeout(reconnectTimer.current);
      document.removeEventListener("visibilitychange", visibilityHandler);
      window.removeEventListener("online", onlineHandler);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [isDemoMode, isAuthenticated, user, tokens]);

  return { alerts, connected, upgradeRequired, clearAlerts };
};

export default useStrategyAlerts;
