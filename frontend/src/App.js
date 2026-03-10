import { useState, useEffect, createContext, useContext } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Wallet, TrendingUp, BarChart3, Bot, Store, Shield, Settings,
  ChevronDown, ArrowUpRight, ArrowDownRight, Activity, Zap,
  AlertTriangle, Check, X, Menu, Home, PieChart, LineChart,
  Clock, Users, DollarSign, Percent, Target, Brain, Cpu,
  RefreshCw, ExternalLink, Copy, Sparkles
} from "lucide-react";
import {
  LineChart as ReLineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart as RePieChart, Pie,
  Cell, AreaChart, Area, BarChart, Bar
} from "recharts";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./components/ui/card";
import { Badge } from "./components/ui/badge";
import { Input } from "./components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Progress } from "./components/ui/progress";
import { ScrollArea } from "./components/ui/scroll-area";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from "./components/ui/dialog";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger
} from "./components/ui/dropdown-menu";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "./components/ui/select";
import "@/App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for wallet
const WalletContext = createContext();

const useWallet = () => useContext(WalletContext);

// Wallet Provider
const WalletProvider = ({ children }) => {
  const [wallet, setWallet] = useState(null);
  const [investor, setInvestor] = useState(null);
  const [loading, setLoading] = useState(false);

  const connectWallet = async () => {
    setLoading(true);
    try {
      if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const address = accounts[0];
        setWallet(address);
        
        const response = await axios.post(`${API}/investors/register`, { wallet_address: address });
        setInvestor(response.data);
        toast.success("Wallet connected successfully!");
      } else {
        // Demo mode
        const demoAddress = "0x" + Math.random().toString(16).slice(2, 42);
        setWallet(demoAddress);
        const response = await axios.post(`${API}/investors/register`, { wallet_address: demoAddress });
        setInvestor(response.data);
        toast.success("Demo wallet connected!");
      }
    } catch (error) {
      console.error("Wallet connection error:", error);
      toast.error("Failed to connect wallet");
    }
    setLoading(false);
  };

  const disconnectWallet = () => {
    setWallet(null);
    setInvestor(null);
    toast.info("Wallet disconnected");
  };

  const refreshInvestor = async () => {
    if (wallet) {
      try {
        const response = await axios.get(`${API}/investors/${wallet}`);
        setInvestor(response.data);
      } catch (error) {
        console.error("Error refreshing investor:", error);
      }
    }
  };

  return (
    <WalletContext.Provider value={{ wallet, investor, loading, connectWallet, disconnectWallet, refreshInvestor }}>
      {children}
    </WalletContext.Provider>
  );
};

