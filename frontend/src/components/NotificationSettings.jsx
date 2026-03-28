import { useState, useEffect } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  Bell, BellRing, Activity, TrendingUp, Check, Moon, Rocket, RefreshCw
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Switch } from "./ui/switch";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { API } from "../lib/constants";

const NotificationSettings = ({ walletAddress, isPro }) => {
  const [prefs, setPrefs] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingNotification, setTestingNotification] = useState(false);

  useEffect(() => {
    if (walletAddress) {
      Promise.all([
        axios.get(`${API}/notifications/preferences?wallet_address=${walletAddress}`),
        axios.get(`${API}/notifications/config`)
      ]).then(([prefsRes, configRes]) => {
        setPrefs(prefsRes.data);
        setConfig(configRes.data);
      }).catch(console.error).finally(() => setLoading(false));
    }
  }, [walletAddress]);

  const updatePref = async (key, value) => {
    setSaving(true);
    try {
      const updateData = { [key]: value };
      const res = await axios.put(
        `${API}/notifications/preferences?wallet_address=${walletAddress}`,
        updateData
      );
      setPrefs(res.data);
      toast.success("Notification settings updated");
    } catch (error) {
      toast.error("Failed to update settings");
    }
    setSaving(false);
  };

  const sendTestNotification = async () => {
    setTestingNotification(true);
    try {
      const res = await axios.post(`${API}/notifications/test?wallet_address=${walletAddress}`);
      if (res.data.success) {
        toast.success("Test notification sent!");
      } else {
        toast.info(res.data.message || "No devices registered");
      }
    } catch (error) {
      toast.error("Failed to send test notification");
    }
    setTestingNotification(false);
  };

  if (loading) {
    return (
      <Card className="glass-card">
        <CardContent className="p-6 flex items-center justify-center">
          <RefreshCw className="w-5 h-5 animate-spin text-zinc-500" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass-card" data-testid="notification-settings">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-[#7B61FF]" />
          Push Notifications
          {isPro && (
            <Badge className="bg-gradient-to-r from-[#7B61FF] to-[#00FF94] text-white text-xs ml-2">
              PRO
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Get instant alerts when high-confidence signals are generated
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800">
          <div className="flex items-center gap-3">
            <BellRing className="w-4 h-4 text-[#00FF94]" />
            <span className="text-sm font-medium">Enable Push Notifications</span>
          </div>
          <Switch
            checked={prefs?.push_enabled ?? true}
            onCheckedChange={(checked) => updatePref('push_enabled', checked)}
            disabled={saving}
            data-testid="push-enabled-toggle"
          />
        </div>

        {prefs?.push_enabled && (
          <div className="p-4 rounded-lg bg-gradient-to-r from-[#7B61FF]/10 to-transparent border border-[#7B61FF]/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-full bg-[#7B61FF]/20">
                  <Rocket className="w-4 h-4 text-[#7B61FF]" />
                </div>
                <div>
                  <span className="text-sm font-medium block">High-Confidence Signal Alerts</span>
                  <span className="text-xs text-zinc-500">
                    Signals with {config?.high_confidence_threshold || 75}%+ confidence
                  </span>
                </div>
              </div>
              <Switch
                checked={prefs?.high_confidence_alerts ?? true}
                onCheckedChange={(checked) => updatePref('high_confidence_alerts', checked)}
                disabled={saving || !isPro}
                data-testid="high-confidence-toggle"
              />
            </div>
            {!isPro && (
              <p className="text-xs text-yellow-400 mt-2 pl-11">
                Upgrade to Pro for instant high-confidence alerts
              </p>
            )}
          </div>
        )}

        {prefs?.push_enabled && (
          <div className="space-y-2">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Alert Types</p>
            
            {[
              { key: 'signal_alerts', label: 'All Signal Alerts', icon: Activity, desc: 'Every trading signal' },
              { key: 'trade_confirmations', label: 'Trade Confirmations', icon: Check, desc: 'When trades execute' },
              { key: 'price_alerts', label: 'Price Alerts', icon: TrendingUp, desc: 'Price target hits' },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between p-2 rounded-lg hover:bg-[#050505]/50">
                <div className="flex items-center gap-2">
                  <item.icon className="w-4 h-4 text-zinc-500" />
                  <div>
                    <span className="text-sm">{item.label}</span>
                    <span className="text-xs text-zinc-600 block">{item.desc}</span>
                  </div>
                </div>
                <Switch
                  checked={prefs?.[item.key] ?? true}
                  onCheckedChange={(checked) => updatePref(item.key, checked)}
                  disabled={saving}
                />
              </div>
            ))}
          </div>
        )}

        {prefs?.push_enabled && (
          <div className="pt-3 border-t border-zinc-800">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Moon className="w-4 h-4 text-zinc-500" />
                <span className="text-sm">Quiet Hours</span>
              </div>
              <Switch
                checked={prefs?.quiet_hours?.enabled ?? false}
                onCheckedChange={(checked) => updatePref('quiet_hours_enabled', checked)}
                disabled={saving}
              />
            </div>
            {prefs?.quiet_hours?.enabled && (
              <div className="flex items-center gap-2 pl-6">
                <Input
                  type="time"
                  value={prefs?.quiet_hours?.start || "22:00"}
                  onChange={(e) => updatePref('quiet_hours_start', e.target.value)}
                  className="bg-[#050505] border-zinc-800 w-24 text-xs"
                />
                <span className="text-zinc-500">to</span>
                <Input
                  type="time"
                  value={prefs?.quiet_hours?.end || "08:00"}
                  onChange={(e) => updatePref('quiet_hours_end', e.target.value)}
                  className="bg-[#050505] border-zinc-800 w-24 text-xs"
                />
              </div>
            )}
          </div>
        )}

        <Button
          onClick={sendTestNotification}
          disabled={testingNotification || !prefs?.push_enabled}
          variant="outline"
          className="w-full rounded-full border-zinc-700 hover:border-[#7B61FF]"
          data-testid="test-notification-btn"
        >
          {testingNotification ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Bell className="w-4 h-4 mr-2" />
          )}
          Send Test Notification
        </Button>
      </CardContent>
    </Card>
  );
};

export default NotificationSettings;
