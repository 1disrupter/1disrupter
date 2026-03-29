import { motion, AnimatePresence } from "framer-motion";
import { X, Zap, Shield, TrendingUp, Star } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { toast } from "sonner";
import { useDemoMode } from "../contexts/DemoModeContext";
import axios from "axios";
import { API } from "../lib/constants";

const FEATURES = [
  { icon: TrendingUp, label: "Unlimited strategy follows" },
  { icon: Shield, label: "Full leaderboard access" },
  { icon: Zap, label: "Unlimited backtesting" },
  { icon: Star, label: "Real-time signal notifications" },
];

const UpgradeModal = ({ open, onClose, feature = "This feature" }) => {
  const { isDemoMode } = useDemoMode();

  const handleUpgrade = async () => {
    if (isDemoMode) {
      toast.info("Billing disabled in Demo Mode");
      return;
    }
    try {
      const token = localStorage.getItem("alphaai_token");
      const email = localStorage.getItem("alphaai_email") || "";
      const res = await axios.post(`${API}/payments/checkout`, {
        package_id: "pro_monthly",
        origin_url: window.location.origin,
        user_email: email,
      }, { headers: token ? { Authorization: `Bearer ${token}` } : {} });
      if (res.data?.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (e) {
      toast.error("Unable to start checkout — please try again");
    }
  };

  return (
    <AnimatePresence>
      {open && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
          <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.95, opacity: 0 }} onClick={e => e.stopPropagation()} className="w-full max-w-md mx-4">
            <Card className="bg-[#0A0A0A] border-[#7B61FF]/30" data-testid="upgrade-modal">
              <CardHeader className="text-center pb-2">
                <div className="mx-auto p-3 rounded-2xl bg-[#7B61FF]/10 border border-[#7B61FF]/20 w-fit mb-3">
                  <Zap className="w-7 h-7 text-[#7B61FF]" />
                </div>
                <CardTitle className="text-lg font-['Outfit']">Upgrade to AlphaAI Pro</CardTitle>
                <p className="text-xs text-zinc-500 mt-1">{feature} requires a Pro subscription</p>
              </CardHeader>
              <CardContent className="p-5 space-y-4">
                <div className="space-y-2">
                  {FEATURES.map((f, i) => (
                    <div key={i} className="flex items-center gap-3 text-sm text-zinc-300">
                      <f.icon className="w-4 h-4 text-[#7B61FF] shrink-0" />
                      <span>{f.label}</span>
                    </div>
                  ))}
                </div>
                <div className="pt-2 space-y-2">
                  <Button onClick={handleUpgrade} className="w-full rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/80 text-white" data-testid="upgrade-btn">
                    <Zap className="w-4 h-4 mr-2" /> Upgrade Now — $29/mo
                  </Button>
                  <Button variant="outline" onClick={onClose} className="w-full rounded-full border-zinc-800 text-xs text-zinc-400">
                    Maybe Later
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default UpgradeModal;
