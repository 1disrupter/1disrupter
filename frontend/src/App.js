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
  RefreshCw, ExternalLink, Copy, Sparkles, FlaskConical, Play,
  Pause, TestTube, Rocket, StopCircle, Gauge, Scale, Split,
  Beaker, Trophy, FileCode, Radio, CircleDot, Terminal, ScrollText
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
import { Switch } from "./components/ui/switch";
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

const WalletContext = createContext();
const useWallet = () => useContext(WalletContext);

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
        toast.success("Wallet connected!");
      } else {
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

const formatCurrency = (value) => {
  if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(2)}K`;
  return `$${value?.toFixed(2) || '0.00'}`;
};

const formatAddress = (address) => {
  if (!address) return '';
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
};

// Navigation
const Navigation = () => {
  const { wallet, connectWallet, disconnectWallet, loading } = useWallet();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: "/", label: "Home", icon: Home },
    { path: "/dashboard", label: "Dashboard", icon: BarChart3 },
    { path: "/simulation", label: "Simulation", icon: Radio },
    { path: "/agents", label: "AI Agents", icon: Bot },
    { path: "/lab", label: "Strategy Lab", icon: FlaskConical },
    { path: "/marketplace", label: "Marketplace", icon: Store },
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
            {wallet ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="rounded-full border-[#7B61FF]/30 hover:border-[#7B61FF] bg-[#7B61FF]/10" data-testid="wallet-dropdown">
                    <Wallet className="w-4 h-4 mr-2 text-[#7B61FF]" />
                    {formatAddress(wallet)}
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="bg-[#121212] border-zinc-800">
                  <DropdownMenuItem onClick={() => navigator.clipboard.writeText(wallet)}>
                    <Copy className="w-4 h-4 mr-2" />Copy Address
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={disconnectWallet} className="text-red-400">
                    <X className="w-4 h-4 mr-2" />Disconnect
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button onClick={connectWallet} disabled={loading} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 glow-primary" data-testid="connect-wallet-btn">
                <Wallet className="w-4 h-4 mr-2" />
                {loading ? "Connecting..." : "Connect Wallet"}
              </Button>
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
    axios.get(`${API}/fund/stats`).then(res => setFundStats(res.data)).catch(console.error);
  }, []);

  return (
    <div className="min-h-screen pt-20">
      <section className="relative px-4 py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0 grid-pattern opacity-50" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#7B61FF]/20 rounded-full blur-[120px]" />
        
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="text-center max-w-4xl mx-auto">
            <Badge className="mb-6 bg-[#7B61FF]/20 text-[#7B61FF] border-[#7B61FF]/30" data-testid="hero-badge">
              <Sparkles className="w-3 h-3 mr-1" />AI-Powered Hedge Fund
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 font-['Outfit'] tracking-tight" data-testid="hero-title">
              <span className="text-gradient">Autonomous Trading</span><br />
              <span className="text-gradient-primary">Powered by AI</span>
            </h1>
            
            <p className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl mx-auto" data-testid="hero-description">
              Deploy capital into our AI-managed vault. Multi-agent trading system analyzes markets 24/7, executing optimal strategies across DeFi.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {wallet ? (
                <Link to="/dashboard">
                  <Button size="lg" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary btn-hover-lift" data-testid="go-to-dashboard-btn">
                    Go to Dashboard<ArrowUpRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
              ) : (
                <Button size="lg" onClick={connectWallet} disabled={loading} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary btn-hover-lift" data-testid="hero-connect-wallet-btn">
                  <Wallet className="w-5 h-5 mr-2" />{loading ? "Connecting..." : "Connect Wallet"}
                </Button>
              )}
              <Link to="/lab">
                <Button size="lg" variant="outline" className="rounded-full border-zinc-700 hover:border-zinc-600 px-8 btn-hover-lift" data-testid="explore-lab-btn">
                  <FlaskConical className="w-5 h-5 mr-2" />Strategy Lab
                </Button>
              </Link>
            </div>
          </motion.div>

          {fundStats && (
            <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.3 }} className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-20">
              <Card className="glass-card card-hover" data-testid="stat-nav">
                <CardContent className="p-6 text-center">
                  <p className="text-sm text-zinc-500 mb-2">Fund NAV</p>
                  <p className="text-2xl md:text-3xl font-bold text-white font-['JetBrains_Mono']">{formatCurrency(fundStats.nav)}</p>
                  <p className={`text-sm mt-1 flex items-center justify-center gap-1 ${fundStats.nav_change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                    {fundStats.nav_change_24h >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}{fundStats.nav_change_24h}%
                  </p>
                </CardContent>
              </Card>
              <Card className="glass-card card-hover" data-testid="stat-aum"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Total AUM</p><p className="text-2xl md:text-3xl font-bold text-white font-['JetBrains_Mono']">{formatCurrency(fundStats.total_aum)}</p></CardContent></Card>
              <Card className="glass-card card-hover" data-testid="stat-sharpe"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Sharpe Ratio</p><p className="text-2xl md:text-3xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">{fundStats.sharpe_ratio}</p></CardContent></Card>
              <Card className="glass-card card-hover" data-testid="stat-return"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Monthly Return</p><p className={`text-2xl md:text-3xl font-bold font-['JetBrains_Mono'] ${fundStats.monthly_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{fundStats.monthly_return >= 0 ? '+' : ''}{fundStats.monthly_return}%</p></CardContent></Card>
            </motion.div>
          )}
        </div>
      </section>

      <section className="px-4 py-20 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold font-['Outfit'] mb-4" data-testid="features-title">Self-Improving AI System</h2>
            <p className="text-zinc-400 max-w-2xl mx-auto">Our Strategy Lab continuously generates, tests, and deploys new trading strategies</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Brain, title: "Strategy Generator", description: "AI creates new trading strategies autonomously", color: "#7B61FF" },
              { icon: TestTube, title: "Backtesting Engine", description: "Tests strategies on historical data", color: "#00FF94" },
              { icon: Beaker, title: "Sandbox Validation", description: "Paper trading before live deployment", color: "#FFB800" },
              { icon: Trophy, title: "Performance Ranking", description: "Strategies ranked by Sharpe ratio & returns", color: "#FF6B6B" },
              { icon: Rocket, title: "Auto Deployment", description: "Top strategies automatically go live", color: "#00D4FF" },
              { icon: Shield, title: "Risk Management", description: "Real-time drawdown protection", color: "#FF61DC" }
            ].map((feature, index) => (
              <motion.div key={feature.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }} viewport={{ once: true }}>
                <Card className="glass-card card-hover h-full" data-testid={`feature-${feature.title.toLowerCase().replace(' ', '-')}`}>
                  <CardContent className="p-6">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center mb-4" style={{ backgroundColor: `${feature.color}20` }}>
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

      <footer className="px-4 py-8 border-t border-zinc-800">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2"><Brain className="w-5 h-5 text-[#7B61FF]" /><span className="font-semibold">AlphaAI Platform</span></div>
          <p className="text-sm text-zinc-500">© 2026 Martin Maughan. All rights reserved. AlphaAI Platform.</p>
        </div>
      </footer>
    </div>
  );
};

// Dashboard Page with Paper Trading
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
  const [isPaperTrading, setIsPaperTrading] = useState(false);
  const [paperPortfolio, setPaperPortfolio] = useState(null);
  const [paperSymbol, setPaperSymbol] = useState('BTC/USDT');
  const [paperAmount, setPaperAmount] = useState('');
  const [paperSide, setPaperSide] = useState('buy');

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/fund/stats`),
      axios.get(`${API}/fund/allocation`),
      axios.get(`${API}/fund/performance-history`)
    ]).then(([statsRes, allocRes, perfRes]) => {
      setFundStats(statsRes.data);
      setAllocation(allocRes.data);
      setPerformanceHistory(perfRes.data);
    }).catch(console.error);
  }, []);

  useEffect(() => {
    if (wallet && isPaperTrading) {
      axios.get(`${API}/paper/portfolio/${wallet}`).then(res => setPaperPortfolio(res.data)).catch(console.error);
    }
  }, [wallet, isPaperTrading]);

  const handleDeposit = async () => {
    if (!wallet || !depositAmount || parseFloat(depositAmount) < 100) { toast.error("Minimum deposit is $100"); return; }
    setDepositLoading(true);
    try {
      const response = await axios.post(`${API}/investors/deposit`, { wallet_address: wallet, amount: parseFloat(depositAmount) });
      toast.success(response.data.message);
      setDepositAmount(''); setShowDepositDialog(false); refreshInvestor();
    } catch (error) { toast.error(error.response?.data?.detail || "Deposit failed"); }
    setDepositLoading(false);
  };

  const handleWithdraw = async () => {
    if (!wallet || !withdrawAmount || parseFloat(withdrawAmount) <= 0) { toast.error("Enter a valid amount"); return; }
    setWithdrawLoading(true);
    try {
      const response = await axios.post(`${API}/investors/withdraw`, { wallet_address: wallet, amount: parseFloat(withdrawAmount) });
      toast.success(response.data.message);
      setWithdrawAmount(''); setShowWithdrawDialog(false); refreshInvestor();
    } catch (error) { toast.error(error.response?.data?.detail || "Withdrawal failed"); }
    setWithdrawLoading(false);
  };

  const executePaperTrade = async () => {
    if (!paperAmount || parseFloat(paperAmount) <= 0) { toast.error("Enter valid amount"); return; }
    try {
      const res = await axios.post(`${API}/paper/trade`, { wallet_address: wallet, symbol: paperSymbol, side: paperSide, amount: parseFloat(paperAmount) });
      toast.success(`Paper trade executed! PnL: $${res.data.pnl}`);
      setPaperPortfolio(prev => ({ ...prev, paper_balance: res.data.new_paper_balance }));
      setPaperAmount('');
    } catch (error) { toast.error(error.response?.data?.detail || "Trade failed"); }
  };

  const resetPaperPortfolio = async () => {
    try {
      await axios.post(`${API}/paper/reset/${wallet}`);
      toast.success("Paper portfolio reset to $10,000");
      setPaperPortfolio({ paper_balance: 10000, paper_pnl: 0, total_trades: 0 });
    } catch (error) { toast.error("Reset failed"); }
  };

  if (!wallet) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <Card className="glass-card max-w-md w-full" data-testid="connect-wallet-prompt">
          <CardContent className="p-8 text-center">
            <Wallet className="w-16 h-16 mx-auto mb-4 text-[#7B61FF]" />
            <h2 className="text-2xl font-bold mb-2">Connect Your Wallet</h2>
            <p className="text-zinc-400 mb-6">Connect to view your dashboard</p>
            <WalletConnectButton />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="dashboard-title">Investor Dashboard</h1>
            <p className="text-zinc-400 mt-1">Welcome back, {formatAddress(wallet)}</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-[#050505] border border-zinc-800">
              <span className="text-sm text-zinc-400">Paper Trading</span>
              <Switch checked={isPaperTrading} onCheckedChange={setIsPaperTrading} data-testid="paper-trading-toggle" />
            </div>
            <Button onClick={() => setShowDepositDialog(true)} className="rounded-full bg-[#00FF94] text-black hover:bg-[#00FF94]/90" data-testid="deposit-btn">
              <ArrowUpRight className="w-4 h-4 mr-2" />Deposit
            </Button>
            <Button onClick={() => setShowWithdrawDialog(true)} variant="outline" className="rounded-full border-zinc-700" data-testid="withdraw-btn">
              <ArrowDownRight className="w-4 h-4 mr-2" />Withdraw
            </Button>
          </div>
        </div>

        {isPaperTrading && paperPortfolio && (
          <Card className="glass-card mb-8 border-[#FFB800]/30" data-testid="paper-trading-panel">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Beaker className="w-5 h-5 text-[#FFB800]" />Paper Trading Sandbox</CardTitle>
              <CardDescription>Practice trading with virtual funds - no real money at risk</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800">
                  <p className="text-sm text-zinc-500">Paper Balance</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">{formatCurrency(paperPortfolio.paper_balance)}</p>
                </div>
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800">
                  <p className="text-sm text-zinc-500">Total P&L</p>
                  <p className={`text-2xl font-bold font-['JetBrains_Mono'] ${paperPortfolio.paper_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                    {paperPortfolio.paper_pnl >= 0 ? '+' : ''}${paperPortfolio.paper_pnl?.toFixed(2)}
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800">
                  <p className="text-sm text-zinc-500">Return</p>
                  <p className={`text-2xl font-bold font-['JetBrains_Mono'] ${paperPortfolio.return_percent >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                    {paperPortfolio.return_percent >= 0 ? '+' : ''}{paperPortfolio.return_percent}%
                  </p>
                </div>
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800">
                  <p className="text-sm text-zinc-500">Total Trades</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">{paperPortfolio.total_trades}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-3 items-end">
                <Select value={paperSymbol} onValueChange={setPaperSymbol}>
                  <SelectTrigger className="w-[140px] bg-[#050505] border-zinc-800" data-testid="paper-symbol-select"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-[#121212] border-zinc-800">
                    <SelectItem value="BTC/USDT">BTC/USDT</SelectItem>
                    <SelectItem value="ETH/USDT">ETH/USDT</SelectItem>
                    <SelectItem value="SOL/USDT">SOL/USDT</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={paperSide} onValueChange={setPaperSide}>
                  <SelectTrigger className="w-[100px] bg-[#050505] border-zinc-800" data-testid="paper-side-select"><SelectValue /></SelectTrigger>
                  <SelectContent className="bg-[#121212] border-zinc-800">
                    <SelectItem value="buy">Buy</SelectItem>
                    <SelectItem value="sell">Sell</SelectItem>
                  </SelectContent>
                </Select>
                <Input type="number" placeholder="Amount" value={paperAmount} onChange={e => setPaperAmount(e.target.value)} className="w-[120px] bg-[#050505] border-zinc-800" data-testid="paper-amount-input" />
                <Button onClick={executePaperTrade} className={`rounded-full ${paperSide === 'buy' ? 'bg-[#00FF94] text-black' : 'bg-red-500'}`} data-testid="paper-trade-btn">
                  {paperSide === 'buy' ? 'Buy' : 'Sell'}
                </Button>
                <Button onClick={resetPaperPortfolio} variant="outline" className="rounded-full border-zinc-700" data-testid="paper-reset-btn">Reset</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card" data-testid="investor-balance"><CardContent className="p-6"><div className="flex items-center justify-between mb-2"><span className="text-sm text-zinc-500">Your Balance</span><DollarSign className="w-4 h-4 text-[#00FF94]" /></div><p className="text-2xl font-bold font-['JetBrains_Mono']">{formatCurrency(investor?.balance || 0)}</p></CardContent></Card>
          <Card className="glass-card" data-testid="investor-shares"><CardContent className="p-6"><div className="flex items-center justify-between mb-2"><span className="text-sm text-zinc-500">Your Shares</span><PieChart className="w-4 h-4 text-[#7B61FF]" /></div><p className="text-2xl font-bold font-['JetBrains_Mono']">{investor?.shares?.toFixed(4) || '0.0000'}</p></CardContent></Card>
          <Card className="glass-card" data-testid="fund-nav-card"><CardContent className="p-6"><div className="flex items-center justify-between mb-2"><span className="text-sm text-zinc-500">Fund NAV</span><TrendingUp className="w-4 h-4 text-[#00FF94]" /></div><p className="text-2xl font-bold font-['JetBrains_Mono']">{formatCurrency(fundStats?.nav || 0)}</p><p className={`text-xs mt-1 ${fundStats?.nav_change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{fundStats?.nav_change_24h >= 0 ? '+' : ''}{fundStats?.nav_change_24h}% (24h)</p></CardContent></Card>
          <Card className="glass-card" data-testid="monthly-return-card"><CardContent className="p-6"><div className="flex items-center justify-between mb-2"><span className="text-sm text-zinc-500">Monthly Return</span><Percent className="w-4 h-4 text-[#FFB800]" /></div><p className={`text-2xl font-bold font-['JetBrains_Mono'] ${fundStats?.monthly_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{fundStats?.monthly_return >= 0 ? '+' : ''}{fundStats?.monthly_return}%</p></CardContent></Card>
        </div>

        <div className="grid lg:grid-cols-3 gap-6 mb-8">
          <Card className="glass-card lg:col-span-2" data-testid="performance-chart">
            <CardHeader><CardTitle className="flex items-center gap-2"><LineChart className="w-5 h-5 text-[#7B61FF]" />Performance History</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={performanceHistory}>
                    <defs><linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#7B61FF" stopOpacity={0.3}/><stop offset="95%" stopColor="#7B61FF" stopOpacity={0}/></linearGradient></defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis dataKey="date" stroke="#71717A" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#71717A" tick={{ fontSize: 11 }} />
                    <Tooltip contentStyle={{ backgroundColor: '#121212', border: '1px solid #7B61FF', borderRadius: '8px' }} />
                    <Area type="monotone" dataKey="value" stroke="#7B61FF" fillOpacity={1} fill="url(#colorValue)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="allocation-chart">
            <CardHeader><CardTitle className="flex items-center gap-2"><PieChart className="w-5 h-5 text-[#00FF94]" />Portfolio Allocation</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart><Pie data={allocation} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label={({ value }) => `${value}%`} labelLine={false}>{allocation.map((entry, index) => (<Cell key={`cell-${index}`} fill={entry.color} />))}</Pie><Tooltip contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '8px' }} /></RePieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2 mt-4">{allocation.map((item, index) => (<div key={index} className="flex items-center justify-between text-sm"><div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} /><span className="text-zinc-400">{item.name}</span></div><span className="font-mono">{item.value}%</span></div>))}</div>
            </CardContent>
          </Card>
        </div>
      </div>

      <Dialog open={showDepositDialog} onOpenChange={setShowDepositDialog}>
        <DialogContent className="bg-[#121212] border-zinc-800" data-testid="deposit-dialog">
          <DialogHeader><DialogTitle>Deposit Funds</DialogTitle><DialogDescription>Minimum: $100</DialogDescription></DialogHeader>
          <div className="py-4"><Input type="number" placeholder="Amount in USD" value={depositAmount} onChange={(e) => setDepositAmount(e.target.value)} className="bg-[#050505] border-zinc-800" data-testid="deposit-amount-input" /></div>
          <DialogFooter><Button variant="outline" onClick={() => setShowDepositDialog(false)}>Cancel</Button><Button onClick={handleDeposit} disabled={depositLoading} className="bg-[#00FF94] text-black hover:bg-[#00FF94]/90" data-testid="confirm-deposit-btn">{depositLoading ? "Processing..." : "Confirm"}</Button></DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={showWithdrawDialog} onOpenChange={setShowWithdrawDialog}>
        <DialogContent className="bg-[#121212] border-zinc-800" data-testid="withdraw-dialog">
          <DialogHeader><DialogTitle>Withdraw Funds</DialogTitle><DialogDescription>Available: {formatCurrency(investor?.balance || 0)}</DialogDescription></DialogHeader>
          <div className="py-4"><Input type="number" placeholder="Amount in USD" value={withdrawAmount} onChange={(e) => setWithdrawAmount(e.target.value)} className="bg-[#050505] border-zinc-800" data-testid="withdraw-amount-input" /></div>
          <DialogFooter><Button variant="outline" onClick={() => setShowWithdrawDialog(false)}>Cancel</Button><Button onClick={handleWithdraw} disabled={withdrawLoading} className="bg-red-500 hover:bg-red-600" data-testid="confirm-withdraw-btn">{withdrawLoading ? "Processing..." : "Confirm"}</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const WalletConnectButton = () => {
  const { connectWallet, loading } = useWallet();
  return (<Button onClick={connectWallet} disabled={loading} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary" data-testid="wallet-connect-btn"><Wallet className="w-5 h-5 mr-2" />{loading ? "Connecting..." : "Connect Wallet"}</Button>);
};

// Strategy Lab Page
const StrategyLabPage = () => {
  const [strategies, setStrategies] = useState([]);
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generateType, setGenerateType] = useState('momentum');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/lab/strategies`),
      axios.get(`${API}/lab/rankings`)
    ]).then(([strategiesRes, rankingsRes]) => {
      setStrategies(strategiesRes.data);
      setRankings(rankingsRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const generateStrategy = async () => {
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/lab/strategies/generate`, { strategy_type: generateType, risk_level: 'medium' });
      toast.success(`Strategy "${res.data.strategy.name}" generated!`);
      setStrategies([res.data.strategy, ...strategies]);
    } catch (error) { toast.error("Generation failed"); }
    setGenerating(false);
  };

  const backtestStrategy = async (strategyId) => {
    try {
      const res = await axios.post(`${API}/lab/strategies/${strategyId}/backtest`, { strategy_id: strategyId, initial_capital: 10000 });
      toast.success(`Backtest complete! Return: ${res.data.results.total_return}%`);
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'backtested', ...res.data.results } : s));
    } catch (error) { toast.error("Backtest failed"); }
  };

  const startSandbox = async (strategyId) => {
    try {
      await axios.post(`${API}/lab/strategies/${strategyId}/sandbox`);
      toast.success("Sandbox testing started!");
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'sandbox' } : s));
    } catch (error) { toast.error("Sandbox start failed"); }
  };

  const deployStrategy = async (strategyId) => {
    try {
      await axios.post(`${API}/lab/strategies/${strategyId}/deploy`, null, { params: { capital: 10000 } });
      toast.success("Strategy deployed live!");
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'live', is_active: true } : s));
    } catch (error) { toast.error(error.response?.data?.detail || "Deployment failed"); }
  };

  const stopStrategy = async (strategyId) => {
    try {
      await axios.post(`${API}/lab/strategies/${strategyId}/stop`);
      toast.success("Strategy stopped");
      setStrategies(strategies.map(s => s.id === strategyId ? { ...s, status: 'stopped', is_active: false } : s));
    } catch (error) { toast.error("Stop failed"); }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'live': return 'bg-[#00FF94]/20 text-[#00FF94]';
      case 'sandbox': return 'bg-[#FFB800]/20 text-[#FFB800]';
      case 'backtested': return 'bg-[#7B61FF]/20 text-[#7B61FF]';
      case 'generated': return 'bg-zinc-700 text-zinc-400';
      default: return 'bg-zinc-700 text-zinc-400';
    }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="lab-title">AI Strategy Lab</h1>
            <p className="text-zinc-400 mt-1">Autonomous strategy generation, testing, and deployment</p>
          </div>
          <div className="flex gap-3">
            <Select value={generateType} onValueChange={setGenerateType}>
              <SelectTrigger className="w-[160px] bg-[#050505] border-zinc-800" data-testid="generate-type-select"><SelectValue /></SelectTrigger>
              <SelectContent className="bg-[#121212] border-zinc-800">
                <SelectItem value="momentum">Momentum</SelectItem>
                <SelectItem value="arbitrage">Arbitrage</SelectItem>
                <SelectItem value="yield">DeFi Yield</SelectItem>
                <SelectItem value="mean_reversion">Mean Reversion</SelectItem>
                <SelectItem value="funding">Funding Rate</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={generateStrategy} disabled={generating} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="generate-strategy-btn">
              {generating ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}
              Generate Strategy
            </Button>
          </div>
        </div>

        {/* Strategy Pipeline */}
        <Card className="glass-card mb-8" data-testid="strategy-pipeline">
          <CardHeader><CardTitle>Strategy Pipeline</CardTitle><CardDescription>Strategies progress through: Generated → Backtested → Sandbox → Live</CardDescription></CardHeader>
          <CardContent>
            <div className="grid grid-cols-4 gap-4 text-center">
              {['generated', 'backtested', 'sandbox', 'live'].map((stage, i) => {
                const count = strategies.filter(s => s.status === stage).length;
                return (
                  <div key={stage} className="p-4 rounded-xl bg-[#050505] border border-zinc-800">
                    <p className="text-2xl font-bold font-['JetBrains_Mono']">{count}</p>
                    <p className="text-sm text-zinc-500 capitalize">{stage}</p>
                    {i < 3 && <ArrowUpRight className="w-4 h-4 mx-auto mt-2 text-zinc-600" />}
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Rankings Table */}
        <Card className="glass-card mb-8" data-testid="strategy-rankings">
          <CardHeader><CardTitle className="flex items-center gap-2"><Trophy className="w-5 h-5 text-[#FFB800]" />Strategy Rankings</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-zinc-800">
                    <th className="text-left p-3 text-zinc-500">Rank</th>
                    <th className="text-left p-3 text-zinc-500">Strategy</th>
                    <th className="text-left p-3 text-zinc-500">Type</th>
                    <th className="text-left p-3 text-zinc-500">Status</th>
                    <th className="text-right p-3 text-zinc-500">Sharpe</th>
                    <th className="text-right p-3 text-zinc-500">Return</th>
                    <th className="text-right p-3 text-zinc-500">Drawdown</th>
                    <th className="text-right p-3 text-zinc-500">Capital</th>
                  </tr>
                </thead>
                <tbody>
                  {rankings.slice(0, 10).map((s, i) => (
                    <tr key={s.id} className="border-b border-zinc-800/50" data-testid={`ranking-row-${i}`}>
                      <td className="p-3"><Badge variant="outline" className={i < 3 ? 'border-[#FFB800] text-[#FFB800]' : 'border-zinc-700'}>#{s.rank}</Badge></td>
                      <td className="p-3 font-medium">{s.name}</td>
                      <td className="p-3 text-zinc-400 capitalize">{s.type}</td>
                      <td className="p-3"><Badge className={getStatusColor(s.status)}>{s.status}</Badge></td>
                      <td className="p-3 text-right font-mono text-[#7B61FF]">{s.sharpe_ratio?.toFixed(2)}</td>
                      <td className={`p-3 text-right font-mono ${s.total_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{s.total_return >= 0 ? '+' : ''}{s.total_return}%</td>
                      <td className="p-3 text-right font-mono text-red-400">-{s.max_drawdown}%</td>
                      <td className="p-3 text-right font-mono">{formatCurrency(s.capital_allocated)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Strategy Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? Array(6).fill(0).map((_, i) => (<Card key={i} className="glass-card animate-pulse"><CardContent className="p-6 h-[250px]" /></Card>)) : (
            strategies.map((strategy) => (
              <Card key={strategy.id} className="glass-card card-hover" data-testid={`strategy-card-${strategy.id}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-10 h-10 rounded-xl bg-[#7B61FF]/20 flex items-center justify-center">
                      <FileCode className="w-5 h-5 text-[#7B61FF]" />
                    </div>
                    <Badge className={getStatusColor(strategy.status)}>{strategy.status}</Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-1">{strategy.name}</h3>
                  <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{strategy.description}</p>
                  
                  <div className="grid grid-cols-2 gap-3 text-sm mb-4">
                    <div><p className="text-zinc-500">Sharpe</p><p className="font-mono text-[#7B61FF]">{strategy.sharpe_ratio?.toFixed(2) || '—'}</p></div>
                    <div><p className="text-zinc-500">Return</p><p className={`font-mono ${strategy.total_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{strategy.total_return ? `${strategy.total_return >= 0 ? '+' : ''}${strategy.total_return}%` : '—'}</p></div>
                  </div>

                  <div className="flex gap-2">
                    {strategy.status === 'generated' && (
                      <Button size="sm" onClick={() => backtestStrategy(strategy.id)} className="flex-1 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] hover:bg-[#7B61FF]/30" data-testid={`backtest-${strategy.id}`}>
                        <TestTube className="w-3 h-3 mr-1" />Backtest
                      </Button>
                    )}
                    {strategy.status === 'backtested' && (
                      <Button size="sm" onClick={() => startSandbox(strategy.id)} className="flex-1 rounded-full bg-[#FFB800]/20 text-[#FFB800] hover:bg-[#FFB800]/30" data-testid={`sandbox-${strategy.id}`}>
                        <Beaker className="w-3 h-3 mr-1" />Sandbox
                      </Button>
                    )}
                    {strategy.status === 'sandbox' && (
                      <Button size="sm" onClick={() => deployStrategy(strategy.id)} className="flex-1 rounded-full bg-[#00FF94]/20 text-[#00FF94] hover:bg-[#00FF94]/30" data-testid={`deploy-${strategy.id}`}>
                        <Rocket className="w-3 h-3 mr-1" />Deploy
                      </Button>
                    )}
                    {strategy.status === 'live' && (
                      <Button size="sm" onClick={() => stopStrategy(strategy.id)} variant="outline" className="flex-1 rounded-full border-red-500/30 text-red-400 hover:bg-red-500/10" data-testid={`stop-${strategy.id}`}>
                        <StopCircle className="w-3 h-3 mr-1" />Stop
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// AI Agents Page
const AgentsPage = () => {
  const [agents, setAgents] = useState([]);
  const [trades, setTrades] = useState([]);
  const [riskStatus, setRiskStatus] = useState(null);
  const [executionStats, setExecutionStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState('bitcoin');

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/agents`),
      axios.get(`${API}/trades?limit=10`),
      axios.get(`${API}/risk/portfolio-status`),
      axios.get(`${API}/execution/stats`)
    ]).then(([agentsRes, tradesRes, riskRes, execRes]) => {
      setAgents(agentsRes.data);
      setTrades(tradesRes.data);
      setRiskStatus(riskRes.data);
      setExecutionStats(execRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const runAIAnalysis = async () => {
    setAnalysisLoading(true);
    try {
      const response = await axios.post(`${API}/ai/analyze`, { symbol: selectedSymbol, timeframe: "1d" });
      setAnalysisResult(response.data);
      toast.success("AI Analysis complete!");
    } catch (error) { toast.error("Analysis failed"); }
    setAnalysisLoading(false);
  };

  const getAgentIcon = (type) => ({ data: Activity, analysis: Brain, strategy: Target, execution: Zap, risk: Shield }[type] || Bot);
  const getAgentColor = (type) => ({ data: '#00FF94', analysis: '#7B61FF', strategy: '#FF6B6B', execution: '#FFB800', risk: '#00D4FF' }[type] || '#7B61FF');

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="agents-title">AI Trading Agents</h1>
          <p className="text-zinc-400 mt-1">Monitor and manage autonomous trading agents</p>
        </div>

        {/* Risk & Execution Stats */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {riskStatus && (
            <Card className="glass-card" data-testid="risk-status-card">
              <CardHeader><CardTitle className="flex items-center gap-2"><Shield className="w-5 h-5 text-[#00D4FF]" />Risk Status</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1"><span className="text-zinc-400">Drawdown</span><span className={riskStatus.current_drawdown > 4 ? 'text-red-400' : 'text-[#00FF94]'}>{riskStatus.current_drawdown}% / {riskStatus.max_drawdown_limit}%</span></div>
                    <Progress value={riskStatus.drawdown_utilization} className="h-2" />
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div><p className="text-sm text-zinc-500">Daily P&L</p><p className={`font-mono ${riskStatus.daily_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{riskStatus.daily_pnl >= 0 ? '+' : ''}{riskStatus.daily_pnl}%</p></div>
                    <div><p className="text-sm text-zinc-500">Risk Level</p><Badge className={riskStatus.risk_level === 'high' ? 'bg-red-500/20 text-red-400' : riskStatus.risk_level === 'medium' ? 'bg-[#FFB800]/20 text-[#FFB800]' : 'bg-[#00FF94]/20 text-[#00FF94]'}>{riskStatus.risk_level}</Badge></div>
                    <div><p className="text-sm text-zinc-500">Stop Losses</p><p className="font-mono">{riskStatus.active_stop_losses}</p></div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {executionStats && (
            <Card className="glass-card" data-testid="execution-stats-card">
              <CardHeader><CardTitle className="flex items-center gap-2"><Split className="w-5 h-5 text-[#FFB800]" />Execution Optimization</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div><p className="text-sm text-zinc-500">Orders Today</p><p className="text-xl font-bold font-mono">{executionStats.total_orders_today}</p></div>
                  <div><p className="text-sm text-zinc-500">Avg Slippage</p><p className="text-xl font-bold font-mono text-[#00FF94]">{executionStats.avg_slippage}%</p></div>
                  <div><p className="text-sm text-zinc-500">Avg Gas Fee</p><p className="text-xl font-bold font-mono">${executionStats.avg_gas_fee}</p></div>
                  <div><p className="text-sm text-zinc-500">Best Price Rate</p><p className="text-xl font-bold font-mono text-[#7B61FF]">{executionStats.best_price_achieved}%</p></div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* AI Analysis */}
        <Card className="glass-card mb-8" data-testid="ai-analysis-section">
          <CardHeader><CardTitle className="flex items-center gap-2"><Sparkles className="w-5 h-5 text-[#7B61FF]" />AI Market Analysis</CardTitle></CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-4">
              <Select value={selectedSymbol} onValueChange={setSelectedSymbol}>
                <SelectTrigger className="w-full md:w-[200px] bg-[#050505] border-zinc-800" data-testid="analysis-symbol-select"><SelectValue placeholder="Select coin" /></SelectTrigger>
                <SelectContent className="bg-[#121212] border-zinc-800">
                  <SelectItem value="bitcoin">Bitcoin (BTC)</SelectItem>
                  <SelectItem value="ethereum">Ethereum (ETH)</SelectItem>
                  <SelectItem value="solana">Solana (SOL)</SelectItem>
                </SelectContent>
              </Select>
              <Button onClick={runAIAnalysis} disabled={analysisLoading} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="run-analysis-btn">
                {analysisLoading ? <><RefreshCw className="w-4 h-4 mr-2 animate-spin" />Analyzing...</> : <><Brain className="w-4 h-4 mr-2" />Run Analysis</>}
              </Button>
            </div>
            {analysisResult && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-6 p-4 rounded-xl bg-[#050505] border border-zinc-800" data-testid="analysis-result">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <Badge className="bg-[#7B61FF]/20 text-[#7B61FF]">{analysisResult.symbol}</Badge>
                    <span className="font-mono text-lg">${analysisResult.price?.toLocaleString()}</span>
                    <span className={`text-sm ${analysisResult.change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{analysisResult.change_24h >= 0 ? '+' : ''}{analysisResult.change_24h?.toFixed(2)}%</span>
                  </div>
                </div>
                <p className="text-zinc-300 whitespace-pre-wrap">{analysisResult.analysis}</p>
              </motion.div>
            )}
          </CardContent>
        </Card>

        {/* Agents Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {loading ? Array(5).fill(0).map((_, i) => (<Card key={i} className="glass-card animate-pulse"><CardContent className="p-6 h-[200px]" /></Card>)) : agents.map((agent) => {
            const Icon = getAgentIcon(agent.type);
            const color = getAgentColor(agent.type);
            return (
              <Card key={agent.id} className="glass-card card-hover" data-testid={`agent-card-${agent.name}`}>
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}20` }}><Icon className="w-6 h-6" style={{ color }} /></div>
                    <Badge className={agent.status === 'active' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-zinc-700 text-zinc-400'}>{agent.status}</Badge>
                  </div>
                  <h3 className="text-lg font-semibold mb-1">{agent.name}</h3>
                  <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{agent.description}</p>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div><p className="text-zinc-500">7D Perf</p><p className={`font-mono ${agent.performance_7d >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{agent.performance_7d >= 0 ? '+' : ''}{agent.performance_7d}%</p></div>
                    <div><p className="text-zinc-500">Allocation</p><p className="font-mono">{agent.capital_allocation}%</p></div>
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Recent Trades */}
        <Card className="glass-card" data-testid="recent-trades">
          <CardHeader><CardTitle className="flex items-center gap-2"><Activity className="w-5 h-5 text-[#00FF94]" />Recent Trades</CardTitle></CardHeader>
          <CardContent>
            <ScrollArea className="h-[300px]">
              <div className="space-y-3">
                {trades.map((trade) => (
                  <div key={trade.id} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`trade-${trade.id}`}>
                    <div className="flex items-center gap-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${trade.side === 'buy' ? 'bg-[#00FF94]/20' : 'bg-red-400/20'}`}>
                        {trade.side === 'buy' ? <ArrowUpRight className="w-4 h-4 text-[#00FF94]" /> : <ArrowDownRight className="w-4 h-4 text-red-400" />}
                      </div>
                      <div><p className="font-medium">{trade.symbol}</p><p className="text-xs text-zinc-500">{trade.agent_id}</p></div>
                    </div>
                    <div className="text-right">
                      <p className="font-mono">${trade.price?.toLocaleString()}</p>
                      <p className={`text-xs ${trade.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{trade.pnl >= 0 ? '+' : ''}{trade.pnl?.toFixed(2)} P&L</p>
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
  const [newAgent, setNewAgent] = useState({ name: '', description: '', strategy: '', min_investment: 100 });

  useEffect(() => {
    axios.get(`${API}/marketplace/agents`).then(res => setAgents(res.data)).catch(console.error).finally(() => setLoading(false));
  }, []);

  const handleSubmitAgent = async () => {
    if (!wallet) { toast.error("Connect wallet first"); return; }
    try {
      await axios.post(`${API}/marketplace/agents`, { ...newAgent, developer_address: wallet });
      toast.success("Agent submitted for review!");
      setShowSubmitDialog(false);
    } catch (error) { toast.error("Failed to submit agent"); }
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div><h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="marketplace-title">AI Agent Marketplace</h1><p className="text-zinc-400 mt-1">Discover and deploy community-built strategies</p></div>
          <Button onClick={() => setShowSubmitDialog(true)} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="submit-agent-btn"><Cpu className="w-4 h-4 mr-2" />Submit Your Agent</Button>
        </div>

        <Card className="glass-card mb-8 border-[#7B61FF]/30" data-testid="revenue-info">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row md:items-center gap-6">
              <div className="flex-1"><h3 className="text-lg font-semibold mb-2">Developer Revenue Model</h3><p className="text-zinc-400 text-sm">Deploy your AI trading agent and earn 90% of subscriber fees.</p></div>
              <div className="flex gap-8">
                <div className="text-center"><p className="text-3xl font-bold text-[#00FF94]">90%</p><p className="text-xs text-zinc-500">Developer Share</p></div>
                <div className="text-center"><p className="text-3xl font-bold text-zinc-400">10%</p><p className="text-xs text-zinc-500">Platform Fee</p></div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? Array(3).fill(0).map((_, i) => (<Card key={i} className="glass-card animate-pulse"><CardContent className="p-6 h-[250px]" /></Card>)) : agents.map((agent) => (
            <Card key={agent.id} className="glass-card card-hover" data-testid={`marketplace-agent-${agent.id}`}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center"><Bot className="w-6 h-6 text-white" /></div>
                  <Badge className="bg-[#00FF94]/20 text-[#00FF94]">{agent.total_subscribers} subscribers</Badge>
                </div>
                <h3 className="text-lg font-semibold mb-2">{agent.name}</h3>
                <p className="text-sm text-zinc-400 mb-4 line-clamp-2">{agent.description}</p>
                <div className="flex items-center justify-between text-sm mb-4"><span className="text-zinc-500">30D Return</span><span className={`font-mono ${agent.performance_30d >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{agent.performance_30d >= 0 ? '+' : ''}{agent.performance_30d}%</span></div>
                <Button className="w-full mt-4 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] hover:bg-[#7B61FF]/30" data-testid={`subscribe-${agent.id}`}>Subscribe</Button>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
        <DialogContent className="bg-[#121212] border-zinc-800" data-testid="submit-agent-dialog">
          <DialogHeader><DialogTitle>Submit Your AI Agent</DialogTitle></DialogHeader>
          <div className="space-y-4 py-4">
            <Input placeholder="Agent Name" value={newAgent.name} onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })} className="bg-[#050505] border-zinc-800" data-testid="agent-name-input" />
            <Input placeholder="Description" value={newAgent.description} onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })} className="bg-[#050505] border-zinc-800" data-testid="agent-description-input" />
            <Select value={newAgent.strategy} onValueChange={(v) => setNewAgent({ ...newAgent, strategy: v })}>
              <SelectTrigger className="bg-[#050505] border-zinc-800" data-testid="agent-strategy-select"><SelectValue placeholder="Select strategy" /></SelectTrigger>
              <SelectContent className="bg-[#121212] border-zinc-800">
                <SelectItem value="Momentum Trading">Momentum Trading</SelectItem>
                <SelectItem value="Arbitrage">Arbitrage</SelectItem>
                <SelectItem value="Yield Farming">Yield Farming</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setShowSubmitDialog(false)}>Cancel</Button><Button onClick={handleSubmitAgent} className="bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="submit-agent-confirm-btn">Submit</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Analytics Page
const AnalyticsPage = () => {
  const [analytics, setAnalytics] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [allocations, setAllocations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/analytics/overview`),
      axios.get(`${API}/analytics/strategies`),
      axios.get(`${API}/capital/allocations`)
    ]).then(([overviewRes, strategiesRes, allocRes]) => {
      setAnalytics(overviewRes.data);
      setStrategies(strategiesRes.data);
      setAllocations(allocRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="min-h-screen pt-24 px-4 flex items-center justify-center"><RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" /></div>;

  const dailyReturnsData = analytics?.daily_returns?.map((value, index) => ({ day: index + 1, return: value })) || [];

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8"><h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="analytics-title">Analytics & Performance</h1><p className="text-zinc-400 mt-1">Detailed performance metrics and strategy analysis</p></div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card" data-testid="metric-sharpe"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Sharpe Ratio</p><p className="text-3xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">{analytics?.sharpe_ratio}</p></CardContent></Card>
          <Card className="glass-card" data-testid="metric-sortino"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Sortino Ratio</p><p className="text-3xl font-bold text-[#00FF94] font-['JetBrains_Mono']">{analytics?.sortino_ratio}</p></CardContent></Card>
          <Card className="glass-card" data-testid="metric-drawdown"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Max Drawdown</p><p className="text-3xl font-bold text-red-400 font-['JetBrains_Mono']">-{analytics?.max_drawdown}%</p></CardContent></Card>
          <Card className="glass-card" data-testid="metric-winrate"><CardContent className="p-6 text-center"><p className="text-sm text-zinc-500 mb-2">Win Rate</p><p className="text-3xl font-bold font-['JetBrains_Mono']">{analytics?.win_rate}%</p></CardContent></Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <Card className="glass-card" data-testid="daily-returns-chart">
            <CardHeader><CardTitle>Daily Returns (30D)</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dailyReturnsData}><CartesianGrid strokeDasharray="3 3" stroke="#27272A" /><XAxis dataKey="day" stroke="#71717A" /><YAxis stroke="#71717A" /><Tooltip contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '8px' }} /><Bar dataKey="return" fill="#7B61FF" radius={[4, 4, 0, 0]} /></BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="capital-allocation-chart">
            <CardHeader><CardTitle className="flex items-center gap-2"><Scale className="w-5 h-5 text-[#00FF94]" />Capital Allocation</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={allocations} layout="vertical"><CartesianGrid strokeDasharray="3 3" stroke="#27272A" /><XAxis type="number" stroke="#71717A" /><YAxis dataKey="strategy_name" type="category" stroke="#71717A" width={120} /><Tooltip contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '8px' }} /><Bar dataKey="allocation_percent" fill="#00FF94" radius={[0, 4, 4, 0]} /></BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="glass-card" data-testid="strategies-table">
          <CardHeader><CardTitle>Strategy Details</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead><tr className="border-b border-zinc-800"><th className="text-left p-4 text-zinc-500">Strategy</th><th className="text-right p-4 text-zinc-500">Return</th><th className="text-right p-4 text-zinc-500">Trades</th><th className="text-right p-4 text-zinc-500">Win Rate</th></tr></thead>
                <tbody>
                  {strategies.map((strategy, index) => (
                    <tr key={index} className="border-b border-zinc-800/50" data-testid={`strategy-row-${index}`}>
                      <td className="p-4 font-medium">{strategy.name}</td>
                      <td className={`p-4 text-right font-mono ${strategy.return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{strategy.return >= 0 ? '+' : ''}{strategy.return}%</td>
                      <td className="p-4 text-right font-mono text-zinc-400">{strategy.trades}</td>
                      <td className="p-4 text-right font-mono">{strategy.win_rate}%</td>
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

// Admin Page
const AdminPage = () => {
  const [fundStats, setFundStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [trades, setTrades] = useState([]);
  const [agents, setAgents] = useState([]);
  const [riskConfig, setRiskConfig] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/fund/stats`),
      axios.get(`${API}/risk/alerts`),
      axios.get(`${API}/trades?limit=20`),
      axios.get(`${API}/agents`),
      axios.get(`${API}/risk/config`)
    ]).then(([statsRes, alertsRes, tradesRes, agentsRes, configRes]) => {
      setFundStats(statsRes.data);
      setAlerts(alertsRes.data);
      setTrades(tradesRes.data);
      setAgents(agentsRes.data);
      setRiskConfig(configRes.data);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const resolveAlert = async (alertId) => {
    try {
      await axios.post(`${API}/risk/alerts/${alertId}/resolve`);
      setAlerts(alerts.filter(a => a.id !== alertId));
      toast.success("Alert resolved");
    } catch (error) { toast.error("Failed to resolve alert"); }
  };

  const updateRiskConfig = async (field, value) => {
    try {
      const newConfig = { ...riskConfig, [field]: parseFloat(value) };
      await axios.put(`${API}/risk/config`, newConfig);
      setRiskConfig(newConfig);
      toast.success("Risk config updated");
    } catch (error) { toast.error("Update failed"); }
  };

  if (loading) return <div className="min-h-screen pt-24 px-4 flex items-center justify-center"><RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" /></div>;

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8"><h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="admin-title">Admin Dashboard</h1><p className="text-zinc-400 mt-1">Monitor fund operations and manage risk</p></div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card" data-testid="admin-nav"><CardContent className="p-6"><p className="text-sm text-zinc-500 mb-1">Fund NAV</p><p className="text-2xl font-bold font-['JetBrains_Mono']">{formatCurrency(fundStats?.nav)}</p></CardContent></Card>
          <Card className="glass-card" data-testid="admin-investors"><CardContent className="p-6"><p className="text-sm text-zinc-500 mb-1">Total Investors</p><p className="text-2xl font-bold font-['JetBrains_Mono']">{fundStats?.total_investors}</p></CardContent></Card>
          <Card className="glass-card" data-testid="admin-trades-24h"><CardContent className="p-6"><p className="text-sm text-zinc-500 mb-1">24h Trades</p><p className="text-2xl font-bold font-['JetBrains_Mono']">{fundStats?.total_trades_24h}</p></CardContent></Card>
          <Card className="glass-card" data-testid="admin-drawdown"><CardContent className="p-6"><p className="text-sm text-zinc-500 mb-1">Max Drawdown</p><p className="text-2xl font-bold text-red-400 font-['JetBrains_Mono']">-{fundStats?.max_drawdown}%</p></CardContent></Card>
        </div>

        {/* Risk Config */}
        {riskConfig && (
          <Card className="glass-card mb-8" data-testid="risk-config-card">
            <CardHeader><CardTitle className="flex items-center gap-2"><Gauge className="w-5 h-5 text-[#FF6B6B]" />Risk Configuration</CardTitle></CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4">
                <div>
                  <label className="text-sm text-zinc-400 block mb-1">Max Drawdown %</label>
                  <Input type="number" value={riskConfig.max_drawdown} onChange={e => updateRiskConfig('max_drawdown', e.target.value)} className="bg-[#050505] border-zinc-800" data-testid="risk-max-drawdown" />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 block mb-1">Max Position Size %</label>
                  <Input type="number" value={riskConfig.max_position_size} onChange={e => updateRiskConfig('max_position_size', e.target.value)} className="bg-[#050505] border-zinc-800" data-testid="risk-max-position" />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 block mb-1">Max Daily Loss %</label>
                  <Input type="number" value={riskConfig.max_daily_loss} onChange={e => updateRiskConfig('max_daily_loss', e.target.value)} className="bg-[#050505] border-zinc-800" data-testid="risk-max-daily-loss" />
                </div>
                <div>
                  <label className="text-sm text-zinc-400 block mb-1">Stop Loss %</label>
                  <Input type="number" value={riskConfig.stop_loss} onChange={e => updateRiskConfig('stop_loss', e.target.value)} className="bg-[#050505] border-zinc-800" data-testid="risk-stop-loss" />
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          <Card className="glass-card" data-testid="risk-alerts-card">
            <CardHeader><CardTitle className="flex items-center gap-2"><AlertTriangle className="w-5 h-5 text-[#FFB800]" />Risk Alerts</CardTitle></CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                <div className="space-y-3">
                  {alerts.length === 0 ? <p className="text-zinc-500 text-center py-8">No active alerts</p> : alerts.map((alert) => (
                    <div key={alert.id} className={`p-4 rounded-lg border ${alert.severity === 'high' ? 'bg-red-500/10 border-red-500/30' : alert.severity === 'medium' ? 'bg-[#FFB800]/10 border-[#FFB800]/30' : 'bg-zinc-800/50 border-zinc-700'}`} data-testid={`alert-${alert.id}`}>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge className={alert.severity === 'high' ? 'bg-red-500/20 text-red-400' : alert.severity === 'medium' ? 'bg-[#FFB800]/20 text-[#FFB800]' : 'bg-zinc-700 text-zinc-400'}>{alert.severity}</Badge>
                            <span className="text-xs text-zinc-500">{alert.type}</span>
                          </div>
                          <p className="text-sm">{alert.message}</p>
                        </div>
                        <Button size="sm" variant="ghost" onClick={() => resolveAlert(alert.id)} className="text-zinc-400 hover:text-white" data-testid={`resolve-alert-${alert.id}`}><Check className="w-4 h-4" /></Button>
                      </div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="agent-status-card">
            <CardHeader><CardTitle className="flex items-center gap-2"><Bot className="w-5 h-5 text-[#7B61FF]" />Agent Status</CardTitle></CardHeader>
            <CardContent>
              <ScrollArea className="h-[300px]">
                <div className="space-y-3">
                  {agents.map((agent) => (
                    <div key={agent.id} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`admin-agent-${agent.id}`}>
                      <div className="flex items-center gap-3">
                        <div className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-[#00FF94]' : 'bg-zinc-500'}`} />
                        <div><p className="font-medium text-sm">{agent.name}</p><p className="text-xs text-zinc-500">{agent.type}</p></div>
                      </div>
                      <Badge className={agent.status === 'active' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-zinc-700 text-zinc-400'}>{agent.status}</Badge>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        <Card className="glass-card" data-testid="trade-logs-card">
          <CardHeader><CardTitle className="flex items-center gap-2"><Activity className="w-5 h-5 text-[#00FF94]" />Trade Logs</CardTitle></CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead><tr className="border-b border-zinc-800"><th className="text-left p-3 text-zinc-500">Time</th><th className="text-left p-3 text-zinc-500">Agent</th><th className="text-left p-3 text-zinc-500">Symbol</th><th className="text-left p-3 text-zinc-500">Side</th><th className="text-right p-3 text-zinc-500">Price</th><th className="text-right p-3 text-zinc-500">P&L</th></tr></thead>
                <tbody>
                  {trades.slice(0, 10).map((trade) => (
                    <tr key={trade.id} className="border-b border-zinc-800/50" data-testid={`trade-log-${trade.id}`}>
                      <td className="p-3 text-sm text-zinc-400">{new Date(trade.timestamp).toLocaleTimeString()}</td>
                      <td className="p-3 text-sm">{trade.agent_id}</td>
                      <td className="p-3 font-mono text-sm">{trade.symbol}</td>
                      <td className="p-3"><Badge className={trade.side === 'buy' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-400/20 text-red-400'}>{trade.side}</Badge></td>
                      <td className="p-3 text-right font-mono text-sm">${trade.price?.toLocaleString()}</td>
                      <td className={`p-3 text-right font-mono text-sm ${trade.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{trade.pnl >= 0 ? '+' : ''}{trade.pnl?.toFixed(2)}</td>
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

// Simulation Control Page
const SimulationPage = () => {
  const [simConfig, setSimConfig] = useState(null);
  const [simStats, setSimStats] = useState(null);
  const [logs, setLogs] = useState([]);
  const [interactions, setInteractions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [cycleRunning, setCycleRunning] = useState(false);
  const [dailyReport, setDailyReport] = useState(null);
  const [weeklyReport, setWeeklyReport] = useState(null);
  const [activeTab, setActiveTab] = useState("control");
  
  // Enhanced simulation state
  const [acceleratedRunning, setAcceleratedRunning] = useState(false);
  const [stressTestRunning, setStressTestRunning] = useState(false);
  const [acceleratedResults, setAcceleratedResults] = useState(null);
  const [stressTestResults, setStressTestResults] = useState(null);
  const [agentPerformance, setAgentPerformance] = useState([]);
  const [daysToSimulate, setDaysToSimulate] = useState(30);

  const fetchData = async () => {
    try {
      const [configRes, statsRes, logsRes, interactionsRes] = await Promise.all([
        axios.get(`${API}/simulation/config`),
        axios.get(`${API}/simulation/stats`),
        axios.get(`${API}/simulation/logs?limit=30`),
        axios.get(`${API}/simulation/agent-interactions?limit=20`)
      ]);
      setSimConfig(configRes.data);
      setSimStats(statsRes.data);
      setLogs(logsRes.data);
      setInteractions(interactionsRes.data);
      setRunning(configRes.data?.is_running || false);
    } catch (error) {
      console.error("Error fetching simulation data:", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const startSimulation = async () => {
    try {
      const res = await axios.post(`${API}/simulation/start`);
      toast.success(res.data.message);
      setRunning(true);
      fetchData();
    } catch (error) {
      toast.error("Failed to start simulation");
    }
  };

  const stopSimulation = async () => {
    try {
      const res = await axios.post(`${API}/simulation/stop`);
      toast.success(res.data.message);
      setRunning(false);
      fetchData();
    } catch (error) {
      toast.error("Failed to stop simulation");
    }
  };

  const runCycle = async () => {
    setCycleRunning(true);
    try {
      const res = await axios.post(`${API}/simulation/run-cycle`);
      toast.success(`Cycle complete! ${res.data.cycle_results?.length || 0} trades executed`);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.message || "Cycle failed");
    }
    setCycleRunning(false);
  };

  const autoDeployTop = async () => {
    try {
      const res = await axios.post(`${API}/lab/auto-deploy-top`);
      toast.success(res.data.message);
      fetchData();
    } catch (error) {
      toast.error("Auto-deploy failed");
    }
  };

  const rebalanceCapital = async () => {
    try {
      await axios.post(`${API}/capital/rebalance`);
      toast.success("Capital rebalanced!");
      fetchData();
    } catch (error) {
      toast.error("Rebalance failed");
    }
  };

  const generateDailyReport = async () => {
    try {
      const res = await axios.get(`${API}/reports/daily`);
      setDailyReport(res.data);
      toast.success("Daily report generated!");
    } catch (error) {
      toast.error("Report generation failed");
    }
  };

  const generateWeeklyReport = async () => {
    try {
      const res = await axios.get(`${API}/reports/weekly`);
      setWeeklyReport(res.data);
      toast.success("Weekly report generated!");
    } catch (error) {
      toast.error("Report generation failed");
    }
  };

  const switchMode = async (newMode) => {
    try {
      const res = await axios.post(`${API}/simulation/switch-mode?mode=${newMode}&live_capital=1000`);
      toast.success(res.data.message);
      if (res.data.warning) toast.warning(res.data.warning);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Mode switch failed");
    }
  };

  const addStrategies = async () => {
    try {
      const res = await axios.post(`${API}/strategies/add-batch?count=3`);
      toast.success(res.data.message);
      fetchData();
    } catch (error) {
      toast.error("Failed to add strategies");
    }
  };

  // Enhanced simulation functions
  const runAcceleratedSimulation = async () => {
    setAcceleratedRunning(true);
    try {
      // First configure with 100x speed
      await axios.post(`${API}/simulation/configure`, {
        time_acceleration: 100,
        start_date: "2025-01-01",
        end_date: "2025-12-31",
        initial_capital: 100000,
        stress_test_enabled: true
      });
      
      // Load historical data
      await axios.post(`${API}/simulation/load-historical-data?use_sample=true`);
      
      // Run accelerated simulation
      const res = await axios.post(`${API}/simulation/run-accelerated?days_to_simulate=${daysToSimulate}`);
      setAcceleratedResults(res.data);
      toast.success(`Simulated ${daysToSimulate} days at 100x speed!`);
      fetchData();
      
      // Fetch agent performance
      const perfRes = await axios.get(`${API}/simulation/agent-performance`);
      setAgentPerformance(perfRes.data.agents || []);
    } catch (error) {
      toast.error("Accelerated simulation failed");
      console.error(error);
    }
    setAcceleratedRunning(false);
  };

  const runStressTest = async (scenario) => {
    setStressTestRunning(true);
    try {
      const res = await axios.post(`${API}/simulation/stress-test?scenario_name=${encodeURIComponent(scenario)}`);
      setStressTestResults(res.data);
      toast.success(`Stress test complete: ${res.data.results?.survival_status}`);
      fetchData();
    } catch (error) {
      toast.error("Stress test failed");
    }
    setStressTestRunning(false);
  };

  const exportResults = async () => {
    try {
      const res = await axios.post(`${API}/simulation/export`, {
        formats: ["pdf", "csv"],
        include_trades: true,
        include_agent_performance: true
      });
      toast.success("Results exported successfully!");
    } catch (error) {
      toast.error("Export failed");
    }
  };

  const getLogIcon = (type) => {
    switch (type) {
      case 'trade': return Activity;
      case 'risk': return AlertTriangle;
      case 'allocation': return Scale;
      case 'strategy': return Target;
      case 'agent': return Bot;
      default: return Terminal;
    }
  };

  const getLogColor = (type) => {
    switch (type) {
      case 'trade': return '#00FF94';
      case 'risk': return '#FF6B6B';
      case 'allocation': return '#7B61FF';
      case 'strategy': return '#FFB800';
      case 'agent': return '#00D4FF';
      default: return '#71717A';
    }
  };

  if (loading) return <div className="min-h-screen pt-24 px-4 flex items-center justify-center"><RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" /></div>;

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="simulation-title">MVP Simulation Control</h1>
            <p className="text-zinc-400 mt-1">Paper trading mode with full agent coordination</p>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={running ? 'bg-[#00FF94]/20 text-[#00FF94] animate-pulse' : 'bg-zinc-700 text-zinc-400'} data-testid="simulation-status">
              <CircleDot className="w-3 h-3 mr-1" />
              {running ? 'RUNNING' : 'STOPPED'}
            </Badge>
            {!running ? (
              <Button onClick={startSimulation} className="rounded-full bg-[#00FF94] text-black hover:bg-[#00FF94]/90" data-testid="start-simulation-btn">
                <Play className="w-4 h-4 mr-2" />Start Simulation
              </Button>
            ) : (
              <Button onClick={stopSimulation} variant="outline" className="rounded-full border-red-500/50 text-red-400 hover:bg-red-500/10" data-testid="stop-simulation-btn">
                <StopCircle className="w-4 h-4 mr-2" />Stop
              </Button>
            )}
          </div>
        </div>

        {/* Simulation Stats */}
        {simStats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
            <Card className="glass-card" data-testid="sim-capital">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Current Capital</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{formatCurrency(simStats.simulation?.current_capital || 10000)}</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-return">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Total Return</p>
                <p className={`text-xl font-bold font-['JetBrains_Mono'] ${simStats.simulation?.total_return_percent >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                  {simStats.simulation?.total_return_percent >= 0 ? '+' : ''}{simStats.simulation?.total_return_percent?.toFixed(2)}%
                </p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-trades">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Total Trades</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{simStats.trading?.total_trades || 0}</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-winrate">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Win Rate</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{simStats.trading?.win_rate?.toFixed(1) || 0}%</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-strategies">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Active Strategies</p>
                <p className="text-xl font-bold font-['JetBrains_Mono']">{simStats.strategies?.active || 0}</p>
              </CardContent>
            </Card>
            <Card className="glass-card" data-testid="sim-risk-events">
              <CardContent className="p-4 text-center">
                <p className="text-xs text-zinc-500 mb-1">Risk Events</p>
                <p className="text-xl font-bold font-['JetBrains_Mono'] text-[#FFB800]">{simStats.risk?.events_triggered || 0}</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Control Panel */}
        <Card className="glass-card mb-8 border-[#7B61FF]/30" data-testid="control-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Cpu className="w-5 h-5 text-[#7B61FF]" />Control Panel</CardTitle>
            <CardDescription>Execute simulation cycles, manage agents, and generate reports</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3 mb-4">
              <Button onClick={runCycle} disabled={!running || cycleRunning} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="run-cycle-btn">
                {cycleRunning ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Zap className="w-4 h-4 mr-2" />}
                Run Trade Cycle
              </Button>
              <Button onClick={autoDeployTop} variant="outline" className="rounded-full border-[#00FF94]/50 text-[#00FF94] hover:bg-[#00FF94]/10" data-testid="auto-deploy-btn">
                <Rocket className="w-4 h-4 mr-2" />Auto-Deploy Top
              </Button>
              <Button onClick={addStrategies} variant="outline" className="rounded-full border-[#FFB800]/50 text-[#FFB800] hover:bg-[#FFB800]/10" data-testid="add-strategies-btn">
                <Sparkles className="w-4 h-4 mr-2" />Add New Strategies
              </Button>
              <Button onClick={rebalanceCapital} variant="outline" className="rounded-full border-zinc-700" data-testid="rebalance-capital-btn">
                <Scale className="w-4 h-4 mr-2" />Rebalance
              </Button>
            </div>
            <div className="flex flex-wrap gap-3">
              <Button onClick={generateDailyReport} variant="outline" className="rounded-full border-zinc-700" data-testid="daily-report-btn">
                <FileCode className="w-4 h-4 mr-2" />Daily Report
              </Button>
              <Button onClick={generateWeeklyReport} variant="outline" className="rounded-full border-zinc-700" data-testid="weekly-report-btn">
                <ScrollText className="w-4 h-4 mr-2" />Weekly Report
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" className="rounded-full border-zinc-700" data-testid="mode-switch-btn">
                    <Radio className="w-4 h-4 mr-2" />
                    Mode: {simStats?.simulation?.mode?.toUpperCase() || 'PAPER'}
                    <ChevronDown className="w-4 h-4 ml-2" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="bg-[#121212] border-zinc-800">
                  <DropdownMenuItem onClick={() => switchMode('paper')} className={simStats?.simulation?.mode === 'paper' ? 'text-[#00FF94]' : ''}>
                    Paper Trading
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => switchMode('testnet')} className={simStats?.simulation?.mode === 'testnet' ? 'text-[#FFB800]' : ''}>
                    Testnet
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => switchMode('live')} className="text-red-400">
                    Live Trading ($1000)
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </CardContent>
        </Card>

        {/* Performance Reports */}
        {(dailyReport || weeklyReport) && (
          <Card className="glass-card mb-8 border-[#00FF94]/30" data-testid="reports-panel">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-[#00FF94]" />Performance Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <Tabs defaultValue="daily" className="w-full">
                <TabsList className="bg-[#050505] mb-4">
                  <TabsTrigger value="daily" disabled={!dailyReport}>Daily</TabsTrigger>
                  <TabsTrigger value="weekly" disabled={!weeklyReport}>Weekly</TabsTrigger>
                </TabsList>
                
                {dailyReport && (
                  <TabsContent value="daily">
                    <div className="grid md:grid-cols-3 gap-4 mb-4">
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Daily P&L</p>
                        <p className={`text-2xl font-bold font-['JetBrains_Mono'] ${dailyReport.summary?.daily_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {dailyReport.summary?.daily_pnl >= 0 ? '+' : ''}${dailyReport.summary?.daily_pnl?.toFixed(2)}
                        </p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Win Rate</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{dailyReport.trading?.win_rate?.toFixed(1)}%</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Trades Today</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{dailyReport.trading?.total_trades}</p>
                      </div>
                    </div>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-sm text-zinc-400 mb-2">Best Trade</p>
                        <p className="text-lg font-bold text-[#00FF94] font-['JetBrains_Mono']">+${dailyReport.trading?.best_trade?.toFixed(2)}</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-sm text-zinc-400 mb-2">Worst Trade</p>
                        <p className="text-lg font-bold text-red-400 font-['JetBrains_Mono']">${dailyReport.trading?.worst_trade?.toFixed(2)}</p>
                      </div>
                    </div>
                  </TabsContent>
                )}
                
                {weeklyReport && (
                  <TabsContent value="weekly">
                    <div className="grid md:grid-cols-4 gap-4 mb-4">
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Weekly P&L</p>
                        <p className={`text-2xl font-bold font-['JetBrains_Mono'] ${weeklyReport.summary?.weekly_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {weeklyReport.summary?.weekly_pnl >= 0 ? '+' : ''}${weeklyReport.summary?.weekly_pnl?.toFixed(2)}
                        </p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Sharpe Ratio</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#7B61FF]">{weeklyReport.summary?.sharpe_ratio}</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Win Rate</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{weeklyReport.trading?.win_rate?.toFixed(1)}%</p>
                      </div>
                      <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Total Trades</p>
                        <p className="text-2xl font-bold font-['JetBrains_Mono']">{weeklyReport.trading?.total_trades}</p>
                      </div>
                    </div>
                    <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                      <p className="text-sm text-zinc-400 mb-3">Daily Breakdown</p>
                      <div className="flex gap-2">
                        {weeklyReport.trading?.daily_breakdown?.slice(0, 7).map((day, i) => (
                          <div key={i} className="flex-1 text-center p-2 rounded bg-[#121212]">
                            <p className="text-xs text-zinc-500">{day.date?.slice(5)}</p>
                            <p className={`text-sm font-mono ${day.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                              {day.pnl >= 0 ? '+' : ''}{day.pnl}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                )}
              </Tabs>
            </CardContent>
          </Card>
        )}

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Simulation Logs */}
          <Card className="glass-card" data-testid="simulation-logs">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><ScrollText className="w-5 h-5 text-[#00FF94]" />Simulation Logs</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-2">
                  {logs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No logs yet. Start the simulation!</p>
                  ) : logs.map((log, i) => {
                    const Icon = getLogIcon(log.log_type);
                    const color = getLogColor(log.log_type);
                    return (
                      <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`log-${i}`}>
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ backgroundColor: `${color}20` }}>
                          <Icon className="w-4 h-4" style={{ color }} />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant="outline" className="text-xs" style={{ borderColor: color, color }}>{log.log_type}</Badge>
                            {log.agent_name && <span className="text-xs text-zinc-500">{log.agent_name}</span>}
                          </div>
                          <p className="text-sm text-zinc-300 break-words">{log.message}</p>
                          <p className="text-xs text-zinc-600 mt-1">{new Date(log.timestamp).toLocaleTimeString()}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Agent Interactions */}
          <Card className="glass-card" data-testid="agent-interactions">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Bot className="w-5 h-5 text-[#7B61FF]" />Agent Interactions</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-[400px]">
                <div className="space-y-2">
                  {interactions.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No interactions yet</p>
                  ) : interactions.map((interaction, i) => (
                    <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`interaction-${i}`}>
                      <div className="flex items-center gap-2 mb-2">
                        <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-xs">{interaction.from_agent}</Badge>
                        <ArrowUpRight className="w-3 h-3 text-zinc-500" />
                        <Badge className="bg-[#00FF94]/20 text-[#00FF94] text-xs">{interaction.to_agent}</Badge>
                      </div>
                      <p className="text-xs text-zinc-400">
                        <span className="text-[#FFB800]">{interaction.interaction_type}</span>: {JSON.stringify(interaction.payload).slice(0, 80)}...
                      </p>
                      <p className="text-xs text-zinc-600 mt-1">{new Date(interaction.timestamp).toLocaleTimeString()}</p>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Risk & Strategy Status */}
        <div className="grid lg:grid-cols-2 gap-6">
          <Card className="glass-card" data-testid="risk-status">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Shield className="w-5 h-5 text-[#FF6B6B]" />Risk Engine Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-zinc-400">Current Drawdown</span>
                    <span className={simStats?.risk?.current_drawdown > 4 ? 'text-red-400' : 'text-[#00FF94]'}>
                      {simStats?.risk?.current_drawdown?.toFixed(2) || 0}%
                    </span>
                  </div>
                  <Progress value={(simStats?.risk?.current_drawdown || 0) * 20} className="h-2" />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-zinc-400">Daily P&L</span>
                    <span className={simStats?.risk?.daily_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}>
                      {simStats?.risk?.daily_pnl >= 0 ? '+' : ''}{simStats?.risk?.daily_pnl?.toFixed(2) || 0}%
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505]">
                  <span className="text-sm text-zinc-400">Auto-Stop Enabled</span>
                  <Badge className="bg-[#00FF94]/20 text-[#00FF94]">Active</Badge>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505]">
                  <span className="text-sm text-zinc-400">Active Alerts</span>
                  <Badge className="bg-[#FFB800]/20 text-[#FFB800]">{simStats?.risk?.active_alerts || 0}</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="glass-card" data-testid="strategy-status">
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><Target className="w-5 h-5 text-[#FFB800]" />Strategy Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-[#00FF94]">{simStats?.strategies?.live || 0}</p>
                  <p className="text-xs text-zinc-500">Live</p>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-[#FFB800]">{simStats?.strategies?.in_sandbox || 0}</p>
                  <p className="text-xs text-zinc-500">In Sandbox</p>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-zinc-400">{simStats?.strategies?.total || 0}</p>
                  <p className="text-xs text-zinc-500">Total</p>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] text-center">
                  <p className="text-3xl font-bold text-[#7B61FF]">{simStats?.strategies?.active || 0}</p>
                  <p className="text-xs text-zinc-500">Active</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
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
            <Route path="/simulation" element={<SimulationPage />} />
            <Route path="/agents" element={<AgentsPage />} />
            <Route path="/lab" element={<StrategyLabPage />} />
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
