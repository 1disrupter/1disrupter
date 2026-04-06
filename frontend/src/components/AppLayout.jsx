import { useState } from "react";
import { Link, useLocation, useNavigate, Outlet } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart3, Bot, Store, Shield,
  ChevronDown, Copy, FlaskConical,
  Users, Home, Eye, Trophy,
  LogOut, User, Menu, Radio, Crown, Share2, Heart, Activity,
  X, Beaker, Brain
} from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
  DropdownMenuSeparator, DropdownMenuLabel
} from "./ui/dropdown-menu";
import { useAuth } from "../contexts/AuthContext";
import { useDemoMode } from "../contexts/DemoModeContext";
import { BrandLockup } from "./BrandComponents";
import { TierBadge } from "../pages/PricingPage";
import NotificationBell from "./NotificationBell";
import DemoModeBanner from "./DemoModeBanner";
import MobileBottomNav from "./MobileBottomNav";
import GuidedTour, { restartTour } from "./GuidedTour";
import { useSystemMode } from "../contexts/DemoModeContext";

const primaryItems = [
  { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
  { path: "/live-signals", label: "Live Signals", icon: Activity },
  { path: "/research", label: "Research", icon: Beaker },
  { path: "/lab", label: "Strategy Lab", icon: FlaskConical },
  { path: "/agents", label: "AI Agents", icon: Bot },
];

const overflowItems = [
  { path: "/alerts", label: "Alerts", icon: Radio },
  { path: "/simulation", label: "Simulation", icon: Radio },
  { path: "/events", label: "Event Agents", icon: Eye },
  { path: "/marketplace", label: "Marketplace", icon: Store },
  { path: "/copy-trading", label: "Copy Trading", icon: Copy },
  { path: "/following", label: "Following", icon: Heart },
  { path: "/referrals", label: "Referrals", icon: Users },
  { path: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { path: "/pricing", label: "Pricing", icon: Crown },
];

const adminItems = [
  { path: "/admin", label: "Admin Panel", icon: Shield },
  { path: "/admin/analytics", label: "Demo Analytics", icon: BarChart3 },
  { path: "/admin/traffic", label: "Traffic", icon: Activity },
];

const allMobileItems = [
  { path: "/", label: "Home", icon: Home },
  ...primaryItems,
  ...overflowItems,
  ...adminItems,
];

const overflowPaths = [...overflowItems, ...adminItems].map(i => i.path);

const AppLayout = () => {
  const { user, isAuthenticated, logout, isPro, isAdmin } = useAuth();
  const { isDemoMode, toggleDemoMode, shareDemoLink } = useDemoMode();
  const { isDemo: showTour } = useSystemMode();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isOverflowActive = overflowPaths.includes(location.pathname);

  return (
    <>
      <DemoModeBanner />
      <nav className="fixed top-0 left-0 right-0 z-50 px-2 sm:px-3 md:px-4 lg:px-6 py-3" data-testid="app-layout-nav">
        <div className="max-w-7xl mx-auto">
          <div className="glass rounded-2xl px-3 sm:px-4 md:px-5 lg:px-6 py-3 flex items-center justify-between gap-2 md:gap-3 overflow-hidden">
            {/* Logo */}
            <Link to="/dashboard" className="flex items-center gap-2 shrink-0" data-testid="app-nav-logo">
              <BrandLockup size="default" showSubtitle={false} />
            </Link>

            {/* Desktop Nav Items */}
            <div className="hidden md:flex items-center gap-0.5 lg:gap-1 min-w-0 flex-1 justify-center">
              {primaryItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`app-nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                  className={`px-2.5 lg:px-3.5 py-1.5 rounded-full text-xs lg:text-sm font-medium transition-all whitespace-nowrap shrink-0 ${
                    location.pathname === item.path
                      ? "bg-white/10 text-white"
                      : "text-zinc-400 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {item.label}
                </Link>
              ))}

              {/* More dropdown */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    className={`px-2.5 lg:px-3.5 py-1.5 rounded-full text-xs lg:text-sm font-medium transition-all whitespace-nowrap shrink-0 flex items-center gap-1 ${
                      isOverflowActive
                        ? "bg-white/10 text-white"
                        : "text-zinc-400 hover:text-white hover:bg-white/5"
                    }`}
                    data-testid="app-nav-more-dropdown"
                  >
                    More
                    <ChevronDown className="w-3 h-3" />
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="center" className="bg-[#121212] border-zinc-800 w-52" data-testid="app-nav-more-menu">
                  <DropdownMenuLabel className="text-[10px] text-zinc-600 uppercase tracking-wider">Features</DropdownMenuLabel>
                  {overflowItems.map((item) => (
                    <DropdownMenuItem
                      key={item.path}
                      onClick={() => navigate(item.path)}
                      className={`cursor-pointer ${location.pathname === item.path ? "bg-white/5 text-white" : ""}`}
                      data-testid={`app-nav-more-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      <item.icon className="w-4 h-4 mr-2.5 text-zinc-500" />
                      {item.label}
                    </DropdownMenuItem>
                  ))}
                  <DropdownMenuSeparator className="bg-zinc-800" />
                  <DropdownMenuLabel className="text-[10px] text-zinc-600 uppercase tracking-wider">Admin</DropdownMenuLabel>
                  {adminItems.map((item) => (
                    <DropdownMenuItem
                      key={item.path}
                      onClick={() => navigate(item.path)}
                      className={`cursor-pointer ${location.pathname === item.path ? "bg-white/5 text-white" : ""}`}
                      data-testid={`app-nav-more-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                    >
                      <item.icon className="w-4 h-4 mr-2.5 text-zinc-500" />
                      {item.label}
                    </DropdownMenuItem>
                  ))}
                  {showTour && !isAdmin && (
                    <>
                      <DropdownMenuSeparator className="bg-zinc-800" />
                      <DropdownMenuItem
                        onClick={restartTour}
                        className="cursor-pointer text-[#7B61FF]"
                        data-testid="restart-tour-desktop"
                      >
                        <Brain className="w-4 h-4 mr-2.5" />
                        Restart Tour
                      </DropdownMenuItem>
                    </>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            </div>

            {/* Right side actions */}
            <div className="flex items-center gap-1.5 sm:gap-2 lg:gap-3 shrink-0">
              {/* System Mode Badge */}
              <div
                className={`hidden xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-[10px] font-mono font-bold tracking-wider border ${
                  isDemoMode
                    ? 'bg-[#7B61FF]/10 border-[#7B61FF]/30 text-[#7B61FF]'
                    : 'bg-[#00FF94]/10 border-[#00FF94]/30 text-[#00FF94]'
                }`}
                data-testid="system-mode-badge"
              >
                <span className={`w-1.5 h-1.5 rounded-full ${isDemoMode ? 'bg-[#7B61FF]' : 'bg-[#00FF94] animate-pulse'}`} />
                {isDemoMode ? 'DEMO MODE' : 'LIVE MODE'}
              </div>

              {/* Share Demo */}
              {isDemoMode && (
                <button
                  onClick={shareDemoLink}
                  className="hidden xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs font-medium transition-all border border-[#00FF94]/30 text-[#00FF94]/80 hover:bg-[#00FF94]/10 hover:text-[#00FF94] hover:border-[#00FF94]/50"
                  data-testid="share-demo-btn"
                >
                  <Share2 className="w-3.5 h-3.5" />
                  Share
                </button>
              )}

              {(isPro || isDemoMode) && (
                <Badge className="hidden sm:flex bg-gradient-to-r from-[#7B61FF] to-[#00FF94] text-white text-[10px]" data-testid="pro-badge">
                  PRO
                </Badge>
              )}

              {isAdmin && (
                <Badge
                  className="hidden sm:flex items-center gap-1 bg-transparent border border-[#7B61FF]/50 text-[#7B61FF] text-[10px] font-mono"
                  data-testid="admin-badge"
                >
                  <Shield className="w-3 h-3" />
                  Admin
                </Badge>
              )}

              {isAuthenticated ? (
                <>
                  <NotificationBell />
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" size="sm" className="rounded-full border-[#7B61FF]/30 hover:border-[#7B61FF] bg-[#7B61FF]/10 h-8 px-2.5 lg:px-3" data-testid="user-dropdown">
                        <User className="w-3.5 h-3.5 lg:mr-1.5 text-[#7B61FF]" />
                        <span className="hidden lg:inline text-xs">{user?.name?.split(' ')[0] || 'User'}</span>
                        <ChevronDown className="w-3 h-3 ml-1" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="bg-[#121212] border-zinc-800 w-56">
                      <div className="px-3 py-2 border-b border-zinc-800">
                        <div className="flex items-center gap-2">
                          <p className="text-sm font-medium">{user?.name}</p>
                          <TierBadge tier={user?.user_tier || 'free'} />
                        </div>
                        <p className="text-xs text-zinc-500">{user?.email}</p>
                      </div>
                      <DropdownMenuItem onClick={logout} className="text-red-400">
                        <LogOut className="w-4 h-4 mr-2" />Sign Out
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </>
              ) : isDemoMode ? (
                <>
                  <NotificationBell />
                  <Link to="/register">
                    <Button size="sm" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-xs px-3 h-8" data-testid="demo-signup-btn">
                      Sign Up
                    </Button>
                  </Link>
                </>
              ) : null}

              {/* Mobile menu button */}
              <Button variant="ghost" size="icon" className="md:hidden h-8 w-8" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="app-mobile-menu-btn">
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>

          {/* Mobile menu */}
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="md:hidden glass rounded-2xl mt-2 p-3 max-h-[70vh] overflow-y-auto">
                {allMobileItems.map((item) => (
                  <Link key={item.path} to={item.path} onClick={() => setMobileMenuOpen(false)} className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm ${location.pathname === item.path ? "bg-white/10 text-white" : "text-zinc-400"}`}>
                    <item.icon className="w-4 h-4" />{item.label}
                  </Link>
                ))}

                <Link
                  to="/admin"
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm ${
                    location.pathname === "/admin" ? "bg-[#7B61FF]/10 text-[#7B61FF]" : "text-zinc-500"
                  }`}
                  data-testid="admin-login-mobile"
                >
                  <Shield className="w-4 h-4" />Admin Login
                </Link>

                <div className="mt-3 pt-3 border-t border-zinc-800 space-y-1">
                  <button
                    onClick={() => { toggleDemoMode(); setMobileMenuOpen(false); }}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm w-full ${isDemoMode ? 'text-[#7B61FF] bg-[#7B61FF]/10' : 'text-zinc-400'}`}
                    data-testid="demo-mode-toggle-mobile"
                  >
                    <Eye className="w-4 h-4" />
                    Demo Mode
                    <div className={`ml-auto w-7 h-4 rounded-full p-0.5 transition-colors ${isDemoMode ? 'bg-[#7B61FF]' : 'bg-zinc-700'}`}>
                      <div className={`w-3 h-3 rounded-full bg-white transition-transform ${isDemoMode ? 'translate-x-3' : 'translate-x-0'}`} />
                    </div>
                  </button>
                  {isDemoMode && (
                    <button
                      onClick={() => { shareDemoLink(); setMobileMenuOpen(false); }}
                      className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm w-full text-[#00FF94]/80 hover:bg-[#00FF94]/10"
                      data-testid="share-demo-btn-mobile"
                    >
                      <Share2 className="w-4 h-4" />Share Demo Link
                    </button>
                  )}
                  {showTour && !isAdmin && (
                    <button
                      onClick={() => { restartTour(); setMobileMenuOpen(false); }}
                      className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm w-full text-[#7B61FF] hover:bg-[#7B61FF]/10"
                      data-testid="restart-tour-mobile"
                    >
                      <Brain className="w-4 h-4" />Restart Tour
                    </button>
                  )}
                  {!isAuthenticated && isDemoMode && (
                    <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm bg-[#7B61FF] text-white mt-2">
                      <User className="w-4 h-4" />Sign Up Free
                    </Link>
                  )}
                  {isAuthenticated && (
                    <button
                      onClick={() => { logout(); setMobileMenuOpen(false); }}
                      className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm w-full text-red-400"
                      data-testid="app-nav-signout-mobile"
                    >
                      <LogOut className="w-4 h-4" />Sign Out
                    </button>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </nav>

      {/* Page content */}
      <Outlet />
      <MobileBottomNav />
      {showTour && !isAdmin && <GuidedTour />}
    </>
  );
};

export default AppLayout;
