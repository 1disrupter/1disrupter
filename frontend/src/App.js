import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import { AnimatePresence } from "framer-motion";
import "@/App.css";
import { AuthProvider } from "./contexts/AuthContext";
import { WalletProvider } from "./contexts/WalletContext";
import { DemoModeProvider } from "./contexts/DemoModeContext";
import DemoModeBanner from "./components/DemoModeBanner";
import { LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, VerifyEmailPage } from "./pages/AuthPages";
import Navigation from "./components/Navigation";
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
import ReferralPage from "./pages/ReferralPage";

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
    <AuthProvider>
      <WalletProvider>
        <DemoModeProvider>
        <AnimatePresence>
          {showSplash && <SplashScreen onComplete={handleSplashComplete} />}
        </AnimatePresence>
        <div className="App min-h-screen bg-[#050505]">
          <BrowserRouter>
            <DemoModeBanner />
            <Navigation />
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/leaderboard" element={<LeaderboardPage />} />
              <Route path="/copy-trading" element={<CopyTradingPage />} />
              <Route path="/pricing" element={<PricingPage />} />
              <Route path="/simulation" element={<SimulationPage />} />
              <Route path="/research" element={<ResearchEnginePage />} />
              <Route path="/agents" element={<AgentsPage />} />
              <Route path="/events" element={<EventAgentsPage />} />
              <Route path="/lab" element={<StrategyLabPage />} />
              <Route path="/marketplace" element={<MarketplacePage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/conversion-analytics" element={<ConversionAnalyticsPage />} />
              <Route path="/admin" element={<AdminPage />} />
              {/* Auth Routes */}
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password" element={<ResetPasswordPage />} />
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              {/* Referral */}
              <Route path="/referrals" element={<ReferralPage />} />
            </Routes>
          </BrowserRouter>
          <Toaster position="bottom-right" theme="dark" />
        </div>
        </DemoModeProvider>
      </WalletProvider>
    </AuthProvider>
  );
}

export default App;
