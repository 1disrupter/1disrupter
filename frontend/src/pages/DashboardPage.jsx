import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Activity } from "lucide-react";
import { Badge } from "../components/ui/badge";
import { useAuth } from "../contexts/AuthContext";
import { useSystemMode } from "../contexts/DemoModeContext";
import OnboardingModal from "../components/OnboardingModal";
import LiveDashboard from "../components/LiveDashboard";
import { API } from "../lib/constants";
import axios from "axios";

const DashboardPage = () => {
  const { user: authUser } = useAuth();
  const { isDemo, isLive } = useSystemMode();
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Check for payment return
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get("session_id");
    const paymentStatus = urlParams.get("payment");
    if (sessionId && paymentStatus === "success") {
      toast.success("Payment successful! Upgrading your account...");
      window.history.replaceState({}, "", "/dashboard");
    } else if (paymentStatus === "cancelled") {
      toast.info("Payment cancelled. You can upgrade anytime.");
      window.history.replaceState({}, "", "/dashboard");
    }
  }, []);

  // Onboarding for new users
  useEffect(() => {
    if (authUser && !localStorage.getItem("alphaai_onboarded")) {
      setShowOnboarding(true);
    }
  }, [authUser]);

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="dashboard-page">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/20">
              <Activity className="w-6 h-6 text-[#7B61FF]" />
            </div>
            <div>
              <h1 className="text-2xl font-bold font-['Outfit'] text-zinc-100" data-testid="dashboard-title">
                Dashboard
              </h1>
              <p className="text-sm text-zinc-500 mt-0.5">
                {isLive
                  ? `Welcome back${authUser?.name ? ", " + authUser.name : ""} — live signal overview`
                  : "Dashboard unavailable in demo mode"}
              </p>
            </div>
          </div>
          <Badge
            className={`text-[10px] font-mono px-3 py-1.5 ${
              isLive
                ? "bg-[#00FF94]/10 text-[#00FF94] border border-[#00FF94]/20"
                : "bg-[#7B61FF]/10 text-[#7B61FF] border border-[#7B61FF]/20"
            }`}
            data-testid="dashboard-mode-badge"
          >
            <span
              className={`w-1.5 h-1.5 rounded-full mr-1.5 inline-block ${
                isLive ? "bg-[#00FF94] animate-pulse" : "bg-[#7B61FF]"
              }`}
            />
            {isLive ? "LIVE" : "DEMO"}
          </Badge>
        </div>

        {/* Content */}
        {isLive ? (
          <LiveDashboard />
        ) : (
          <div
            className="rounded-xl border border-zinc-800/50 bg-[#0A0A0A] py-20 text-center"
            data-testid="dashboard-demo-placeholder"
          >
            <Activity className="w-12 h-12 text-zinc-800 mx-auto mb-4" />
            <p className="text-sm text-zinc-500 font-medium">
              Demo mode — no live dashboard data
            </p>
            <p className="text-xs text-zinc-700 mt-1">
              Switch to Live mode in the admin panel to view real metrics
            </p>
          </div>
        )}
      </div>

      {/* Onboarding modal */}
      {showOnboarding && (
        <OnboardingModal
          onClose={() => {
            setShowOnboarding(false);
            localStorage.setItem("alphaai_onboarded", "true");
          }}
        />
      )}
    </div>
  );
};

export default DashboardPage;
