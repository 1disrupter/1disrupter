import { useState } from "react";
import { motion } from "framer-motion";
import { Settings, Trash2, RefreshCw, Volume2, VolumeX, Minimize2, Maximize2 } from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { toast } from "sonner";
import { cacheClearAll, cacheGet } from "../lib/mobileCache";
import { fetchBootstrap } from "../lib/mobileApi";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";

const MobileSettingsPage = () => {
  const { isDemoMode } = useDemoMode();
  const { tokens } = useAuth();
  const [soundEnabled, setSoundEnabled] = useState(() => localStorage.getItem("alphaai_sound") !== "off");
  const [compactMode, setCompactMode] = useState(() => localStorage.getItem("alphaai_compact") === "on");
  const [refreshing, setRefreshing] = useState(false);

  const handleClearCache = () => {
    cacheClearAll();
    toast.success("Cache cleared");
  };

  const handleRefreshData = async () => {
    setRefreshing(true);
    try {
      cacheClearAll();
      await fetchBootstrap(isDemoMode, tokens?.access_token);
      toast.success("Data refreshed");
    } catch {
      toast.error("Refresh failed");
    } finally {
      setRefreshing(false);
    }
  };

  const toggleSound = () => {
    const next = !soundEnabled;
    setSoundEnabled(next);
    localStorage.setItem("alphaai_sound", next ? "on" : "off");
    toast.success(next ? "Sounds enabled" : "Sounds muted");
  };

  const toggleCompact = () => {
    const next = !compactMode;
    setCompactMode(next);
    localStorage.setItem("alphaai_compact", next ? "on" : "off");
    document.documentElement.classList.toggle("compact-mode", next);
    toast.success(next ? "Compact mode enabled" : "Compact mode disabled");
  };

  const cacheStatus = {
    bootstrap: !!cacheGet("bootstrap") || !!cacheGet("bootstrap_demo"),
    strategies: !!cacheGet("strategies"),
    followed: !!cacheGet("followed"),
    alerts: !!cacheGet("alerts"),
  };

  return (
    <div className="min-h-screen pt-24 pb-24 px-4" data-testid="mobile-settings-page">
      <div className="max-w-lg mx-auto">
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-2xl font-bold font-['Outfit'] flex items-center gap-3" data-testid="settings-title">
            <div className="p-2.5 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/20">
              <Settings className="w-6 h-6 text-[#7B61FF]" />
            </div>
            Settings
          </h1>
        </motion.div>

        <div className="space-y-4">
          {/* Data Management */}
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-4 space-y-3">
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Data</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-200">Clear Cache</p>
                  <p className="text-[10px] text-zinc-600">Remove locally stored data</p>
                </div>
                <Button variant="outline" size="sm" onClick={handleClearCache} className="rounded-full border-zinc-800 h-8 px-3 text-xs" data-testid="clear-cache-btn">
                  <Trash2 className="w-3.5 h-3.5 mr-1.5" /> Clear
                </Button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-200">Refresh Data</p>
                  <p className="text-[10px] text-zinc-600">Re-fetch all cached data</p>
                </div>
                <Button variant="outline" size="sm" onClick={handleRefreshData} disabled={refreshing} className="rounded-full border-zinc-800 h-8 px-3 text-xs" data-testid="refresh-data-btn">
                  <RefreshCw className={`w-3.5 h-3.5 mr-1.5 ${refreshing ? "animate-spin" : ""}`} /> Refresh
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Preferences */}
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-4 space-y-3">
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Preferences</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-200">Alert Sounds</p>
                  <p className="text-[10px] text-zinc-600">Play sound on new alerts</p>
                </div>
                <button onClick={toggleSound} className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs border transition-all ${soundEnabled ? "border-[#00FF94]/30 text-[#00FF94] bg-[#00FF94]/10" : "border-zinc-800 text-zinc-500"}`} data-testid="sound-toggle">
                  {soundEnabled ? <Volume2 className="w-3.5 h-3.5" /> : <VolumeX className="w-3.5 h-3.5" />}
                  {soundEnabled ? "On" : "Off"}
                </button>
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-200">Compact Mode</p>
                  <p className="text-[10px] text-zinc-600">Reduce spacing for mobile</p>
                </div>
                <button onClick={toggleCompact} className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs border transition-all ${compactMode ? "border-[#7B61FF]/30 text-[#7B61FF] bg-[#7B61FF]/10" : "border-zinc-800 text-zinc-500"}`} data-testid="compact-toggle">
                  {compactMode ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
                  {compactMode ? "On" : "Off"}
                </button>
              </div>
            </CardContent>
          </Card>

          {/* Cache Status */}
          <Card className="bg-[#0A0A0A] border-zinc-800/50">
            <CardContent className="p-4 space-y-2">
              <h3 className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Cache Status</h3>
              {Object.entries(cacheStatus).map(([key, cached]) => (
                <div key={key} className="flex items-center justify-between text-xs">
                  <span className="text-zinc-400 capitalize">{key}</span>
                  <span className={cached ? "text-[#00FF94]" : "text-zinc-700"}>{cached ? "Cached" : "Empty"}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default MobileSettingsPage;
