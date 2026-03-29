import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Wallet, BarChart3, Bot, Store, Shield,
  ChevronDown, ArrowUpRight, Copy, FlaskConical,
  Users, ExternalLink, Home, Eye, Trophy,
  LogIn, LogOut, User, Menu, Radio, Crown, Share2, Heart
} from "lucide-react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
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
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const publicNavItems = [
    { path: "/", label: "Home", icon: Home },
    { path: "/leaderboard", label: "Leaderboard", icon: Trophy },
    { path: "/pricing", label: "Pricing", icon: Crown },
  ];

  const authNavItems = [
    { path: "/", label: "Home", icon: Home },
    { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
    { path: "/simulation", label: "Simulation", icon: Radio },
    { path: "/research", label: "Research", icon: Beaker },
    { path: "/agents", label: "AI Agents", icon: Bot },
    { path: "/events", label: "Event Agents", icon: Eye },
    { path: "/lab", label: "Strategy Lab", icon: FlaskConical },
    { path: "/marketplace", label: "Marketplace", icon: Store },
    { path: "/referrals", label: "Referrals", icon: Users },
    { path: "/copy-trading", label: "Copy Trading", icon: Copy },
    { path: "/leaderboard", label: "Leaderboard", icon: Trophy },
    { path: "/following", label: "Following", icon: Heart },
    { path: "/alerts", label: "Alerts", icon: Radio },
    { path: "/pricing", label: "Pricing", icon: Crown },
    { path: "/admin", label: "Admin", icon: Shield },
    { path: "/admin/analytics", label: "Demo Analytics", icon: BarChart3 },
  ];

  const navItems = (isAuthenticated || isDemoMode) ? authNavItems : publicNavItems;

  const isOnSepolia = chainId === 11155111;

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3">
      <div className="max-w-7xl mx-auto">
        <div className="glass rounded-2xl px-6 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="nav-logo">
            <BrandLockup size="default" showSubtitle={false} />
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  location.pathname === item.path
                    ? "bg-white/10 text-white"
                    : "text-zinc-400 hover:text-white hover:bg-white/5"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </div>

          <div className="flex items-center gap-3">
            {(isAuthenticated || isDemoMode) ? (
              <>
                {/* Demo Mode Toggle */}
                <button
                  onClick={toggleDemoMode}
                  className={`hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
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
                    className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all border border-[#00FF94]/30 text-[#00FF94]/80 hover:bg-[#00FF94]/10 hover:text-[#00FF94] hover:border-[#00FF94]/50"
                    data-testid="share-demo-btn"
                  >
                    <Share2 className="w-3.5 h-3.5" />
                    Share Demo
                  </button>
                )}

                {(isPro || isDemoMode) && (
                  <Badge className="bg-gradient-to-r from-[#7B61FF] to-[#00FF94] text-white" data-testid="pro-badge">
                    PRO
                  </Badge>
                )}
                
                {wallet && (
                  <>
                    {chainId && (
                      <Badge 
                        className={`${isOnSepolia ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-[#FFB800]/20 text-[#FFB800] cursor-pointer'}`}
                        onClick={!isOnSepolia ? switchToSepolia : undefined}
                        data-testid="network-badge"
                      >
                        {isOnSepolia ? '⚡ Sepolia' : '⚠️ Wrong Network'}
                      </Badge>
                    )}
                    
                    {ethBalance && (
                      <div className="hidden sm:flex items-center gap-1 px-3 py-1 rounded-full bg-zinc-800/50 border border-zinc-700">
                        <span className="text-xs text-zinc-400">ETH</span>
                        <span className="text-sm font-mono font-bold text-white">{parseFloat(ethBalance).toFixed(4)}</span>
                      </div>
                    )}
                  </>
                )}
                
                {isAuthenticated ? (
                  <>
                  <NotificationBell />
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline" className="rounded-full border-[#7B61FF]/30 hover:border-[#7B61FF] bg-[#7B61FF]/10" data-testid="user-dropdown">
                        <User className="w-4 h-4 mr-2 text-[#7B61FF]" />
                        {user?.name?.split(' ')[0] || 'User'}
                        <ChevronDown className="w-4 h-4 ml-2" />
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
                      <Button className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-xs px-4" data-testid="demo-signup-btn">
                        Sign Up Free
                      </Button>
                    </Link>
                  </>
                ) : null}
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" className="rounded-full text-zinc-400 hover:text-white" data-testid="login-nav-btn">
                    <LogIn className="w-4 h-4 mr-2" />
                    Sign In
                  </Button>
                </Link>
                <Link to="/register">
                  <Button className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 glow-primary" data-testid="register-nav-btn">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
            
            <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="mobile-menu-btn">
              <Menu className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="md:hidden glass rounded-2xl mt-2 p-4">
              {navItems.map((item) => (
                <Link key={item.path} to={item.path} onClick={() => setMobileMenuOpen(false)} className={`flex items-center gap-3 px-4 py-3 rounded-xl ${location.pathname === item.path ? "bg-white/10 text-white" : "text-zinc-400"}`}>
                  <item.icon className="w-5 h-5" />{item.label}
                </Link>
              ))}
              {!isAuthenticated && !isDemoMode && (
                <div className="mt-4 pt-4 border-t border-zinc-800 space-y-2">
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-xl text-zinc-400">
                    <LogIn className="w-5 h-5" />Sign In
                  </Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#7B61FF] text-white">
                    <User className="w-5 h-5" />Get Started
                  </Link>
                </div>
              )}
              {(isAuthenticated || isDemoMode) && (
                <div className="mt-4 pt-4 border-t border-zinc-800 space-y-1">
                  <button
                    onClick={() => { toggleDemoMode(); setMobileMenuOpen(false); }}
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl w-full ${isDemoMode ? 'text-[#7B61FF] bg-[#7B61FF]/10' : 'text-zinc-400'}`}
                    data-testid="demo-mode-toggle-mobile"
                  >
                    <Eye className="w-5 h-5" />
                    Demo Mode
                    <div className={`ml-auto w-7 h-4 rounded-full p-0.5 transition-colors ${isDemoMode ? 'bg-[#7B61FF]' : 'bg-zinc-700'}`}>
                      <div className={`w-3 h-3 rounded-full bg-white transition-transform ${isDemoMode ? 'translate-x-3' : 'translate-x-0'}`} />
                    </div>
                  </button>
                  {isDemoMode && (
                    <button
                      onClick={() => { shareDemoLink(); setMobileMenuOpen(false); }}
                      className="flex items-center gap-3 px-4 py-3 rounded-xl w-full text-[#00FF94]/80 hover:bg-[#00FF94]/10"
                      data-testid="share-demo-btn-mobile"
                    >
                      <Share2 className="w-5 h-5" />
                      Share Demo Link
                    </button>
                  )}
                  {!isAuthenticated && isDemoMode && (
                    <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#7B61FF] text-white mt-2">
                      <User className="w-5 h-5" />Sign Up Free
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
