import { useState } from "react";
import { Link, useLocation, Outlet } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Home, Trophy, Crown, LogIn, User, Menu, X, BarChart3 } from "lucide-react";
import { Button } from "./ui/button";
import { BrandLockup } from "./BrandComponents";
import { useAuth } from "../contexts/AuthContext";

const navItems = [
  { path: "/", label: "Home", icon: Home },
  { path: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { path: "/pricing", label: "Pricing", icon: Crown },
];

const MarketingLayout = () => {
  const location = useLocation();
  const { isAuthenticated } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 px-2 sm:px-3 md:px-4 lg:px-6 py-3" data-testid="marketing-layout-nav">
        <div className="max-w-7xl mx-auto">
          <div className="glass rounded-2xl px-3 sm:px-4 md:px-5 lg:px-6 py-3 flex items-center justify-between gap-2 md:gap-3 overflow-hidden">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-2 shrink-0" data-testid="marketing-nav-logo">
              <BrandLockup size="default" showSubtitle={false} />
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-0.5 lg:gap-1 min-w-0 flex-1 justify-center">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`marketing-nav-${item.label.toLowerCase().replace(/\s+/g, '-')}`}
                  className={`px-3 lg:px-4 py-1.5 rounded-full text-xs lg:text-sm font-medium transition-all whitespace-nowrap ${
                    location.pathname === item.path
                      ? "bg-white/10 text-white"
                      : "text-zinc-400 hover:text-white hover:bg-white/5"
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </div>

            {/* Right side */}
            <div className="flex items-center gap-1.5 sm:gap-2 lg:gap-3 shrink-0">
              {isAuthenticated ? (
                <Link to="/dashboard">
                  <Button size="sm" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 glow-primary h-8 px-3 text-xs" data-testid="marketing-go-dashboard-btn">
                    <BarChart3 className="w-3.5 h-3.5 mr-1.5" />
                    Dashboard
                  </Button>
                </Link>
              ) : (
                <>
                  <Link to="/login">
                    <Button variant="ghost" size="sm" className="rounded-full text-zinc-400 hover:text-white h-8 px-3 text-xs" data-testid="marketing-login-btn">
                      <LogIn className="w-3.5 h-3.5 mr-1.5" />
                      Sign In
                    </Button>
                  </Link>
                  <Link to="/register">
                    <Button size="sm" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 glow-primary h-8 px-3 text-xs" data-testid="marketing-register-btn">
                      Get Started
                    </Button>
                  </Link>
                </>
              )}

              {/* Mobile menu button */}
              <Button variant="ghost" size="icon" className="md:hidden h-8 w-8" onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="marketing-mobile-menu-btn">
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </Button>
            </div>
          </div>

          {/* Mobile menu */}
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="md:hidden glass rounded-2xl mt-2 p-3">
                {navItems.map((item) => (
                  <Link key={item.path} to={item.path} onClick={() => setMobileMenuOpen(false)} className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm ${location.pathname === item.path ? "bg-white/10 text-white" : "text-zinc-400"}`}>
                    <item.icon className="w-4 h-4" />{item.label}
                  </Link>
                ))}
                <div className="mt-3 pt-3 border-t border-zinc-800 space-y-2">
                  {isAuthenticated ? (
                    <Link to="/dashboard" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm bg-[#7B61FF] text-white">
                      <BarChart3 className="w-4 h-4" />Dashboard
                    </Link>
                  ) : (
                    <>
                      <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-zinc-400">
                        <LogIn className="w-4 h-4" />Sign In
                      </Link>
                      <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm bg-[#7B61FF] text-white">
                        <User className="w-4 h-4" />Get Started
                      </Link>
                    </>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </nav>

      {/* Page content */}
      <Outlet />
    </>
  );
};

export default MarketingLayout;
