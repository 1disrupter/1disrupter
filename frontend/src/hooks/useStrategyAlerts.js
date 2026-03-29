import { useState, useEffect, useRef, useCallback } from "react";
import { toast } from "sonner";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { BACKEND_URL } from "../lib/constants";

const MAX_ALERTS = 50;
const RECONNECT_DELAY = 3000;
const MAX_RECONNECT_ATTEMPTS = 5;

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
    // Determine connection parameters
    let clientId;
    if (isDemoMode) {
      clientId = `demo-${Date.now()}`;
    } else if (isAuthenticated && user && tokens?.access_token) {
      const tier = user.user_tier || (user.is_pro || user.is_elite ? "pro" : "free");
      clientId = `${user.id}:${tier}`;
    } else {
      return; // No connection without auth or demo
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
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === "connected") {
            // Connection confirmed
            return;
          }

          if (data.type === "upgrade_required") {
            setUpgradeRequired(true);
            return;
          }

          if (data.type === "heartbeat" || data.type === "pong") {
            return;
          }

          if (data.type === "strategy_alert") {
            setAlerts((prev) => [data, ...prev].slice(0, MAX_ALERTS));
            toast(data.message, {
              description: data.asset || data.strategy_name || "",
              duration: 6000,
            });
          }
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onclose = (event) => {
        setConnected(false);
        wsRef.current = null;

        // Don't reconnect if intentionally closed or upgrade required
        if (event.code === 4003) {
          setUpgradeRequired(true);
          return;
        }

        // Reconnect with backoff
        if (reconnectCount.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectCount.current += 1;
          const delay = RECONNECT_DELAY * reconnectCount.current;
          reconnectTimer.current = setTimeout(connect, delay);
        }
      };

      ws.onerror = () => {
        // onclose will handle reconnection
      };
    };

    connect();

    // Ping every 45 seconds to keep alive
    const pingInterval = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "ping" }));
      }
    }, 45000);

    return () => {
      clearInterval(pingInterval);
      clearTimeout(reconnectTimer.current);
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [isDemoMode, isAuthenticated, user, tokens]);

  return { alerts, connected, upgradeRequired, clearAlerts };
};

export default useStrategyAlerts;
