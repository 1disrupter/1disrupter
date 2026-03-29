import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Bell, Check, TrendingUp, UserPlus, Radio } from "lucide-react";
import { Badge } from "./ui/badge";
import axios from "axios";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { API } from "../lib/constants";
import useStrategyAlerts from "../hooks/useStrategyAlerts";

const typeIcon = { signal: TrendingUp, follow: UserPlus, strategy_alert: Radio };

const NotificationBell = () => {
  const { isDemoMode } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;
  const [open, setOpen] = useState(false);
  const [items, setItems] = useState([]);
  const [unread, setUnread] = useState(0);
  const ref = useRef(null);
  const { alerts: liveAlerts } = useStrategyAlerts();

  const load = async () => {
    try {
      const url = isDemoMode ? `${API}/notifications/inbox/demo` : `${API}/notifications/inbox`;
      const headers = !isDemoMode && token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.get(url, { headers });
      if (res.data?.success) {
        setItems(res.data.notifications || []);
        setUnread(res.data.unread_count || 0);
      }
    } catch {}
  };

  useEffect(() => { load(); const iv = setInterval(load, 30000); return () => clearInterval(iv); }, [isDemoMode, token]);

  // Bump unread when a live alert arrives
  const prevAlertCount = useRef(0);
  useEffect(() => {
    if (liveAlerts.length > prevAlertCount.current) {
      const diff = liveAlerts.length - prevAlertCount.current;
      setUnread(prev => prev + diff);
      // Prepend live alerts to items
      const newItems = liveAlerts.slice(0, diff).map(a => ({
        id: `live-${a.timestamp}-${Math.random()}`,
        strategy_id: a.strategy_id || "",
        message: a.message,
        type: "signal",
        read: false,
        created_at: a.timestamp || new Date().toISOString(),
      }));
      setItems(prev => [...newItems, ...prev].slice(0, 30));
    }
    prevAlertCount.current = liveAlerts.length;
  }, [liveAlerts]);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const markRead = async (id) => {
    if (isDemoMode) {
      setItems(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      setUnread(prev => Math.max(0, prev - 1));
      return;
    }
    try {
      await axios.post(`${API}/notifications/${id}/read`, {}, { headers: { Authorization: `Bearer ${token}` } });
      setItems(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
      setUnread(prev => Math.max(0, prev - 1));
    } catch {}
  };

  const markAllRead = async () => {
    if (isDemoMode) {
      setItems(prev => prev.map(n => ({ ...n, read: true })));
      setUnread(0);
      return;
    }
    try {
      await axios.post(`${API}/notifications/read-all`, {}, { headers: { Authorization: `Bearer ${token}` } });
      setItems(prev => prev.map(n => ({ ...n, read: true })));
      setUnread(0);
    } catch {}
  };

  return (
    <div className="relative" ref={ref}>
      <button onClick={() => { setOpen(o => !o); if (!open) load(); }} className="relative p-2 rounded-lg hover:bg-white/5 transition-colors" data-testid="notification-bell">
        <Bell className="w-4.5 h-4.5 text-zinc-400" />
        {unread > 0 && (
          <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-[#7B61FF] text-white text-[9px] font-bold flex items-center justify-center" data-testid="unread-count">{unread > 9 ? "9+" : unread}</span>
        )}
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ opacity: 0, y: 5, scale: 0.97 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: 5, scale: 0.97 }} className="absolute right-0 top-full mt-2 w-80 max-h-96 overflow-y-auto rounded-xl bg-[#0A0A0A] border border-zinc-800 shadow-2xl z-50" data-testid="notification-dropdown">
            <div className="sticky top-0 bg-[#0A0A0A] border-b border-zinc-800/50 px-4 py-3 flex items-center justify-between">
              <span className="text-xs font-semibold text-zinc-300">Notifications</span>
              {unread > 0 && (
                <button onClick={markAllRead} className="text-[10px] text-[#7B61FF] hover:underline" data-testid="mark-all-read">Mark all read</button>
              )}
            </div>
            {items.length === 0 ? (
              <div className="py-8 text-center text-xs text-zinc-600">No notifications yet</div>
            ) : (
              <div className="divide-y divide-zinc-800/30">
                {items.map(n => {
                  const Icon = typeIcon[n.type] || TrendingUp;
                  return (
                    <div key={n.id} className={`px-4 py-3 flex gap-3 hover:bg-white/[0.02] transition-colors ${!n.read ? "bg-[#7B61FF]/[0.03]" : ""}`} data-testid={`notif-${n.id}`}>
                      <div className={`mt-0.5 p-1.5 rounded-lg shrink-0 ${!n.read ? "bg-[#7B61FF]/10" : "bg-zinc-800/50"}`}>
                        <Icon className={`w-3 h-3 ${!n.read ? "text-[#7B61FF]" : "text-zinc-600"}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className={`text-xs leading-relaxed ${!n.read ? "text-zinc-200" : "text-zinc-500"}`}>{n.message}</p>
                        <p className="text-[10px] text-zinc-700 mt-1">{new Date(n.created_at).toLocaleString()}</p>
                      </div>
                      {!n.read && (
                        <button onClick={() => markRead(n.id)} className="shrink-0 p-1 rounded hover:bg-white/5" title="Mark read">
                          <Check className="w-3 h-3 text-zinc-600" />
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default NotificationBell;
