import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import { AnimatePresence } from "framer-motion";
import "@/App.css";
import { AuthProvider } from "./contexts/AuthContext";
import { WalletProvider } from "./contexts/WalletContext";
import { DemoModeProvider } from "./contexts/DemoModeContext";
import { ProtectedRoute, PublicOnlyRoute } from "./components/RouteGuards";
import AppLayout from "./components/AppLayout";
import MarketingLayout from "./components/MarketingLayout";
import { LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, VerifyEmailPage } from "./pages/AuthPages";
import SplashScreen from "./components/SplashScreen";
import LandingPage from "./pages/LandingPage";
import DashboardPage from "./pages/DashboardPage";
import LeaderboardPage from "./pages/LeaderboardPage";
import CopyTradingPage from "./pages/CopyTradingPage";
import PricingPage from "./pages/PricingPage";
import SimulationPage from "./pages/SimulationPage";
import ResearchEnginePage from "./pages/ResearchEnginePage";
import AgentsPage from "./pages/AgentsPage";
import EventAgentsPage from "./pages/EventAgentsPage";
import StrategyLabPage from "./pages/StrategyLabPage";
import MarketplacePage from "./pages/MarketplacePage";
import AnalyticsPage from "./pages/AnalyticsPage";
import ConversionAnalyticsPage from "./pages/ConversionAnalyticsPage";
import AdminPage from "./pages/AdminPage";
import AdminAnalyticsPage from "./pages/AdminAnalyticsPage";
import ReferralPage from "./pages/ReferralPage";
import FollowingPage from "./pages/FollowingPage";
import AlertsPage from "./pages/AlertsPage";
import LiveSignalsPage from "./pages/LiveSignalsPage";
import AdminTrafficPage from "./pages/AdminTrafficPage";
import ConnectExchangePage from "./pages/ConnectExchangePage";
import DemoPage from "./pages/DemoPage";
import MobileSettingsPage from "./pages/MobileSettingsPage";
import StrategyMarketplacePage from "./pages/StrategyMarketplacePage";
import StrategyDetailPage from "./pages/StrategyDetailPage";
import StrategyLeaderboardPage from "./pages/StrategyLeaderboardPage";
import MyStrategiesPage from "./pages/MyStrategiesPage";
import CreatorDashboardPage from "./pages/CreatorDashboardPage";
import ExecutionSettingsPage from "./pages/ExecutionSettingsPage";
import ExecutionMonitorPage from "./pages/ExecutionMonitorPage";
import BillingPortalPage from "./pages/BillingPortalPage";
import TourAnalyticsPage from "./pages/TourAnalyticsPage";
import NotFoundPage from "./pages/NotFoundPage";
import TermsOfService from "./pages/TermsOfService";
import PrivacyPolicy from "./pages/PrivacyPolicy";
import ErrorBoundary from "./components/ErrorBoundary";
import CookieConsent from "./components/CookieConsent";
import MobileNetworkBanner from "./components/MobileNetworkBanner";
import useMobileOptimizations from "./hooks/useMobileOptimizations";
import useStrategyAlerts from "./hooks/useStrategyAlerts";
import useTracking from "./hooks/useTracking";
import useReferralCapture from "./hooks/useReferralCapture";
import usePrefetch from "./hooks/usePrefetch";

function TrackingWrapper({ children }) {
  useTracking();
  useReferralCapture();
  usePrefetch();
  const { isOnline } = useMobileOptimizations();
  const { connected: wsConnected } = useStrategyAlerts();

  return (
    <>
      <MobileNetworkBanner isOnline={isOnline} wsConnected={wsConnected} />
      {children}
    </>
  );
}

function App() {
  const [showSplash, setShowSplash] = useState(() => {
    if (sessionStorage.getItem('alphaai_splash_shown')) return false;
    return true;
  });

  const handleSplashComplete = () => {
    sessionStorage.setItem('alphaai_splash_shown', '1');
    setShowSplash(false);
  };

  return (
    <ErrorBoundary>
    <AuthProvider>
      <WalletProvider>
        <DemoModeProvider>
        <AnimatePresence>
          {showSplash && <SplashScreen onComplete={handleSplashComplete} />}
        </AnimatePresence>
        <div className="App min-h-screen bg-[#050505]">
          <BrowserRouter>
            <TrackingWrapper>
            <Routes>
              {/* Public marketing routes */}
              <Route element={<MarketingLayout />}>
                <Route path="/" element={<LandingPage />} />
                <Route path="/leaderboard" element={<LeaderboardPage />} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/demo" element={<DemoPage />} />
                <Route path="/login" element={<PublicOnlyRoute><LoginPage /></PublicOnlyRoute>} />
                <Route path="/register" element={<PublicOnlyRoute><RegisterPage /></PublicOnlyRoute>} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />
                <Route path="/verify-email" element={<VerifyEmailPage />} />
                <Route path="/terms" element={<TermsOfService />} />
                <Route path="/privacy" element={<PrivacyPolicy />} />
              </Route>

              {/* Authenticated app routes */}
              <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/live-signals" element={<LiveSignalsPage />} />
                <Route path="/alerts" element={<AlertsPage />} />
                <Route path="/agents" element={<AgentsPage />} />
                <Route path="/events" element={<EventAgentsPage />} />
                <Route path="/analytics" element={<AnalyticsPage />} />
                <Route path="/conversion-analytics" element={<ConversionAnalyticsPage />} />
                <Route path="/research" element={<ResearchEnginePage />} />
                <Route path="/lab" element={<StrategyLabPage />} />
                <Route path="/simulation" element={<SimulationPage />} />
                <Route path="/marketplace" element={<MarketplacePage />} />
                <Route path="/copy-trading" element={<CopyTradingPage />} />
                <Route path="/connect-exchange" element={<ConnectExchangePage />} />
                <Route path="/strategy-marketplace" element={<StrategyMarketplacePage />} />
                <Route path="/strategies" element={<StrategyLeaderboardPage />} />
                <Route path="/strategy-marketplace/:id" element={<StrategyDetailPage />} />
                <Route path="/marketplace/:id" element={<StrategyDetailPage />} />
                <Route path="/creator/strategies" element={<CreatorDashboardPage />} />
                <Route path="/me/strategies" element={<MyStrategiesPage />} />
                <Route path="/me/execution-settings" element={<ExecutionSettingsPage />} />
                <Route path="/billing" element={<BillingPortalPage />} />
                <Route path="/referrals" element={<ReferralPage />} />
                <Route path="/following" element={<FollowingPage />} />
                <Route path="/settings" element={<MobileSettingsPage />} />
                <Route path="/admin" element={<AdminPage />} />
                <Route path="/admin/analytics" element={<AdminAnalyticsPage />} />
                <Route path="/admin/traffic" element={<AdminTrafficPage />} />
                <Route path="/admin/execution-monitor" element={<ExecutionMonitorPage />} />
                <Route path="/admin/tour-analytics" element={<TourAnalyticsPage />} />
              </Route>

              {/* 404 Catch-All */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
            </TrackingWrapper>
          </BrowserRouter>
          <Toaster position="top-center" theme="dark" toastOptions={{ className: "md:!bottom-auto" }} />
          <CookieConsent />
        </div>
        </DemoModeProvider>
      </WalletProvider>
    </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
