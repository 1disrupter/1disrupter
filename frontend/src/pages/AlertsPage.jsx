import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { List as VirtualList } from "react-window";
import {
  Radio, Zap, TrendingUp, TrendingDown, X, Trash2,
  ArrowUpRight, ArrowDownRight, Target, ShieldAlert, Wifi, WifiOff
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import useStrategyAlerts from "../hooks/useStrategyAlerts";
import UpgradeModal from "../components/UpgradeModal";
import { AlertListSkeleton } from "../components/SkeletonLoaders";
import { cacheGet, cacheSet } from "../lib/mobileCache";

const actionConfig = {
  LONG: { icon: ArrowUpRight, color: "text-[#00FF94]", bg: "bg-[#00FF94]/10", label: "LONG" },
  SHORT: { icon: ArrowDownRight, color: "text-red-400", bg: "bg-red-400/10", label: "SHORT" },
  CLOSE: { icon: X, color: "text-[#7B61FF]", bg: "bg-[#7B61FF]/10", label: "CLOSE" },
  TAKE_PROFIT: { icon: Target, color: "text-[#00FF94]", bg: "bg-[#00FF94]/10", label: "TP HIT" },
  STOP_LOSS: { icon: ShieldAlert, color: "text-[#FFB800]", bg: "bg-[#FFB800]/10", label: "SL HIT" },
};

function getTimeAgo(date) {
  const seconds = Math.floor((new Date() - date) / 1000);
  if (seconds < 10) return "just now";
  if (seconds < 60) return `${seconds}s ago`;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  return `${hours}h ago`;
}

const AlertCard = ({ alert, index, style }) => {
  const cfg = actionConfig[alert.action] || actionConfig.LONG;
  const Icon = cfg.icon;
  const ts = alert.timestamp ? new Date(alert.timestamp) : new Date();
  const timeAgo = getTimeAgo(ts);

  return (
    <div style={style} className="pb-3">
      <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-all h-full" data-testid={`alert-card-${index}`}>
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${cfg.bg} shrink-0 mt-0.5`}>
              <Icon className={`w-4 h-4 ${cfg.color}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <Badge className={`${cfg.bg} ${cfg.color} text-[9px] font-bold`}>{cfg.label}</Badge>
                {alert.asset && <span className="text-[10px] font-mono text-zinc-600">{alert.asset}</span>}
                {alert.confidence && (
                  <span className="text-[10px] text-zinc-600">{alert.confidence}% conf</span>
                )}
              </div>
              <p className="text-xs text-zinc-300 leading-relaxed">{alert.message}</p>
              <div className="flex items-center gap-3 mt-2">
                {alert.strategy_name && (
                  <span className="text-[10px] text-[#7B61FF]">{alert.strategy_name}</span>
                )}
                <span className="text-[10px] text-zinc-700">{timeAgo}</span>
              </div>
            </div>
            {alert.price && (
              <div className="text-right shrink-0">
                <p className="text-xs font-mono font-bold text-white">${Number(alert.price).toLocaleString()}</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const VIRTUALIZE_THRESHOLD = 20;
const ITEM_SIZE = 110;

const AlertsPage = () => {
  const { isDemoMode } = useDemoMode();
  const { isAuthenticated, isPro } = useAuth();
  const { alerts, connected, upgradeRequired, clearAlerts } = useStrategyAlerts();
  const [showUpgrade, setShowUpgrade] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const containerRef = useRef(null);

  useEffect(() => {
    const on = () => setIsOnline(true);
    const off = () => setIsOnline(false);
    window.addEventListener("online", on);
    window.addEventListener("offline", off);
    return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
  }, []);

  // Cache alerts for offline access
  useEffect(() => {
    if (alerts.length > 0) cacheSet("alerts", alerts);
  }, [alerts]);

  const cachedAlerts = !isOnline && alerts.length === 0 ? (cacheGet("alerts") || []) : alerts;
  const showUpgradePrompt = !isDemoMode && isAuthenticated && upgradeRequired;
  const useVirtualList = cachedAlerts.length > VIRTUALIZE_THRESHOLD;

  const VirtualRow = useCallback(({ index, style }) => (
    <AlertCard alert={cachedAlerts[index]} index={index} style={style} />
  ), [cachedAlerts]);

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="alerts-page">
      <div className="max-w-4xl mx-auto">
        {/* Offline Banner */}
        {!isOnline && (
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="mb-4 p-3 rounded-xl bg-zinc-800/50 border border-zinc-700 flex items-center gap-2 text-sm text-zinc-400" data-testid="alerts-offline-banner">
            <WifiOff className="w-4 h-4" /> You're offline — showing cached alerts
          </motion.div>
        )}

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold font-['Outfit'] flex items-center gap-3" data-testid="alerts-title">
                <div className="p-2.5 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/20">
                  <Radio className="w-6 h-6 text-[#7B61FF]" />
                </div>
                Live Alerts
              </h1>
              <p className="text-sm text-zinc-500 mt-2 ml-14">
                Real-time strategy signals from strategies you follow
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2" data-testid="connection-status">
                {connected ? (
                  <Badge className="bg-[#00FF94]/10 text-[#00FF94] text-[9px] gap-1.5">
                    <Wifi className="w-3 h-3" /> Live
                  </Badge>
                ) : (
                  <Badge className="bg-zinc-800 text-zinc-500 text-[9px] gap-1.5">
                    <WifiOff className="w-3 h-3" /> Offline
                  </Badge>
                )}
              </div>
              {isDemoMode && (
                <Badge className="bg-zinc-700 text-zinc-400 text-[9px]">Demo Mode</Badge>
              )}
              {cachedAlerts.length > 0 && (
                <Button variant="outline" size="sm" onClick={clearAlerts} className="rounded-full border-zinc-800 text-[10px] h-7 px-3 text-zinc-400" data-testid="clear-alerts-btn">
                  <Trash2 className="w-3 h-3 mr-1" /> Clear
                </Button>
              )}
            </div>
          </div>
        </motion.div>

        {/* Upgrade prompt for free users */}
        {showUpgradePrompt && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="bg-gradient-to-r from-[#7B61FF]/5 to-[#00FF94]/5 border-[#7B61FF]/20 mb-6" data-testid="upgrade-prompt">
              <CardContent className="p-6 text-center">
                <Zap className="w-8 h-8 text-[#7B61FF] mx-auto mb-3" />
                <h3 className="text-sm font-semibold text-zinc-200 mb-1">
                  Upgrade to Pro for Real-Time Alerts
                </h3>
                <p className="text-xs text-zinc-500 mb-4">
                  Get instant strategy signals delivered via WebSocket. Never miss a trade.
                </p>
                <Button onClick={() => setShowUpgrade(true)} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white text-xs" data-testid="upgrade-alerts-btn">
                  <Zap className="w-3.5 h-3.5 mr-1.5" /> Upgrade to Pro — $29/mo
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Waiting for alerts state */}
        {!showUpgradePrompt && cachedAlerts.length === 0 && (
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50 border-dashed" data-testid="alerts-empty">
              <CardContent className="py-20 text-center">
                <div className="relative mx-auto w-16 h-16 mb-5">
                  <div className="absolute inset-0 rounded-full bg-[#7B61FF]/10 animate-ping" />
                  <div className="relative flex items-center justify-center w-16 h-16 rounded-full bg-[#7B61FF]/10 border border-[#7B61FF]/20">
                    <Radio className="w-7 h-7 text-[#7B61FF]" />
                  </div>
                </div>
                <h3 className="text-sm font-semibold text-zinc-400 mb-2">
                  {connected ? "Listening for signals..." : "Connecting..."}
                </h3>
                <p className="text-xs text-zinc-600 max-w-sm mx-auto">
                  {isDemoMode
                    ? "Demo alerts will appear every 10-20 seconds. Watch the magic happen."
                    : "When strategies you follow generate signals, they'll appear here in real-time."}
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Alert feed */}
        {cachedAlerts.length > 0 && (
          <div ref={containerRef}>
            <div className="flex items-center justify-between mb-3">
              <p className="text-[10px] text-zinc-600 uppercase tracking-wider">
                {cachedAlerts.length} alert{cachedAlerts.length !== 1 ? "s" : ""} received
              </p>
              {connected && (
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#00FF94] animate-pulse" />
                  <span className="text-[10px] text-[#00FF94]">streaming</span>
                </div>
              )}
            </div>

            {useVirtualList ? (
              <VirtualList
                height={Math.min(cachedAlerts.length * ITEM_SIZE, 600)}
                itemCount={cachedAlerts.length}
                itemSize={ITEM_SIZE}
                width="100%"
                data-testid="virtualized-alert-list"
              >
                {VirtualRow}
              </VirtualList>
            ) : (
              <div className="space-y-3" data-testid="alert-list">
                <AnimatePresence initial={false}>
                  {cachedAlerts.map((alert, i) => (
                    <motion.div
                      key={`${alert.timestamp}-${i}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ delay: i * 0.03 }}
                    >
                      <AlertCard alert={alert} index={i} />
                    </motion.div>
                  ))}
                </AnimatePresence>
              </div>
            )}
          </div>
        )}
      </div>

      <UpgradeModal open={showUpgrade} onClose={() => setShowUpgrade(false)} feature="Real-time strategy alerts" />
    </div>
  );
};

export default AlertsPage;
