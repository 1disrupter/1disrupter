import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wifi, WifiOff, Activity, TrendingUp, AlertTriangle, ArrowUpRight, ArrowDownRight, RefreshCw, Eye } from 'lucide-react';
import { useDemoMode } from '../contexts/DemoModeContext';

const API_WS = process.env.REACT_APP_BACKEND_URL?.replace(/^http/, 'ws');

const typeStyles = {
  signal: { icon: TrendingUp, color: '#7B61FF', label: 'Signal' },
  trade: { icon: Activity, color: '#00FF94', label: 'Trade' },
  update: { icon: RefreshCw, color: '#FFB800', label: 'Update' },
};

const LiveEventsFeed = () => {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const [wsDemo, setWsDemo] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const { isDemoMode } = useDemoMode();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    try {
      const ws = new WebSocket(`${API_WS}/api/ws/events`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data);
          if (data.type === 'connected') {
            setWsDemo(data.demo_mode);
            return;
          }
          setEvents((prev) => [{ ...data, _id: Date.now() + Math.random() }, ...prev].slice(0, 30));
        } catch { /* ignore bad frames */ }
      };

      ws.onclose = () => {
        setConnected(false);
        reconnectTimer.current = setTimeout(connect, 5000);
      };

      ws.onerror = () => ws.close();
    } catch {
      reconnectTimer.current = setTimeout(connect, 5000);
    }
  }, []);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimer.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const isLive = !isDemoMode && wsDemo === false;

  return (
    <div className="bg-[#0A0A0A] border border-zinc-800 rounded-xl p-4" data-testid="live-events-feed">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-[#7B61FF]" />
          <h3 className="text-sm font-semibold text-white">Live Events Feed</h3>
          {isLive && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#00FF94]/10 text-[#00FF94] border border-[#00FF94]/20">
              LIVE
            </span>
          )}
          {(isDemoMode || wsDemo) && (
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#7B61FF]/10 text-[#7B61FF] border border-[#7B61FF]/20 flex items-center gap-1">
              <Eye className="w-2.5 h-2.5" /> DEMO
            </span>
          )}
        </div>
        <div className="flex items-center gap-1.5">
          {connected ? (
            <Wifi className="w-3.5 h-3.5 text-[#00FF94]" />
          ) : (
            <WifiOff className="w-3.5 h-3.5 text-zinc-500 animate-pulse" />
          )}
          <span className="text-[10px] text-zinc-500 font-mono">
            {connected ? 'Connected' : 'Reconnecting...'}
          </span>
        </div>
      </div>

      {/* Events */}
      <div className="space-y-1.5 max-h-[320px] overflow-y-auto scrollbar-thin">
        <AnimatePresence initial={false}>
          {events.length === 0 && (
            <div className="text-center py-8 text-zinc-600 text-xs">
              Waiting for events...
            </div>
          )}
          {events.map((ev) => {
            const style = typeStyles[ev.type] || typeStyles.update;
            const Icon = style.icon;
            const isPositive = ev.pnl_pct > 0;

            return (
              <motion.div
                key={ev._id}
                initial={{ opacity: 0, x: -20, height: 0 }}
                animate={{ opacity: 1, x: 0, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.25 }}
                className="flex items-center gap-2.5 p-2.5 rounded-lg bg-[#050505] border border-zinc-800/50 hover:border-zinc-700/50 transition-colors"
                data-testid={`event-${ev.type}`}
              >
                <div
                  className="w-7 h-7 rounded-md flex items-center justify-center shrink-0"
                  style={{ backgroundColor: `${style.color}15`, border: `1px solid ${style.color}30` }}
                >
                  <Icon className="w-3.5 h-3.5" style={{ color: style.color }} />
                </div>

                <div className="flex-1 min-w-0">
                  {ev.type === 'signal' && (
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-white">{ev.pair}</span>
                      <span
                        className="text-[10px] font-mono px-1 py-0.5 rounded"
                        style={{
                          color: ev.direction === 'LONG' ? '#00FF94' : '#FF6B6B',
                          backgroundColor: ev.direction === 'LONG' ? 'rgba(0,255,148,.1)' : 'rgba(255,107,107,.1)',
                        }}
                      >
                        {ev.direction}
                      </span>
                      <span className="text-[10px] text-zinc-500 font-mono">{ev.confidence}%</span>
                      {ev.is_real && <span className="text-[9px] text-[#00FF94] font-mono">REAL</span>}
                    </div>
                  )}
                  {ev.type === 'trade' && (
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-semibold text-white">{ev.pair}</span>
                      {isPositive ? (
                        <ArrowUpRight className="w-3 h-3 text-[#00FF94]" />
                      ) : (
                        <ArrowDownRight className="w-3 h-3 text-[#FF6B6B]" />
                      )}
                      <span
                        className="text-[10px] font-mono font-semibold"
                        style={{ color: isPositive ? '#00FF94' : '#FF6B6B' }}
                      >
                        {isPositive ? '+' : ''}{ev.pnl_pct}%
                      </span>
                      {ev.is_real && <span className="text-[9px] text-[#00FF94] font-mono">REAL</span>}
                    </div>
                  )}
                  {ev.type === 'update' && (
                    <p className="text-xs text-zinc-400 truncate">{ev.message}</p>
                  )}
                  <p className="text-[10px] text-zinc-600 font-mono mt-0.5">{ev.strategy || ''}</p>
                </div>

                <span className="text-[10px] text-zinc-600 font-mono shrink-0">
                  {ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </span>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default LiveEventsFeed;