// Format helpers
const formatCurrency = (value) => {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(2)}K`;
  return `$${value?.toFixed(2) || '0.00'}`;
};

const formatAddress = (address) => {
  if (!address) return '';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

// Navigation Component
const Navigation = () => {
  const { wallet, connectWallet, disconnectWallet, loading } = useWallet();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: "/", label: "Home", icon: Home },
    { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
    { path: "/agents", label: "AI Agents", icon: Bot },
    { path: "/marketplace", label: "Marketplace", icon: Store },
    { path: "/analytics", label: "Analytics", icon: LineChart },
    { path: "/admin", label: "Admin", icon: Shield },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-4 py-3">
      <div className="max-w-7xl mx-auto">
        <div className="glass rounded-2xl px-6 py-3 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3" data-testid="nav-logo">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold font-['Outfit']">AlphaAI</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                data-testid={`nav-${item.label.toLowerCase()}`}
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

          {/* Wallet Button */}
          <div className="flex items-center gap-3">
            {wallet ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    className="rounded-full border-[#7B61FF]/30 hover:border-[#7B61FF] bg-[#7B61FF]/10"
                    data-testid="wallet-dropdown"
                  >
                    <Wallet className="w-4 h-4 mr-2 text-[#7B61FF]" />
                    {formatAddress(wallet)}
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-[#121212] border-zinc-800">
                  <DropdownMenuItem onClick={() => navigator.clipboard.writeText(wallet)}>
                    <Copy className="w-4 h-4 mr-2" />
                    Copy Address
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={disconnectWallet} className="text-red-400">
                    <X className="w-4 h-4 mr-2" />
                    Disconnect
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button
                onClick={connectWallet}
                disabled={loading}
                className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 glow-primary"
                data-testid="connect-wallet-btn"
              >
                <Wallet className="w-4 h-4 mr-2" />
                {loading ? "Connecting..." : "Connect Wallet"}
              </Button>
            )}

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-menu-btn"
            >
              <Menu className="w-5 h-5" />
            </Button>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="md:hidden glass rounded-2xl mt-2 p-4"
            >
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
                    location.pathname === item.path
                      ? "bg-white/10 text-white"
                      : "text-zinc-400"
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </Link>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
};

// Landing Page
const LandingPage = () => {
  const { connectWallet, wallet, loading } = useWallet();
  const [fundStats, setFundStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get(`${API}/fund/stats`);
        setFundStats(response.data);
      } catch (error) {
        console.error("Error fetching stats:", error);
      }
    };
    fetchStats();
  }, []);

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="relative px-4 py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0 grid-pattern opacity-50" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#7B61FF]/20 rounded-full blur-[120px]" />
        
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center max-w-4xl mx-auto"
          >
            <Badge className="mb-6 bg-[#7B61FF]/20 text-[#7B61FF] border-[#7B61FF]/30" data-testid="hero-badge">
              <Sparkles className="w-3 h-3 mr-1" />
              AI-Powered Hedge Fund
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 font-['Outfit'] tracking-tight" data-testid="hero-title">
              <span className="text-gradient">Autonomous Trading</span>
              <br />
              <span className="text-gradient-primary">Powered by AI</span>
            </h1>
            
            <p className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl mx-auto" data-testid="hero-description">
              Deploy capital into our AI-managed vault. Multi-agent trading system
              analyzes markets 24/7, executing optimal strategies across DeFi.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {wallet ? (
                <Link to="/dashboard">
                  <Button
                    size="lg"
                    className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary btn-hover-lift"
                    data-testid="go-to-dashboard-btn"
                  >
                    Go to Dashboard
                    <ArrowUpRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
              ) : (
                <Button
                  size="lg"
                  onClick={connectWallet}
                  disabled={loading}
                  className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary btn-hover-lift"
                  data-testid="hero-connect-wallet-btn"
                >
                  <Wallet className="w-5 h-5 mr-2" />
                  {loading ? "Connecting..." : "Connect Wallet"}
                </Button>
              )}
              <Link to="/marketplace">
                <Button
                  size="lg"
                  variant="outline"
                  className="rounded-full border-zinc-700 hover:border-zinc-600 px-8 btn-hover-lift"
                  data-testid="explore-agents-btn"
                >
                  Explore AI Agents
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Stats Grid */}
          {fundStats && (
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-20"
            >
              <Card className="glass-card card-hover" data-testid="stat-nav">
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-zinc-500 mb-2">Fund NAV</p>
                  <p className="text-2xl md:text-3xl font-bold text-white font-['JetBrains_Mono']">
                    {formatCurrency(fundStats.nav)}
                  </p>
                  <p className={`text-sm mt-1 flex items-center justify-center gap-1 ${fundStats.nav_change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                    {fundStats.nav_change_24h >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {fundStats.nav_change_24h}%
                  </p>
                </CardContent>
              </Card>

              <Card className="glass-card card-hover" data-testid="stat-aum">
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-zinc-500 mb-2">Total AUM</p>
                  <p className="text-2xl md:text-3xl font-bold text-white font-['JetBrains_Mono']">
                    {formatCurrency(fundStats.total_aum)}
                  </p>
                </CardContent>
              </Card>

              <Card className="glass-card card-hover" data-testid="stat-sharpe">
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-zinc-500 mb-2">Sharpe Ratio</p>
                  <p className="text-2xl md:text-3xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">
                    {fundStats.sharpe_ratio}
                  </p>
                </CardContent>
              </Card>

              <Card className="glass-card card-hover" data-testid="stat-return">
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-zinc-500 mb-2">Monthly Return</p>
                  <p className={`text-2xl md:text-3xl font-bold font-['JetBrains_Mono'] ${fundStats.monthly_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                    {fundStats.monthly_return >= 0 ? '+' : ''}{fundStats.monthly_return}%
                  </p>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section className="px-4 py-20 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold font-['Outfit'] mb-4" data-testid="features-title">
              Multi-Agent Trading System
            </h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">
              Five specialized AI agents work in harmony to analyze, strategize, and execute trades
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Activity,
                title: "Data Collector",
                description: "Aggregates market data from exchanges, on-chain metrics, and sentiment feeds",
                color: "#00FF94"
              },
              {
                icon: Brain,
                title: "Decision Agent",
                description: "Uses ML models to analyze signals and predict price movements",
                color: "#7B61FF"
              },
              {
                icon: Target,
                title: "Strategy Agent",
                description: "Optimizes capital allocation across arbitrage, momentum, and yield strategies",
                color: "#FF6B6B"
              },
              {
                icon: Zap,
                title: "Execution Agent",
                description: "Executes trades with optimal gas fees and minimal slippage",
                color: "#FFB800"
              },
              {
                icon: Shield,
                title: "Risk Agent",
                description: "Enforces stop-loss limits and prevents portfolio drawdowns",
                color: "#00D4FF"
              },
              {
                icon: Store,
                title: "Marketplace",
                description: "Deploy your own AI agents and earn revenue from subscribers",
                color: "#FF61DC"
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="glass-card card-hover h-full" data-testid={`feature-${feature.title.toLowerCase().replace(' ', '-')}`}>
                  <CardContent className="p-6">
                    <div
                      className="w-12 h-12 rounded-xl flex items-center justify-center mb-4"
                      style={{ backgroundColor: `${feature.color}20` }}
                    >
                      <feature.icon className="w-6 h-6" style={{ color: feature.color }} />
                    </div>
                    <h3 className="text-xl font-semibold mb-2 font-['Outfit']">{feature.title}</h3>
                    <p className="text-zinc-400 text-sm">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-4 py-20">
        <div className="max-w-4xl mx-auto">
          <Card className="glass-card overflow-hidden relative" data-testid="cta-section">
            <div className="absolute inset-0 bg-gradient-to-br from-[#7B61FF]/20 to-transparent" />
            <CardContent className="p-12 text-center relative z-10">
              <h2 className="text-3xl md:text-4xl font-bold font-['Outfit'] mb-4">
                Start Earning with AI Trading
              </h2>
              <p className="text-zinc-400 mb-8 max-w-xl mx-auto">
                Minimum investment of $100. Withdraw anytime. No lock-up periods.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/dashboard">
                  <Button
                    size="lg"
                    className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary"
                    data-testid="cta-invest-btn"
                  >
                    Start Investing
                    <ArrowUpRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
                <Link to="/agents">
                  <Button
                    size="lg"
                    variant="outline"
                    className="rounded-full border-zinc-700 px-8"
                    data-testid="cta-learn-btn"
                  >
                    Learn More
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-zinc-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-[#7B61FF]" />
            <span className="font-semibold">AlphaAI Fund</span>
          </div>
          <p className="text-sm text-zinc-500">
            © 2025 AlphaAI Fund. Testnet deployment for demonstration purposes.
          </p>
        </div>
      </footer>
    </div>
  );
};

// Dashboard Page
const DashboardPage = () => {
  const { wallet, investor, refreshInvestor } = useWallet();
  const [fundStats, setFundStats] = useState(null);
  const [allocation, setAllocation] = useState([]);
  const [performanceHistory, setPerformanceHistory] = useState([]);
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [depositLoading, setDepositLoading] = useState(false);
  const [withdrawLoading, setWithdrawLoading] = useState(false);
  const [showDepositDialog, setShowDepositDialog] = useState(false);
  const [showWithdrawDialog, setShowWithdrawDialog] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, allocRes, perfRes] = await Promise.all([
          axios.get(`${API}/fund/stats`),
          axios.get(`${API}/fund/allocation`),
          axios.get(`${API}/fund/performance-history`)
        ]);
        setFundStats(statsRes.data);
        setAllocation(allocRes.data);
        setPerformanceHistory(perfRes.data);
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      }
    };
    fetchData();
  }, []);

  const handleDeposit = async () => {
    if (!wallet || !depositAmount || parseFloat(depositAmount) < 100) {
      toast.error("Minimum deposit is $100");
      return;
    }
    setDepositLoading(true);
    try {
      const response = await axios.post(`${API}/investors/deposit`, {
        wallet_address: wallet,
        amount: parseFloat(depositAmount)
      });
      toast.success(response.data.message);
      setDepositAmount('');
      setShowDepositDialog(false);
      refreshInvestor();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Deposit failed");
    }
    setDepositLoading(false);
  };

  const handleWithdraw = async () => {
    if (!wallet || !withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      toast.error("Enter a valid amount");
      return;
    }
    setWithdrawLoading(true);
    try {
      const response = await axios.post(`${API}/investors/withdraw`, {
        wallet_address: wallet,
        amount: parseFloat(withdrawAmount)
      });
      toast.success(response.data.message);
      setWithdrawAmount('');
      setShowWithdrawDialog(false);
      refreshInvestor();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Withdrawal failed");
    }
    setWithdrawLoading(false);
  };

  if (!wallet) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <Card className="glass-card max-w-md w-full" data-testid="connect-wallet-prompt">
          <CardContent className="p-8 text-center">
            <Wallet className="w-16 h-16 mx-auto mb-4 text-[#7B61FF]" />
            <h2 className="text-2xl font-bold mb-2">Connect Your Wallet</h2>
            <p className="text-zinc-400 mb-6">Connect your wallet to view your dashboard</p>
            <WalletConnectButton />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="dashboard-title">
              Investor Dashboard
            </h1>
            <p className="text-zinc-400 mt-1">Welcome back, {formatAddress(wallet)}</p>
          </div>
          <div className="flex gap-3">
            <Button
              onClick={() => setShowDepositDialog(true)}
              className="rounded-full bg-[#00FF94] text-black hover:bg-[#00FF94]/90"
              data-testid="deposit-btn"
            >
              <ArrowUpRight className="w-4 h-4 mr-2" />
              Deposit
            </Button>
            <Button
              onClick={() => setShowWithdrawDialog(true)}
              variant="outline"
              className="rounded-full border-zinc-700"
              data-testid="withdraw-btn"
            >
              <ArrowDownRight className="w-4 h-4 mr-2" />
              Withdraw
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card" data-testid="investor-balance">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-500">Your Balance</span>
                <DollarSign className="w-4 h-4 text-[#00FF94]" />
              </div>
              <p className="text-2xl font-bold font-['JetBrains_Mono']">
                {formatCurrency(investor?.balance || 0)}
              </p>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="investor-shares">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-500">Your Shares</span>
                <PieChart className="w-4 h-4 text-[#7B61FF]" />
              </div>
              <p className="text-2xl font-bold font-['JetBrains_Mono']">
                {investor?.shares?.toFixed(4) || '0.0000'}
              </p>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="fund-nav-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-500">Fund NAV</span>
                <TrendingUp className="w-4 h-4 text-[#00FF94]" />
              </div>
              <p className="text-2xl font-bold font-['JetBrains_Mono']">
                {formatCurrency(fundStats?.nav || 0)}
              </p>
              <p className={`text-xs mt-1 ${fundStats?.nav_change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                {fundStats?.nav_change_24h >= 0 ? '+' : ''}{fundStats?.nav_change_24h}% (24h)
              </p>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="monthly-return-card">
            <CardContent className="p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-zinc-500">Monthly Return</span>
                <Percent className="w-4 h-4 text-[#FFB800]" />
              </div>
              <p className={`text-2xl font-bold font-['JetBrains_Mono'] ${fundStats?.monthly_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                {fundStats?.monthly_return >= 0 ? '+' : ''}{fundStats?.monthly_return}%
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row */}
        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          {/* Performance Chart */}
          <Card className="glass-card lg:col-span-2" data-testid="performance-chart">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="w-5 h-5 text-[#7B61FF]" />
                Performance History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceHistory}>
                    <defs>
                      <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#7B61FF" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#7B61FF" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis dataKey="date" stroke="#71717A" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#71717A" tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#121212',
                        border: '1px solid #7B61FF',
                        borderRadius: '8px'
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="value"
                      stroke="#7B61FF"
                      fillOpacity={1}
                      fill="url(#colorValue)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Allocation Chart */}
          <Card className="glass-card" data-testid="allocation-chart">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="w-5 h-5 text-[#00FF94]" />
                Portfolio Allocation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie
                      data={allocation}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${value}%`}
                      labelLine={false}
                    >
                      {allocation.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#121212',
                        border: '1px solid #27272A',
                        borderRadius: '8px'
                      }}
                    />
                  </RePieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">
                {allocation.map((item, index) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-zinc-400">{item.name}</span>
                    </div>
                    <span className="font-mono">{item.value}%</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Fund Metrics */}
        <Card className="glass-card" data-testid="fund-metrics">
          <CardHeader>
            <CardTitle>Fund Metrics</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div>
                <p className="text-sm text-zinc-500 mb-1">Sharpe Ratio</p>
                <p className="text-xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">
                  {fundStats?.sharpe_ratio || '—'}
                </p>
              </div>
              <div>
                <p className="text-sm text-zinc-500 mb-1">Max Drawdown</p>
                <p className="text-xl font-bold text-red-400 font-['JetBrains_Mono']">
                  -{fundStats?.max_drawdown || '0'}%
                </p>
              </div>
              <div>
                <p className="text-sm text-zinc-500 mb-1">Active Strategies</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">
                  {fundStats?.active_strategies || '0'}
                </p>
              </div>
              <div>
                <p className="text-sm text-zinc-500 mb-1">24h Trades</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">
                  {fundStats?.total_trades_24h || '0'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Deposit Dialog */}
      <Dialog open={showDepositDialog} onOpenChange={setShowDepositDialog}>
        <DialogContent className="bg-[#121212] border-zinc-800" data-testid="deposit-dialog">
          <DialogHeader>
            <DialogTitle>Deposit Funds</DialogTitle>
            <DialogDescription>
              Deposit funds to receive fund shares. Minimum: $100
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              type="number"
              placeholder="Amount in USD"
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              className="bg-[#050505] border-zinc-800"
              data-testid="deposit-amount-input"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDepositDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleDeposit}
              disabled={depositLoading}
              className="bg-[#00FF94] text-black hover:bg-[#00FF94]/90"
              data-testid="confirm-deposit-btn"
            >
              {depositLoading ? "Processing..." : "Confirm Deposit"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Withdraw Dialog */}
      <Dialog open={showWithdrawDialog} onOpenChange={setShowWithdrawDialog}>
        <DialogContent className="bg-[#121212] border-zinc-800" data-testid="withdraw-dialog">
          <DialogHeader>
            <DialogTitle>Withdraw Funds</DialogTitle>
            <DialogDescription>
              Withdraw funds from your balance. Available: {formatCurrency(investor?.balance || 0)}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Input
              type="number"
              placeholder="Amount in USD"
              value={withdrawAmount}
              onChange={(e) => setWithdrawAmount(e.target.value)}
              className="bg-[#050505] border-zinc-800"
              data-testid="withdraw-amount-input"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowWithdrawDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleWithdraw}
              disabled={withdrawLoading}
              className="bg-red-500 hover:bg-red-600"
              data-testid="confirm-withdraw-btn"
            >
              {withdrawLoading ? "Processing..." : "Confirm Withdrawal"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Wallet Connect Button Component
const WalletConnectButton = () => {
  const { connectWallet, loading } = useWallet();
  return (
    <Button
      onClick={connectWallet}
      disabled={loading}
      className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary"
      data-testid="wallet-connect-btn"
    >
      <Wallet className="w-5 h-5 mr-2" />
      {loading ? "Connecting..." : "Connect Wallet"}
    </Button>
  );
};

// AI Agents Page
const AgentsPage = () => {
  const [agents, setAgents] = useState([]);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('bitcoin');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [agentsRes, tradesRes] = await Promise.all([
          axios.get(`${API}/agents`),
          axios.get(`${API}/trades?limit=10`)
        ]);
        setAgents(agentsRes.data);
        setTrades(tradesRes.data);
      } catch (error) {
        console.error("Error fetching agents:", error);
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  const runAIAnalysis = async () => {
    setAnalysisLoading(true);
    try {
      const response = await axios.post(`${API}/ai/analyze`, {
        symbol: selectedSymbol,
        timeframe: "1d"
      });
      setAnalysisResult(response.data);
      toast.success("AI Analysis complete!");
    } catch (error) {
      toast.error("Analysis failed");
    }
    setAnalysisLoading(false);
  };

  const getAgentIcon = (type) => {
    switch (type) {
      case 'data': return Activity;
      case 'analysis': return Brain;
      case 'strategy': return Target;
      case 'execution': return Zap;
      case 'risk': return Shield;
      default: return Bot;
    }
  };

  const getAgentColor = (type) => {
    switch (type) {
      case 'data': return '#00FF94';
      case 'analysis': return '#7B61FF';
      case 'strategy': return '#FF6B6B';
      case 'execution': return '#FFB800';
      case 'risk': return '#00D4FF';
      default: return '#7B61FF';
    }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="agents-title">
            AI Trading Agents
          </h1>
          <p className="text-zinc-400 mt-1">Monitor and manage autonomous trading agents</p>
        </div>

        {/* AI Analysis Section */}
        <Card className="glass-card mb-8" data-testid="ai-analysis-section">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#7B61FF]" />
              AI Market Analysis
            </CardTitle>
            <CardDescription>
              Get real-time AI-powered market analysis and trading signals
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-4">
              <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                <SelectTrigger className="w-full md:w-[200px] bg-[#050505] border-zinc-800" data-testid="analysis-symbol-select">
                  <SelectValue placeholder="Select coin" />
                </SelectTrigger>
                <SelectContent className="bg-[#121212] border-zinc-800">
                  <SelectItem value="bitcoin">Bitcoin (BTC)</SelectItem>
                  <SelectItem value="ethereum">Ethereum (ETH)</SelectItem>
                  <SelectItem value="solana">Solana (SOL)</SelectItem>
                  <SelectItem value="cardano">Cardano (ADA)</SelectItem>
                </SelectContent>
              </Select>
              <Button
                onClick={runAIAnalysis}
                disabled={analysisLoading}
                className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
                data-testid="run-analysis-btn"
              >
                {analysisLoading ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="w-4 h-4 mr-2" />
                    Run Analysis
                  </>
                )}
              </Button>
            </div>

            {analysisResult && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-4 rounded-xl bg-[#050505] border border-zinc-800"
                data-testid="analysis-result"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Badge className="bg-[#7B61FF]/20 text-[#7B61FF]">
                      {analysisResult.symbol}
                    </Badge>
                    <span className="font-mono text-lg">${analysisResult.price?.toLocaleString()}</span>
                    <span className={`text-sm ${analysisResult.change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {analysisResult.change_24h >= 0 ? '+' : ''}{analysisResult.change_24h?.toFixed(2)}%
                    </span>
                  </div>
                  <span className="text-xs text-zinc-500">
                    {new Date(analysisResult.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="prose prose-invert max-w-none">
                  <p className="text-zinc-300 whitespace-pre-wrap">{analysisResult.analysis}</p>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>

        {/* Agents Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {loading ? (
            Array(5).fill(0).map((_, i) => (
              <Card key={i} className="glass-card animate-pulse">
                <CardContent className="p-6 h-[200px]" />
              </Card>
            ))
          ) : (
            agents.map((agent) => {
              const Icon = getAgentIcon(agent.type);
              const color = getAgentColor(agent.type);
              return (
                <Card key={agent.id} className="glass-card card-hover" data-testid={`agent-card-${agent.name}`}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div
                        className="w-12 h-12 rounded-xl flex items-center justify-center"
                        style={{ backgroundColor: `${color}20` }}
                      >
                        <Icon className="w-6 h-6" style={{ color }} />
                      </div>
                      <Badge
                        className={agent.status === 'active' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-zinc-700 text-zinc-400'}
                      >
                        {agent.status}
                      </Badge>
                    </div>
                    <h3 className="text-lg font-semibold mb-1">{agent.name}</h3>
                    <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{agent.description}</p>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-zinc-500">7D Performance</p>
                        <p className={`font-mono ${agent.performance_7d >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {agent.performance_7d >= 0 ? '+' : ''}{agent.performance_7d}%
                        </p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Win Rate</p>
                        <p className="font-mono">{agent.win_rate}%</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>

        {/* Recent Trades */}
        <Card className="glass-card" data-testid="recent-trades">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#00FF94]" />
              Recent Trades
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              <div className="space-y-3">
                {trades.map((trade) => (
                  <div
                    key={trade.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800"
                    data-testid={`trade-${trade.id}`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        trade.side === 'buy' ? 'bg-[#00FF94]/20' : 'bg-red-400/20'
                      }`}>
                        {trade.side === 'buy' ? (
                          <ArrowUpRight className="w-4 h-4 text-[#00FF94]" />
                        ) : (
                          <ArrowDownRight className="w-4 h-4 text-red-400" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{trade.symbol}</p>
                        <p className="text-xs text-zinc-500">{trade.agent_id}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-mono">${trade.price?.toLocaleString()}</p>
                      <p className={`text-xs ${trade.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                        {trade.pnl >= 0 ? '+' : ''}{trade.pnl?.toFixed(2)} P&L
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Marketplace Page
const MarketplacePage = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const { wallet } = useWallet();

  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    strategy: '',
    min_investment: 100
  });

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const response = await axios.get(`${API}/marketplace/agents`);
        setAgents(response.data);
      } catch (error) {
        console.error("Error fetching marketplace agents:", error);
      }
      setLoading(false);
    };
    fetchAgents();
  }, []);

  const handleSubmitAgent = async () => {
    if (!wallet) {
      toast.error("Connect wallet first");
      return;
    }
    try {
      await axios.post(`${API}/marketplace/agents`, {
        ...newAgent,
        developer_address: wallet
      });
      toast.success("Agent submitted for review!");
      setShowSubmitDialog(false);
      setNewAgent({ name: '', description: '', strategy: '', min_investment: 100 });
    } catch (error) {
      toast.error("Failed to submit agent");
    }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="marketplace-title">
              AI Agent Marketplace
            </h1>
            <p className="text-zinc-400 mt-1">Discover and deploy community-built trading strategies</p>
          </div>
          <Button
            onClick={() => setShowSubmitDialog(true)}
            className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
            data-testid="submit-agent-btn"
          >
            <Cpu className="w-4 h-4 mr-2" />
            Submit Your Agent
          </Button>
        </div>

        {/* Revenue Model Info */}
        <Card className="glass-card mb-8 border-[#7B61FF]/30" data-testid="revenue-info">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-2">Developer Revenue Model</h3>
                <p className="text-zinc-400 text-sm">
                  Deploy your AI trading agent and earn 90% of subscriber fees. Platform takes only 10%.
                </p>
              </div>
              <div className="flex gap-8">
                <div className="text-center">
                  <p className="text-3xl font-bold text-[#00FF94]">90%</p>
                  <p className="text-xs text-zinc-500">Developer Share</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-zinc-400">10%</p>
                  <p className="text-xs text-zinc-500">Platform Fee</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Agents Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            Array(3).fill(0).map((_, i) => (
              <Card key={i} className="glass-card animate-pulse">
                <CardContent className="p-6 h-[250px]" />
              </Card>
            ))
          ) : (
            agents.map((agent) => (
              <Card key={agent.id} className="glass-card card-hover" data-testid={`marketplace-agent-${agent.id}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center">
                      <Bot className="w-6 h-6 text-white" />
                    </div>
                    <Badge className="bg-[#00FF94]/20 text-[#00FF94]">
                      {agent.total_subscribers} subscribers
                    </Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{agent.name}</h3>
                  <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{agent.description}</p>
                  <div className="flex items-center justify-between text-sm mb-4">
                    <span className="text-zinc-500">30D Return</span>
                    <span className={`font-mono ${agent.performance_30d >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {agent.performance_30d >= 0 ? '+' : ''}{agent.performance_30d}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm mb-4">
                    <span className="text-zinc-500">Strategy</span>
                    <Badge variant="outline" className="border-zinc-700">{agent.strategy}</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-zinc-500">Min. Investment</span>
                    <span className="font-mono">${agent.min_investment}</span>
                  </div>
                  <Button
                    className="w-full mt-4 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] hover:bg-[#7B61FF]/30"
                    data-testid={`subscribe-${agent.id}`}
                  >
                    Subscribe
                  </Button>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Submit Agent Dialog */}
      <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <DialogContent className="bg-[#121212] border-zinc-800" data-testid="submit-agent-dialog">
          <DialogHeader>
            <DialogTitle>Submit Your AI Agent</DialogTitle>
            <DialogDescription>
              Deploy your trading strategy to the marketplace
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Agent Name</label>
              <Input
                placeholder="My Trading Bot"
                value={newAgent.name}
                onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                className="bg-[#050505] border-zinc-800"
                data-testid="agent-name-input"
              />
            </div>
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Description</label>
              <Input
                placeholder="Describe your strategy..."
                value={newAgent.description}
                onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                className="bg-[#050505] border-zinc-800"
                data-testid="agent-description-input"
              />
            </div>
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Strategy Type</label>
              <Select
                value={newAgent.strategy}
                onValueChange={(v) => setNewAgent({ ...newAgent, strategy: v })}
              >
                <SelectTrigger className="bg-[#050505] border-zinc-800" data-testid="agent-strategy-select">
                  <SelectValue placeholder="Select strategy" />
                </SelectTrigger>
                <SelectContent className="bg-[#121212] border-zinc-800">
                  <SelectItem value="Momentum Trading">Momentum Trading</SelectItem>
                  <SelectItem value="Arbitrage">Arbitrage</SelectItem>
                  <SelectItem value="Yield Farming">Yield Farming</SelectItem>
                  <SelectItem value="Mean Reversion">Mean Reversion</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Minimum Investment ($)</label>
              <Input
                type="number"
                placeholder="100"
                value={newAgent.min_investment}
                onChange={(e) => setNewAgent({ ...newAgent, min_investment: parseFloat(e.target.value) })}
                className="bg-[#050505] border-zinc-800"
                data-testid="agent-min-investment-input"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSubmitDialog(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmitAgent}
              className="bg-[#7B61FF] hover:bg-[#7B61FF]/90"
              data-testid="submit-agent-confirm-btn"
            >
              Submit for Review
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Analytics Page
const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const [overviewRes, strategiesRes] = await Promise.all([
          axios.get(`${API}/analytics/overview`),
          axios.get(`${API}/analytics/strategies`)
        ]);
        setAnalytics(overviewRes.data);
        setStrategies(strategiesRes.data);
      } catch (error) {
        console.error("Error fetching analytics:", error);
      }
      setLoading(false);
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" />
      </div>
    );
  }

  const dailyReturnsData = analytics?.daily_returns?.map((value, index) => ({
    day: index + 1,
    return: value
  })) || [];

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="analytics-title">
            Analytics & Performance
          </h1>
          <p className="text-zinc-400 mt-1">Detailed performance metrics and strategy analysis</p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card" data-testid="metric-sharpe">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Sharpe Ratio</p>
              <p className="text-3xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">
                {analytics?.sharpe_ratio}
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="metric-sortino">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Sortino Ratio</p>
              <p className="text-3xl font-bold text-[#00FF94] font-['JetBrains_Mono']">
                {analytics?.sortino_ratio}
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="metric-drawdown">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Max Drawdown</p>
              <p className="text-3xl font-bold text-red-400 font-['JetBrains_Mono']">
                -{analytics?.max_drawdown}%
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="metric-winrate">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Win Rate</p>
              <p className="text-3xl font-bold font-['JetBrains_Mono']">
                {analytics?.win_rate}%
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <Card className="glass-card" data-testid="daily-returns-chart">
            <CardHeader>
              <CardTitle>Daily Returns (30D)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dailyReturnsData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis dataKey="day" stroke="#71717A" />
                    <YAxis stroke="#71717A" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#121212',
                        border: '1px solid #27272A',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="return" fill="#7B61FF" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="strategy-performance-chart">
            <CardHeader>
              <CardTitle>Strategy Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={strategies} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis type="number" stroke="#71717A" />
                    <YAxis dataKey="name" type="category" stroke="#71717A" width={120} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#121212',
                        border: '1px solid #27272A',
                        borderRadius: '8px'
                      }}
                    />
                    <Bar dataKey="return" fill="#00FF94" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Strategies Table */}
        <Card className="glass-card" data-testid="strategies-table">
          <CardHeader>
            <CardTitle>Strategy Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-zinc-800">
                    <th className="text-left p-4 text-zinc-500 font-medium">Strategy</th>
                    <th className="text-right p-4 text-zinc-500 font-medium">Return</th>
                    <th className="text-right p-4 text-zinc-500 font-medium">Trades</th>
                    <th className="text-right p-4 text-zinc-500 font-medium">Win Rate</th>
                  </tr>
                </thead>
                <tbody>
                  {strategies.map((strategy, index) => (
                    <tr key={index} className="border-b border-zinc-800/50" data-testid={`strategy-row-${index}`}>
                      <td className="p-4 font-medium">{strategy.name}</td>
                      <td className={`p-4 text-right font-mono ${strategy.return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                        {strategy.return >= 0 ? '+' : ''}{strategy.return}%
                      </td>
                      <td className="p-4 text-right font-mono text-zinc-400">{strategy.trades}</td>
                      <td className="p-4 text-right font-mono">{strategy.win_rate}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Additional Metrics */}
        <div className="grid md:grid-cols-3 gap-4 mt-8">
          <Card className="glass-card" data-testid="total-trades">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-500">Total Trades</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">
                    {analytics?.total_trades?.toLocaleString()}
                  </p>
                </div>
                <Activity className="w-8 h-8 text-[#7B61FF]" />
              </div>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="profit-factor">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-500">Profit Factor</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#00FF94]">
                    {analytics?.profit_factor}
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-[#00FF94]" />
              </div>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="avg-duration">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-500">Avg Trade Duration</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">
                    {analytics?.avg_trade_duration}
                  </p>
                </div>
                <Clock className="w-8 h-8 text-zinc-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

// Admin Dashboard Page
const AdminPage = () => {
  const [fundStats, setFundStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [trades, setTrades] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, alertsRes, tradesRes, agentsRes] = await Promise.all([
          axios.get(`${API}/fund/stats`),
          axios.get(`${API}/risk/alerts`),
          axios.get(`${API}/trades?limit=20`),
          axios.get(`${API}/agents`)
        ]);
        setFundStats(statsRes.data);
        setAlerts(alertsRes.data);
        setTrades(tradesRes.data);
        setAgents(agentsRes.data);
      } catch (error) {
        console.error("Error fetching admin data:", error);
      }
      setLoading(false);
    };
    fetchData();
  }, []);

  const resolveAlert = async (alertId) => {
    try {
      await axios.post(`${API}/risk/alerts/${alertId}/resolve`);
      setAlerts(alerts.filter(a => a.id !== alertId));
      toast.success("Alert resolved");
    } catch (error) {
      toast.error("Failed to resolve alert");
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" />
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="admin-title">
            Admin Dashboard
          </h1>
          <p className="text-zinc-400 mt-1">Monitor fund operations and manage risk</p>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card" data-testid="admin-nav">
            <CardContent className="p-6">
              <p className="text-sm text-zinc-500 mb-1">Fund NAV</p>
              <p className="text-2xl font-bold font-['JetBrains_Mono']">
                {formatCurrency(fundStats?.nav)}
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="admin-investors">
            <CardContent className="p-6">
              <p className="text-sm text-zinc-500 mb-1">Total Investors</p>
              <p className="text-2xl font-bold font-['JetBrains_Mono']">
                {fundStats?.total_investors}
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="admin-trades-24h">
            <CardContent className="p-6">
              <p className="text-sm text-zinc-500 mb-1">24h Trades</p>
              <p className="text-2xl font-bold font-['JetBrains_Mono']">
                {fundStats?.total_trades_24h}
              </p>
            </CardContent>
          </Card>
          <Card className="glass-card" data-testid="admin-drawdown">
            <CardContent className="p-6">
              <p className="text-sm text-zinc-500 mb-1">Max Drawdown</p>
              <p className="text-2xl font-bold text-red-400 font-['JetBrains_Mono']">
                -{fundStats?.max_drawdown}%
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Risk Alerts */}
          <Card className="glass-card" data-testid="risk-alerts-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="w-5 h-5 text-[#FFB800]" />
                Risk Alerts
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                <div className="space-y-3">
                  {alerts.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No active alerts</p>
                  ) : (
                    alerts.map((alert) => (
                      <div
                        key={alert.id}
                        className={`p-4 rounded-lg border ${
                          alert.severity === 'high'
                            ? 'bg-red-500/10 border-red-500/30'
                            : alert.severity === 'medium'
                            ? 'bg-[#FFB800]/10 border-[#FFB800]/30'
                            : 'bg-zinc-800/50 border-zinc-700'
                        }`}
                        data-testid={`alert-${alert.id}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge className={
                                alert.severity === 'high'
                                  ? 'bg-red-500/20 text-red-400'
                                  : alert.severity === 'medium'
                                  ? 'bg-[#FFB800]/20 text-[#FFB800]'
                                  : 'bg-zinc-700 text-zinc-400'
                              }>
                                {alert.severity}
                              </Badge>
                              <span className="text-xs text-zinc-500">{alert.type}</span>
                            </div>
                            <p className="text-sm">{alert.message}</p>
                          </div>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => resolveAlert(alert.id)}
                            className="text-zinc-400 hover:text-white"
                            data-testid={`resolve-alert-${alert.id}`}
                          >
                            <Check className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Agent Status */}
          <Card className="glass-card" data-testid="agent-status-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5 text-[#7B61FF]" />
                Agent Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                <div className="space-y-3">
                  {agents.map((agent) => (
                    <div
                      key={agent.id}
                      className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800"
                      data-testid={`admin-agent-${agent.id}`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${
                          agent.status === 'active' ? 'bg-[#00FF94]' : 'bg-zinc-500'
                        }`} />
                        <div>
                          <p className="font-medium text-sm">{agent.name}</p>
                          <p className="text-xs text-zinc-500">{agent.type}</p>
                        </div>
                      </div>
                      <Badge className={
                        agent.status === 'active'
                          ? 'bg-[#00FF94]/20 text-[#00FF94]'
                          : 'bg-zinc-700 text-zinc-400'
                      }>
                        {agent.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Trade Logs */}
        <Card className="glass-card" data-testid="trade-logs-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#00FF94]" />
              Trade Logs
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-zinc-800">
                    <th className="text-left p-3 text-zinc-500 font-medium">Time</th>
                    <th className="text-left p-3 text-zinc-500 font-medium">Agent</th>
                    <th className="text-left p-3 text-zinc-500 font-medium">Symbol</th>
                    <th className="text-left p-3 text-zinc-500 font-medium">Side</th>
                    <th className="text-right p-3 text-zinc-500 font-medium">Price</th>
                    <th className="text-right p-3 text-zinc-500 font-medium">P&L</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.slice(0, 10).map((trade) => (
                    <tr key={trade.id} className="border-b border-zinc-800/50" data-testid={`trade-log-${trade.id}`}>
                      <td className="p-3 text-sm text-zinc-400">
                        {new Date(trade.timestamp).toLocaleTimeString()}
                      </td>
                      <td className="p-3 text-sm">{trade.agent_id}</td>
                      <td className="p-3 font-mono text-sm">{trade.symbol}</td>
                      <td className="p-3">
                        <Badge className={
                          trade.side === 'buy'
                            ? 'bg-[#00FF94]/20 text-[#00FF94]'
                            : 'bg-red-400/20 text-red-400'
                        }>
                          {trade.side}
                        </Badge>
                      </td>
                      <td className="p-3 text-right font-mono text-sm">${trade.price?.toLocaleString()}</td>
                      <td className={`p-3 text-right font-mono text-sm ${trade.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                        {trade.pnl >= 0 ? '+' : ''}{trade.pnl?.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Main App
function App() {
  return (
    <WalletProvider>
      <div className="App min-h-screen bg-[#050505]">
        <BrowserRouter>
          <Navigation />
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/marketplace" element={<MarketplacePage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="bottom-right" theme="dark" />
      </div>
    </WalletProvider>
  );
}

export default App;
