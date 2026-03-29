import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Wallet, BarChart3, Bot, Store, Shield,
  ChevronDown, ArrowUpRight, Copy, FlaskConical,
  Users, ExternalLink, Home, Eye, Trophy,
  LogIn, LogOut, User, Menu, Radio, Crown, Share2, Heart, Activity,
  MoreHorizontal, X
} from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
  DropdownMenuSeparator, DropdownMenuLabel
} from "./ui/dropdown-menu";
import { useWallet } from "../contexts/WalletContext";
import { useAuth } from "../contexts/AuthContext";
import { useDemoMode } from "../contexts/DemoModeContext";
import { BrandLockup } from "./BrandComponents";
import { TierBadge } from "../pages/PricingPage";
import NotificationBell from "./NotificationBell";
import { Beaker } from "lucide-react";

const Navigation = () => {
  const { wallet, connectWallet, disconnectWallet, loading: walletLoading, chainId, ethBalance, switchToSepolia } = useWallet();
  const { user, isAuthenticated, logout, isPro } = useAuth();
  const { isDemoMode, toggleDemoMode, shareDemoLink } = useDemoMode();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const publicNavItems = [
    { path: "/", label: "Home", icon: Home },
    { path: "/leaderboard", label: "Leaderboard", icon: Trophy },
    { path: "/pricing", label: "Pricing", icon: Crown },
  ];

  // Priority-ordered: first 5 are always visible, rest go into "More"
  const primaryItems = [
    { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
    { path: "/leaderboard", label: "Leaderboard", icon: Trophy },
    { path: "/research", label: "Research", icon: Beaker },
    { path: "/lab", label: "Strategy Lab", icon: FlaskConical },
    { path: "/alerts", label: "Alerts", icon: Radio },
  ];

  const overflowItems = [
    { path: "/simulation", label: "Simulation", icon: Radio },
    { path: "/agents", label: "AI Agents", icon: Bot },
    { path: "/events", label: "Event Agents", icon: Eye },
    { path: "/marketplace", label: "Marketplace", icon: Store },
    { path: "/copy-trading", label: "Copy Trading", icon: Copy },
    { path: "/following", label: "Following", icon: Heart },
    { path: "/referrals", label: "Referrals", icon: Users },
    { path: "/pricing", label: "Pricing", icon: Crown },
  ];

  const adminItems = [
    { path: "/admin", label: "Admin Panel", icon: Shield },
    { path: "/admin/analytics", label: "Demo Analytics", icon: BarChart3 },
    { path: "/admin/traffic", label: "Traffic", icon: Activity },
  ];

  const allAuthItems = [
    { path: "/", label: "Home", icon: Home },
    ...primaryItems,
    ...overflowItems,
    ...adminItems,
  ];

  const isLoggedIn = isAuthenticated || isDemoMode;
  const isOnSepolia = chainId === 11155111;

  // Check if current path matches an overflow or admin item (to highlight "More")
  const overflowPaths = [...overflowItems, ...adminItems].map(i => i.path);
  const isOverflowActive = overflowPaths.includes(location.pathname);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-2 sm:px-3 md:px-4 lg:px-6 py-3">
      <div className="max-w-7xl mx-auto">
        <div className="glass rounded-2xl px-3 sm:px-4 md:px-5 lg:px-6 py-3 flex items-center justify-between gap-2 md:gap-3 overflow-hidden">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 shrink-0" data-testid="nav-logo">
            <BrandLockup size="default" showSubtitle={false} />
          </Link>

          {/* Desktop Nav Items */}
          <div className="hidden md:flex items-center gap-0.5 lg:gap-1 min-w-0 flex-1 justify-center">
            {isLoggedIn ? (
              <>
                {/* Primary items — always visible */}
                {primaryItems.map((item) => (
                  <Link
                    key={item.path}
                    to={item.path}
                    data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                    className={`px-2.5 lg:px-3.5 py-1.5 rounded-full text-xs lg:text-sm font-medium transition-all whitespace-nowrap shrink-0 ${
                      location.pathname === item.path
                        ? "bg-white/10 text-white"
                        : "text-zinc-400 hover:text-white hover:bg-white/5"
                    }`}
                  >
                    {item.label}
                  </Link>
                ))}

                {/* "More" dropdown for overflow + admin items */}
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button
                      className={`px-2.5 lg:px-3.5 py-1.5 rounded-full text-xs lg:text-sm font-medium transition-all whitespace-nowrap shrink-0 flex items-center gap-1 ${
                        isOverflowActive
                          ? "bg-white/10 text-white"
                          : "text-zinc-400 hover:text-white hover:bg-white/5"
                      }`}
                      data-testid="nav-more-dropdown"
                    >
                      More
                      <ChevronDown className="w-3 h-3" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="center" className="bg-[#121212] border-zinc-800 w-52" data-testid="nav-more-menu">
                    <DropdownMenuLabel className="text-[10px] text-zinc-600 uppercase tracking-wider">Features</DropdownMenuLabel>
                    {overflowItems.map((item) => (
                      <DropdownMenuItem
                        key={item.path}
                        onClick={() => navigate(item.path)}
                        className={`cursor-pointer ${location.pathname === item.path ? "bg-white/5 text-white" : ""}`}
                        data-testid={`nav-more-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
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
                        data-testid={`nav-more-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                      >
                        <item.icon className="w-4 h-4 mr-2.5 text-zinc-500" />
                        {item.label}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </>
            ) : (
              publicNavItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                  className={`px-3 lg:px-4 py-1.5 rounded-full text-xs lg:text-sm font-medium transition-all whitespace-nowrap ${
                    location.pathname === item.path
                      ? "bg-white/10 text-white"
                      : "text-zinc-400 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {item.label}
                </Link>
              ))
            )}
          </div>

          {/* Right side actions */}
          <div className="flex items-center gap-1.5 sm:gap-2 lg:gap-3 shrink-0">
            {isLoggedIn ? (
              <>
                {/* Demo Mode Toggle */}
                <button
                  onClick={toggleDemoMode}
                  className={`hidden xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs font-medium transition-all border ${
                    isDemoMode
                      ? 'bg-[#7B61FF]/15 border-[#7B61FF]/40 text-[#7B61FF]'
                      : 'bg-transparent border-zinc-700 text-zinc-400 hover:border-zinc-500 hover:text-zinc-300'
                  }`}
                  data-testid="demo-mode-toggle"
                >
                  <Eye className="w-3.5 h-3.5" />
                  Demo
                  <div className={`w-7 h-4 rounded-full p-0.5 transition-colors ${isDemoMode ? 'bg-[#7B61FF]' : 'bg-zinc-700'}`}>
                    <div className={`w-3 h-3 rounded-full bg-white transition-transform ${isDemoMode ? 'translate-x-3' : 'translate-x-0'}`} />
                  </div>
                </button>

                {/* Share Demo Button */}
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
                
                {wallet && (
                  <>
                    {chainId && (
                      <Badge 
                        className={`hidden lg:flex ${isOnSepolia ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-[#FFB800]/20 text-[#FFB800] cursor-pointer'}`}
                        onClick={!isOnSepolia ? switchToSepolia : undefined}
                        data-testid="network-badge"
                      >
                        {isOnSepolia ? 'Sepolia' : 'Wrong Net'}
                      </Badge>
                    )}
                    
                    {ethBalance && (
                      <div className="hidden xl:flex items-center gap-1 px-2.5 py-1 rounded-full bg-zinc-800/50 border border-zinc-700">
                        <span className="text-[10px] text-zinc-400">ETH</span>
                        <span className="text-xs font-mono font-bold text-white">{parseFloat(ethBalance).toFixed(4)}</span>
                      </div>
                    )}
                  </>
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
                      
                      {wallet ? (
                        <>
                          <DropdownMenuItem onClick={() => navigator.clipboard.writeText(wallet)}>
                            <Copy className="w-4 h-4 mr-2" />Copy Wallet
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => window.open(`https://sepolia.etherscan.io/address/${wallet}`, '_blank')}>
                            <ExternalLink className="w-4 h-4 mr-2" />View on Etherscan
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={disconnectWallet} className="text-[#FFB800]">
                            <Wallet className="w-4 h-4 mr-2" />Disconnect Wallet
                          </DropdownMenuItem>
                        </>
                      ) : (
                        <DropdownMenuItem onClick={connectWallet}>
                          <Wallet className="w-4 h-4 mr-2" />Connect Wallet
                        </DropdownMenuItem>
                      )}
                      
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
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" size="sm" className="rounded-full text-zinc-400 hover:text-white h-8 px-3 text-xs" data-testid="login-nav-btn">
                    <LogIn className="w-3.5 h-3.5 mr-1.5" />
                    Sign In
                  </Button>
                </Link>
                <Link to="/register">
                  <Button size="sm" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 glow-primary h-8 px-3 text-xs" data-testid="register-nav-btn">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
            
            {/* Mobile menu button */}
            <Button variant="ghost" size="icon" className="md:hidden h-8 w-8" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="mobile-menu-btn">
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="md:hidden glass rounded-2xl mt-2 p-3 max-h-[70vh] overflow-y-auto">
              {(isLoggedIn ? allAuthItems : publicNavItems).map((item) => (
                <Link key={item.path} to={item.path} onClick={() => setMobileMenuOpen(false)} className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm ${location.pathname === item.path ? "bg-white/10 text-white" : "text-zinc-400"}`}>
                  <item.icon className="w-4 h-4" />{item.label}
                </Link>
              ))}
              {!isAuthenticated && !isDemoMode && (
                <div className="mt-3 pt-3 border-t border-zinc-800 space-y-2">
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-zinc-400">
                    <LogIn className="w-4 h-4" />Sign In
                  </Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm bg-[#7B61FF] text-white">
                    <User className="w-4 h-4" />Get Started
                  </Link>
                </div>
              )}
              {isLoggedIn && (
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
                  {!isAuthenticated && isDemoMode && (
                    <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm bg-[#7B61FF] text-white mt-2">
                      <User className="w-4 h-4" />Sign Up Free
                    </Link>
                  )}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
};

export default Navigation;
