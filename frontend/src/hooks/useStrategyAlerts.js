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
  const [connected, setConnected] = useState(null); // null = no attempt, true = connected, false = disconnected
  const [upgradeRequired, setUpgradeRequired] = useState(false);
  const wsRef = useRef(null);
  const reconnectCount = useRef(0);
  const reconnectTimer = useRef(null);
  const openedAtRef = useRef(0);
  const failedFastCount = useRef(0);
  const upgradeRequiredRef = useRef(false);

  const clearAlerts = useCallback(() => setAlerts([]), []);

  useEffect(() => {
    let clientId;
    if (isDemoMode) {
      clientId = `demo-${Date.now()}`;
    } else if (isAuthenticated && user && tokens?.access_token) {
      const tier = user.user_tier || (user.is_pro || user.is_elite ? "pro" : "free");
      clientId = `${user.id}:${tier}`;
    } else {
      // No connection needed — keep connected as null (not false)
      return;
    }

    const wsUrl = BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://");
    const fullUrl = `${wsUrl}/api/ws/alerts/${clientId}`;

    const connect = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) return;
      
      // Don't reconnect if upgrade is required (free user)
      if (upgradeRequiredRef.current) {
        console.debug("[WS] Upgrade required, not reconnecting");
        return;
      }

      // Stop if too many rapid failures (server likely down)
      if (failedFastCount.current >= 5) {
        console.debug("[WS] Server appears offline, pausing reconnect");
        setConnected(false);
        // Retry once after 30s
        reconnectTimer.current = setTimeout(() => {
          failedFastCount.current = 0;
          reconnectCount.current = 0;
          connect();
        }, 30000);
        return;
      }

      try {
        const ws = new WebSocket(fullUrl);
        wsRef.current = ws;

        ws.onopen = () => {
          openedAtRef.current = Date.now();
          setConnected(true);
          setUpgradeRequired(false);
          upgradeRequiredRef.current = false;
          reconnectCount.current = 0;
          failedFastCount.current = 0;
          console.debug("[WS] Connected", { url: fullUrl });
          trackEvent("ws_connect", { endpoint: "alerts" });
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === "connected") return;
            if (data.type === "upgrade_required") { 
              upgradeRequiredRef.current = true;
              setUpgradeRequired(true); 
              return; 
            }
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
            // Ignore parse errors
          }
        };

        ws.onclose = (event) => {
          console.debug("[WS] Closed", { code: event.code, reason: event.reason });
          wsRef.current = null;
          trackEvent("ws_disconnect", { endpoint: "alerts", code: event.code });

          // Intentional close (cleanup) - don't show reconnecting banner
          if (event.code === 1000) return;
          
          if (event.code === 4003) { 
            upgradeRequiredRef.current = true;
            setUpgradeRequired(true); 
            // Keep connected as null for free users - they shouldn't see reconnecting banner
            setConnected(null); 
            return; 
          }
          
          // Only set disconnected for unexpected closes
          setConnected(false);

          // Detect rapid close (< 500ms = server likely rejecting)
          const lifespan = Date.now() - openedAtRef.current;
          if (lifespan < 500 && openedAtRef.current > 0) {
            failedFastCount.current += 1;
          }

          // Exponential backoff reconnect
          if (reconnectCount.current < MAX_RECONNECT_ATTEMPTS) {
            reconnectCount.current += 1;
            const baseDelay = failedFastCount.current >= 3 ? 8000 : RECONNECT_BASE_DELAY;
            const delay = baseDelay * Math.pow(1.5, reconnectCount.current - 1);
            console.debug("[WS] Reconnecting in", delay, "ms, attempt", reconnectCount.current);
            reconnectTimer.current = setTimeout(connect, delay);
          }
        };

        ws.onerror = () => {
          console.debug("[WS] Error on", fullUrl);
        };
      } catch (e) {
        console.debug("[WS] Failed to create WebSocket:", e);
      }
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
        failedFastCount.current = 0;
        connect();
      }
    };
    document.addEventListener("visibilitychange", visibilityHandler);

    // Reconnect on network recovery
    const onlineHandler = () => {
      if (wsRef.current?.readyState !== WebSocket.OPEN) {
        reconnectCount.current = 0;
        failedFastCount.current = 0;
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
        wsRef.current.close(1000, "cleanup");
        wsRef.current = null;
      }
    };
  }, [isDemoMode, isAuthenticated, user, tokens]);

  return { alerts, connected, upgradeRequired, clearAlerts };
};

export default useStrategyAlerts;
