import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, TrendingUp, TrendingDown, Bell, Zap, RefreshCw } from "lucide-react";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

const MAX_EVENTS = 30;

const eventIcon = (type) => {
  if (type === "signal") return <Zap className="w-3.5 h-3.5 text-[#7B61FF]" />;
  if (type === "trade") return <TrendingUp className="w-3.5 h-3.5 text-[#00FF94]" />;
  if (type === "update") return <Bell className="w-3.5 h-3.5 text-[#FFB800]" />;
  return <Activity className="w-3.5 h-3.5 text-zinc-500" />;
};

const eventBadge = (type) => {
  const styles = {
    signal: "bg-[#7B61FF]/15 text-[#7B61FF]",
    trade: "bg-[#00FF94]/15 text-[#00FF94]",
    update: "bg-[#FFB800]/15 text-[#FFB800]",
  };
  return styles[type] || "bg-zinc-800 text-zinc-400";
};

const formatTime = (ts) => {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch { return ""; }
};

const LiveEventsFeed = () => {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  const connect = useCallback(() => {
    try {
      const wsUrl = API.replace("https://", "wss://").replace("http://", "ws://");
      const ws = new WebSocket(`${wsUrl}/api/ws/events`);

      ws.onopen = () => {
        setConnected(true);
        if (reconnectRef.current) clearTimeout(reconnectRef.current);
      };

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === "connected") return;

          setEvents(prev => [data, ...prev].slice(0, MAX_EVENTS));

          // Toast for signal events
          if (data.type === "signal") {
            toast(
              `${data.direction} ${data.pair}`,
              { description: `${data.confidence}% confidence — ${data.strategy}` }
            );
          }
        } catch { /* ignore malformed */ }
      };

      ws.onclose = () => {
        setConnected(false);
        reconnectRef.current = setTimeout(connect, 5000);
      };

      ws.onerror = () => {
        setConnected(false);
        ws.close();
      };

      wsRef.current = ws;
    } catch {
      setConnected(false);
      reconnectRef.current = setTimeout(connect, 5000);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (reconnectRef.current) clearTimeout(reconnectRef.current);
    };
  }, [connect]);

  return (
    <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="live-events-feed">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-[#7B61FF]" />
            <span className="text-sm font-semibold font-['Outfit']">Live Events</span>
          </div>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${connected ? 'bg-[#00FF94] animate-pulse' : 'bg-red-400'}`} data-testid="ws-status" />
            <span className="text-[10px] text-zinc-600">{connected ? 'Live' : 'Reconnecting...'}</span>
          </div>
        </div>

        <div className="space-y-1 max-h-[320px] overflow-y-auto scrollbar-thin" data-testid="events-list">
          {events.length === 0 ? (
            <div className="text-center py-8">
              <RefreshCw className="w-5 h-5 text-zinc-700 mx-auto mb-2 animate-spin" />
              <p className="text-xs text-zinc-600">Waiting for events...</p>
            </div>
          ) : (
            <AnimatePresence initial={false}>
              {events.map((ev, i) => (
                <motion.div
                  key={`${ev.timestamp}-${i}`}
                  initial={{ opacity: 0, x: -10, height: 0 }}
                  animate={{ opacity: 1, x: 0, height: "auto" }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex items-start gap-2 py-2 border-b border-zinc-800/20 last:border-0"
                  data-testid={`event-${i}`}
                >
                  <div className="mt-0.5 shrink-0">{eventIcon(ev.type)}</div>
                  <div className="flex-1 min-w-0">
                    {ev.type === "signal" && (
                      <div>
                        <span className="text-xs font-mono font-semibold text-white">{ev.pair}</span>
                        <Badge className={`text-[9px] ml-1.5 ${ev.direction === 'LONG' ? 'bg-[#00FF94]/15 text-[#00FF94]' : 'bg-red-500/15 text-red-400'}`}>
                          {ev.direction}
                        </Badge>
                        <span className="text-[10px] text-zinc-500 ml-1.5">{ev.confidence}% conf</span>
                        <p className="text-[10px] text-zinc-600 mt-0.5">{ev.strategy}</p>
                      </div>
                    )}
                    {ev.type === "trade" && (
                      <div>
                        <span className="text-xs font-mono text-zinc-300">{ev.pair}</span>
                        <span className={`text-xs font-mono ml-2 ${ev.pnl_pct >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {ev.pnl_pct >= 0 ? '+' : ''}{ev.pnl_pct}%
                        </span>
                        <Badge className={`text-[9px] ml-1.5 ${eventBadge('trade')}`}>closed</Badge>
                        <p className="text-[10px] text-zinc-600 mt-0.5">{ev.strategy}</p>
                      </div>
                    )}
                    {ev.type === "update" && (
                      <p className="text-[11px] text-zinc-400 leading-tight">{ev.message}</p>
                    )}
                  </div>
                  <span className="text-[9px] text-zinc-700 font-mono shrink-0">{formatTime(ev.timestamp)}</span>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default LiveEventsFeed;
