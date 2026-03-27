import { useState, useEffect, createContext, useContext, useMemo, useCallback } from "react";
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
  Beaker, Trophy, FileCode, Radio, CircleDot, Terminal, ScrollText,
  Plus, Minus, ArrowDown, Eye, PlayCircle, LogIn, LogOut, User,
  Bell, BellRing, Moon, Sun
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
import { ethers } from "ethers";
import { AuthProvider, useAuth } from "./contexts/AuthContext";
import { LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, VerifyEmailPage } from "./pages/AuthPages";
import PerformanceMetrics from "./components/PerformanceMetrics";
import ReferralDashboard from "./components/ReferralDashboard";
import CopyTradingPage, { FollowTraderModal } from "./pages/CopyTradingPage";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============= BRAND IDENTITY =============
// AlphaAI - Signal Intelligence System
// Brand Lockup Component with optional subtitle toggle

const BrandLockup = ({ 
  showSubtitle = false, 
  size = 'default', // 'small', 'default', 'large', 'hero'
  variant = 'default', // 'default', 'stacked', 'inline'
  className = ''
}) => {
  const sizes = {
    small: { icon: 'w-8 h-8', iconInner: 'w-4 h-4', title: 'text-lg', subtitle: 'text-[10px]' },
    default: { icon: 'w-10 h-10', iconInner: 'w-6 h-6', title: 'text-xl', subtitle: 'text-xs' },
    large: { icon: 'w-12 h-12', iconInner: 'w-7 h-7', title: 'text-2xl', subtitle: 'text-sm' },
    hero: { icon: 'w-16 h-16', iconInner: 'w-10 h-10', title: 'text-4xl', subtitle: 'text-base' }
  };
  
  const s = sizes[size] || sizes.default;
  
  if (variant === 'stacked') {
    return (
      <div className={`flex flex-col items-center ${className}`} data-testid="brand-lockup-stacked">
        <div className={`${s.icon} rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center mb-2`}>
          <Brain className={`${s.iconInner} text-white`} />
        </div>
        <span className={`${s.title} font-bold font-['Outfit'] tracking-tight`}>AlphaAI</span>
        {showSubtitle && (
          <span className={`${s.subtitle} text-zinc-400 font-light tracking-[0.2em] uppercase mt-1`}>
            Signal Intelligence System
          </span>
        )}
      </div>
    );
  }
  
  return (
    <div className={`flex items-center gap-3 ${className}`} data-testid="brand-lockup">
      <div className={`${s.icon} rounded-xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center`}>
        <Brain className={`${s.iconInner} text-white`} />
      </div>
      <div className="flex flex-col">
        <span className={`${s.title} font-bold font-['Outfit'] tracking-tight leading-none`}>AlphaAI</span>
        {showSubtitle && (
          <span className={`${s.subtitle} text-zinc-400 font-light tracking-[0.15em] uppercase`}>
            Signal Intelligence System
          </span>
        )}
      </div>
    </div>
  );
};

// Powered By Footer Tag
const PoweredByTag = ({ className = '' }) => (
  <div className={`flex items-center justify-center gap-2 text-xs text-zinc-500 ${className}`} data-testid="powered-by-tag">
    <span className="opacity-60">Powered by the</span>
    <span className="text-[#7B61FF] font-medium">AlphaAI</span>
    <span className="opacity-60">Signal Intelligence System</span>
  </div>
);

// Sepolia Chain Config
const SEPOLIA_CHAIN_ID = "0xaa36a7"; // 11155111 in hex
const SEPOLIA_CONFIG = {
  chainId: SEPOLIA_CHAIN_ID,
  chainName: "Sepolia Testnet",
  nativeCurrency: { name: "SepoliaETH", symbol: "ETH", decimals: 18 },
  rpcUrls: ["https://rpc.sepolia.org"],
  blockExplorerUrls: ["https://sepolia.etherscan.io"]
};

const WalletContext = createContext();
const useWallet = () => useContext(WalletContext);

const WalletProvider = ({ children }) => {
  const [wallet, setWallet] = useState(null);
  const [investor, setInvestor] = useState(null);
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState(null);
  const [signer, setSigner] = useState(null);
  const [chainId, setChainId] = useState(null);
  const [ethBalance, setEthBalance] = useState(null);
  const [contractAddress, setContractAddress] = useState(null);

  // Check if already connected on mount
  useEffect(() => {
    const checkConnection = async () => {
      if (typeof window.ethereum !== 'undefined') {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          await connectWallet();
        }
      }
    };
    checkConnection();

    // Listen for account changes
    if (window.ethereum) {
      window.ethereum.on('accountsChanged', (accounts) => {
        if (accounts.length === 0) {
          disconnectWallet();
        } else {
          setWallet(accounts[0]);
          updateBalance(accounts[0]);
        }
      });
      window.ethereum.on('chainChanged', () => window.location.reload());
    }

    // Fetch contract address
    axios.get(`${API}/contract/info`).then(res => {
      if (res.data.contract_address) setContractAddress(res.data.contract_address);
    }).catch(console.error);
  }, []);

  const updateBalance = async (address) => {
    if (provider && address) {
      try {
        const balance = await provider.getBalance(address);
        setEthBalance(ethers.utils.formatEther(balance));
      } catch (e) {
        console.error("Balance fetch error:", e);
      }
    }
  };

  const switchToSepolia = async () => {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: SEPOLIA_CHAIN_ID }]
      });
      return true;
    } catch (switchError) {
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [SEPOLIA_CONFIG]
          });
          return true;
        } catch (addError) {
          console.error("Failed to add Sepolia:", addError);
          return false;
        }
      }
      console.error("Failed to switch network:", switchError);
      return false;
    }
  };

  const connectWallet = async () => {
    setLoading(true);
    try {
      if (typeof window.ethereum !== 'undefined') {
        // Request accounts
        const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
        const address = accounts[0];
        
        // Setup provider and signer
        const web3Provider = new ethers.providers.Web3Provider(window.ethereum);
        const web3Signer = web3Provider.getSigner();
        const network = await web3Provider.getNetwork();
        
        setProvider(web3Provider);
        setSigner(web3Signer);
        setChainId(network.chainId);
        setWallet(address);
        
        // Get ETH balance
        const balance = await web3Provider.getBalance(address);
        setEthBalance(ethers.utils.formatEther(balance));
        
        // Register with backend
        const response = await axios.post(`${API}/investors/register`, { wallet_address: address });
        setInvestor(response.data);
        
        // Check if on Sepolia
        if (network.chainId !== 11155111) {
          toast.warning("Please switch to Sepolia testnet for full functionality");
        } else {
          toast.success("MetaMask connected to Sepolia!");
        }
      } else {
        toast.error("MetaMask not detected. Please install MetaMask.");
      }
    } catch (error) {
      console.error("Wallet connection error:", error);
      if (error.code === 4001) {
        toast.error("Connection rejected by user");
      } else {
        toast.error("Failed to connect wallet");
      }
    }
    setLoading(false);
  };

  const disconnectWallet = () => {
    setWallet(null);
    setInvestor(null);
    setProvider(null);
    setSigner(null);
    setChainId(null);
    setEthBalance(null);
    toast.info("Wallet disconnected");
  };

  const refreshInvestor = async () => {
    if (wallet) {
      try {
        const response = await axios.get(`${API}/investors/${wallet}`);
        setInvestor(response.data);
        if (provider) {
          const balance = await provider.getBalance(wallet);
          setEthBalance(ethers.utils.formatEther(balance));
        }
      } catch (error) {
        console.error("Error refreshing investor:", error);
      }
    }
  };

  // Deposit ETH to contract
  const depositToContract = async (amountEth) => {
    if (!signer || !contractAddress) {
      toast.error("Wallet or contract not connected");
      return null;
    }
    try {
      const tx = await signer.sendTransaction({
        to: contractAddress,
        value: ethers.utils.parseEther(amountEth.toString()),
        data: "0xd0e30db0" // deposit() selector
      });
      toast.info(`Transaction sent: ${tx.hash.slice(0, 10)}...`);
      const receipt = await tx.wait();
      toast.success("Deposit confirmed!");
      await refreshInvestor();
      return receipt;
    } catch (error) {
      console.error("Deposit error:", error);
      toast.error(error.message || "Deposit failed");
      return null;
    }
  };

  return (
    <WalletContext.Provider value={{ 
      wallet, investor, loading, provider, signer, chainId, ethBalance, contractAddress,
      connectWallet, disconnectWallet, refreshInvestor, switchToSepolia, depositToContract 
    }}>
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
  const { wallet, connectWallet, disconnectWallet, loading: walletLoading, chainId, ethBalance, switchToSepolia } = useWallet();
  const { user, isAuthenticated, logout, isPro } = useAuth();
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
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
    { path: "/admin", label: "Admin", icon: Shield },
  ];

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
            {/* User Authentication Status */}
            {isAuthenticated ? (
              <>
                {/* Pro Badge */}
                {isPro && (
                  <Badge className="bg-gradient-to-r from-[#7B61FF] to-[#00FF94] text-white" data-testid="pro-badge">
                    PRO
                  </Badge>
                )}
                
                {/* Wallet Section (if connected) */}
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
                
                {/* User Menu Dropdown */}
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
                      <p className="text-sm font-medium">{user?.name}</p>
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
            ) : (
              <>
                {/* Not logged in - show login/register */}
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
              {/* Mobile Auth Links */}
              {!isAuthenticated && (
                <div className="mt-4 pt-4 border-t border-zinc-800 space-y-2">
                  <Link to="/login" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-xl text-zinc-400">
                    <LogIn className="w-5 h-5" />Sign In
                  </Link>
                  <Link to="/register" onClick={() => setMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#7B61FF] text-white">
                    <User className="w-5 h-5" />Get Started
                  </Link>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </nav>
  );
};

// Live Price Ticker Component
const LivePriceTicker = ({ compact = false }) => {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState(null);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const res = await axios.get(`${API}/market/live-prices`);
        setPrices(res.data.prices || []);
        setLastUpdate(new Date());
        setLoading(false);
      } catch (error) {
        console.error("Price fetch error:", error);
        setLoading(false);
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const formatPrice = (price) => {
    if (price >= 1000) return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (price >= 1) return `$${price.toFixed(2)}`;
    return `$${price.toFixed(4)}`;
  };

  const formatVolume = (vol) => {
    if (vol >= 1e9) return `$${(vol / 1e9).toFixed(1)}B`;
    if (vol >= 1e6) return `$${(vol / 1e6).toFixed(1)}M`;
    return `$${vol.toLocaleString()}`;
  };

  if (compact) {
    return (
      <div className="flex items-center gap-4 overflow-x-auto py-2 px-4 bg-[#050505]/80 border-y border-zinc-800" data-testid="price-ticker-compact">
        <div className="flex items-center gap-1 text-xs text-zinc-500">
          <Radio className="w-3 h-3 text-[#00FF94] animate-pulse" />
          LIVE
        </div>
        {prices.slice(0, 6).map((coin) => (
          <div key={coin.id} className="flex items-center gap-2 whitespace-nowrap">
            <span className="font-mono font-bold text-sm">{coin.symbol}</span>
            <span className="font-mono text-sm">{formatPrice(coin.price)}</span>
            <span className={`text-xs font-mono ${coin.change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
              {coin.change_24h >= 0 ? '+' : ''}{coin.change_24h}%
            </span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <Card className="glass-card" data-testid="live-price-feed">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-[#00FF94] animate-pulse" />
            Live Market Prices
          </CardTitle>
          <div className="flex items-center gap-2 text-xs text-zinc-500">
            {lastUpdate && <span>Updated {lastUpdate.toLocaleTimeString()}</span>}
            <Badge className="bg-[#00FF94]/20 text-[#00FF94]">LIVE</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="w-6 h-6 animate-spin text-zinc-500" />
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {prices.map((coin) => (
              <div 
                key={coin.id} 
                className="p-3 rounded-lg bg-[#050505] border border-zinc-800 hover:border-zinc-700 transition-colors"
                data-testid={`price-${coin.symbol.toLowerCase()}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center text-xs font-bold">
                      {coin.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-bold text-sm">{coin.symbol}</p>
                      <p className="text-xs text-zinc-500">{coin.name}</p>
                    </div>
                  </div>
                </div>
                <div className="flex items-end justify-between">
                  <div>
                    <p className="text-lg font-mono font-bold">{formatPrice(coin.price)}</p>
                    <p className="text-xs text-zinc-500">Vol: {formatVolume(coin.volume_24h)}</p>
                  </div>
                  <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-mono ${
                    coin.change_24h >= 0 ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-400/20 text-red-400'
                  }`}>
                    {coin.change_24h >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                    {coin.change_24h >= 0 ? '+' : ''}{coin.change_24h}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
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
      {/* Live Price Ticker */}
      <LivePriceTicker compact={true} />
      
      <section className="relative px-4 py-20 md:py-32 overflow-hidden">
        <div className="absolute inset-0 grid-pattern opacity-50" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#7B61FF]/20 rounded-full blur-[120px]" />
        
        <div className="max-w-7xl mx-auto relative z-10">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="text-center max-w-4xl mx-auto">
            {/* Brand Lockup - Hero Version */}
            <div className="flex justify-center mb-8">
              <BrandLockup size="hero" variant="stacked" showSubtitle={true} />
            </div>
            
            <Badge className="mb-6 bg-[#7B61FF]/20 text-[#7B61FF] border-[#7B61FF]/30" data-testid="hero-badge">
              <Sparkles className="w-3 h-3 mr-1" />AI-Powered Trading Signals
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 font-['Outfit'] tracking-tight" data-testid="hero-title">
              <span className="text-gradient">Intelligent Signals</span><br />
              <span className="text-gradient-primary">Powered by AI</span>
            </h1>
            
            <p className="text-lg md:text-xl text-zinc-400 mb-10 max-w-2xl mx-auto" data-testid="hero-description">
              Advanced AI analyzes markets 24/7, delivering high-confidence trading signals with real-time execution and automated risk management.
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
        <div className="max-w-7xl mx-auto flex flex-col items-center gap-4">
          <BrandLockup size="small" showSubtitle={true} />
          <p className="text-sm text-zinc-500">© 2026 Martin Maughan. All rights reserved.</p>
          <PoweredByTag />
        </div>
      </footer>
    </div>
  );
};

// Notification Settings Component
const NotificationSettings = ({ walletAddress, isPro }) => {
  const [prefs, setPrefs] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testingNotification, setTestingNotification] = useState(false);

  useEffect(() => {
    if (walletAddress) {
      Promise.all([
        axios.get(`${API}/notifications/preferences?wallet_address=${walletAddress}`),
        axios.get(`${API}/notifications/config`)
      ]).then(([prefsRes, configRes]) => {
        setPrefs(prefsRes.data);
        setConfig(configRes.data);
      }).catch(console.error).finally(() => setLoading(false));
    }
  }, [walletAddress]);

  const updatePref = async (key, value) => {
    setSaving(true);
    try {
      const updateData = { [key]: value };
      const res = await axios.put(
        `${API}/notifications/preferences?wallet_address=${walletAddress}`,
        updateData
      );
      setPrefs(res.data);
      toast.success("Notification settings updated");
    } catch (error) {
      toast.error("Failed to update settings");
    }
    setSaving(false);
  };

  const sendTestNotification = async () => {
    setTestingNotification(true);
    try {
      const res = await axios.post(`${API}/notifications/test?wallet_address=${walletAddress}`);
      if (res.data.success) {
        toast.success("Test notification sent!");
      } else {
        toast.info(res.data.message || "No devices registered");
      }
    } catch (error) {
      toast.error("Failed to send test notification");
    }
    setTestingNotification(false);
  };

  if (loading) {
    return (
      <Card className="glass-card">
        <CardContent className="p-6 flex items-center justify-center">
          <RefreshCw className="w-5 h-5 animate-spin text-zinc-500" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="glass-card" data-testid="notification-settings">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-[#7B61FF]" />
          Push Notifications
          {isPro && (
            <Badge className="bg-gradient-to-r from-[#7B61FF] to-[#00FF94] text-white text-xs ml-2">
              PRO
            </Badge>
          )}
        </CardTitle>
        <CardDescription>
          Get instant alerts when high-confidence signals are generated
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main Toggle */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800">
          <div className="flex items-center gap-3">
            <BellRing className="w-4 h-4 text-[#00FF94]" />
            <span className="text-sm font-medium">Enable Push Notifications</span>
          </div>
          <Switch
            checked={prefs?.push_enabled ?? true}
            onCheckedChange={(checked) => updatePref('push_enabled', checked)}
            disabled={saving}
            data-testid="push-enabled-toggle"
          />
        </div>

        {/* High-Confidence Alerts - Featured */}
        {prefs?.push_enabled && (
          <div className="p-4 rounded-lg bg-gradient-to-r from-[#7B61FF]/10 to-transparent border border-[#7B61FF]/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-full bg-[#7B61FF]/20">
                  <Rocket className="w-4 h-4 text-[#7B61FF]" />
                </div>
                <div>
                  <span className="text-sm font-medium block">High-Confidence Signal Alerts</span>
                  <span className="text-xs text-zinc-500">
                    Signals with {config?.high_confidence_threshold || 75}%+ confidence
                  </span>
                </div>
              </div>
              <Switch
                checked={prefs?.high_confidence_alerts ?? true}
                onCheckedChange={(checked) => updatePref('high_confidence_alerts', checked)}
                disabled={saving || !isPro}
                data-testid="high-confidence-toggle"
              />
            </div>
            {!isPro && (
              <p className="text-xs text-yellow-400 mt-2 pl-11">
                Upgrade to Pro for instant high-confidence alerts
              </p>
            )}
          </div>
        )}

        {/* Other Notification Types */}
        {prefs?.push_enabled && (
          <div className="space-y-2">
            <p className="text-xs text-zinc-500 uppercase tracking-wider mb-2">Alert Types</p>
            
            {[
              { key: 'signal_alerts', label: 'All Signal Alerts', icon: Activity, desc: 'Every trading signal' },
              { key: 'trade_confirmations', label: 'Trade Confirmations', icon: Check, desc: 'When trades execute' },
              { key: 'price_alerts', label: 'Price Alerts', icon: TrendingUp, desc: 'Price target hits' },
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between p-2 rounded-lg hover:bg-[#050505]/50">
                <div className="flex items-center gap-2">
                  <item.icon className="w-4 h-4 text-zinc-500" />
                  <div>
                    <span className="text-sm">{item.label}</span>
                    <span className="text-xs text-zinc-600 block">{item.desc}</span>
                  </div>
                </div>
                <Switch
                  checked={prefs?.[item.key] ?? true}
                  onCheckedChange={(checked) => updatePref(item.key, checked)}
                  disabled={saving}
                />
              </div>
            ))}
          </div>
        )}

        {/* Quiet Hours */}
        {prefs?.push_enabled && (
          <div className="pt-3 border-t border-zinc-800">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Moon className="w-4 h-4 text-zinc-500" />
                <span className="text-sm">Quiet Hours</span>
              </div>
              <Switch
                checked={prefs?.quiet_hours?.enabled ?? false}
                onCheckedChange={(checked) => updatePref('quiet_hours_enabled', checked)}
                disabled={saving}
              />
            </div>
            {prefs?.quiet_hours?.enabled && (
              <div className="flex items-center gap-2 pl-6">
                <Input
                  type="time"
                  value={prefs?.quiet_hours?.start || "22:00"}
                  onChange={(e) => updatePref('quiet_hours_start', e.target.value)}
                  className="bg-[#050505] border-zinc-800 w-24 text-xs"
                />
                <span className="text-zinc-500">to</span>
                <Input
                  type="time"
                  value={prefs?.quiet_hours?.end || "08:00"}
                  onChange={(e) => updatePref('quiet_hours_end', e.target.value)}
                  className="bg-[#050505] border-zinc-800 w-24 text-xs"
                />
              </div>
            )}
          </div>
        )}

        {/* Test Notification Button */}
        <Button
          onClick={sendTestNotification}
          disabled={testingNotification || !prefs?.push_enabled}
          variant="outline"
          className="w-full rounded-full border-zinc-700 hover:border-[#7B61FF]"
          data-testid="test-notification-btn"
        >
          {testingNotification ? (
            <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
          ) : (
            <Bell className="w-4 h-4 mr-2" />
          )}
          Send Test Notification
        </Button>
      </CardContent>
    </Card>
  );
};

// Dashboard Page with Paper Trading
const DashboardPage = () => {
  const { wallet, investor, refreshInvestor } = useWallet();
  const [demoMode, setDemoMode] = useState(false);
  const [signals, setSignals] = useState([
    { symbol: 'BTC', signal: 'BUY', confidence: 87, price: 67432 },
    { symbol: 'ETH', signal: 'HOLD', confidence: 72, price: 3521 },
    { symbol: 'SOL', signal: 'SELL', confidence: 65, price: 142 },
  ]);
  const [aiSummary, setAiSummary] = useState("Market showing bullish momentum on BTC. ETH consolidating near support. Consider taking profits on SOL.");
  const [performance, setPerformance] = useState({ return_30d: 12.4, win_rate: 68, max_drawdown: 4.2, total_signals: 847 });
  const [showUpgradePopup, setShowUpgradePopup] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isPro, setIsPro] = useState(false);
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [selectedPackage, setSelectedPackage] = useState('pro_monthly');
  const [expandedSignal, setExpandedSignal] = useState(null); // Track which signal's AI explanation is expanded

  // Check for payment return and poll status
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const paymentStatus = urlParams.get('payment');
    
    if (sessionId && paymentStatus === 'success') {
      pollPaymentStatus(sessionId);
      // Clean URL
      window.history.replaceState({}, '', '/dashboard');
    } else if (paymentStatus === 'cancelled') {
      toast.info("Payment cancelled. You can upgrade anytime.");
      window.history.replaceState({}, '', '/dashboard');
    }
  }, []);

  // Check Pro status on mount
  useEffect(() => {
    if (wallet) {
      axios.get(`${API}/users/pro-status/${wallet}`).then(res => {
        if (res.data.is_pro) {
          setIsPro(true);
          toast.success("Welcome back, Pro user!");
        }
      }).catch(console.error);
    }
  }, [wallet]);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 10;
    const pollInterval = 2000;

    if (attempts >= maxAttempts) {
      toast.error("Payment verification timed out. Please refresh the page.");
      setIsProcessingPayment(false);
      return;
    }

    try {
      setIsProcessingPayment(true);
      const response = await axios.get(`${API}/payments/status/${sessionId}`);
      
      if (response.data.payment_status === 'paid') {
        setIsPro(true);
        setShowUpgradePopup(false);
        setIsProcessingPayment(false);
        toast.success("Welcome to AlphaAI Pro! You now have access to real-time signals.");
        return;
      } else if (response.data.status === 'expired') {
        toast.error("Payment session expired. Please try again.");
        setIsProcessingPayment(false);
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error("Error checking payment status:", error);
      if (attempts < maxAttempts - 1) {
        setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
      } else {
        toast.error("Error verifying payment. Please contact support.");
        setIsProcessingPayment(false);
      }
    }
  };

  const handleUpgradeClick = async (source = 'timed_popup') => {
    try {
      setIsProcessingPayment(true);
      trackEvent('conversion', source, { package: selectedPackage });
      
      const originUrl = window.location.origin;
      
      const response = await axios.post(`${API}/payments/checkout`, {
        package_id: selectedPackage,
        origin_url: originUrl,
        wallet_address: wallet || null
      });
      
      if (response.data.checkout_url) {
        window.location.href = response.data.checkout_url;
      } else {
        throw new Error("No checkout URL received");
      }
    } catch (error) {
      console.error("Error creating checkout:", error);
      toast.error("Failed to start checkout. Please try again.");
      setIsProcessingPayment(false);
    }
  };

  // Show upgrade popup after 2 minutes
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!isPro) {
        setShowUpgradePopup(true);
        trackEvent('view', 'timed_popup');
      }
    }, 120000); // 2 minutes
    return () => clearTimeout(timer);
  }, [isPro]);

  // === ANALYTICS TRACKING ===
  const sessionId = useMemo(() => {
    let id = sessionStorage.getItem('alphaai_session');
    if (!id) {
      id = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('alphaai_session', id);
    }
    return id;
  }, []);

  const trackEvent = useCallback(async (eventType, feature, metadata = {}) => {
    try {
      await axios.post(`${API}/analytics/track`, {
        event_type: eventType,
        feature: feature,
        session_id: sessionId,
        wallet_address: wallet || 'demo_user',
        metadata: metadata
      });
    } catch (e) {
      console.debug('Analytics tracking:', e.message);
    }
  }, [sessionId, wallet]);

  // Track page view on mount
  useEffect(() => {
    trackEvent('view', 'dashboard');
  }, [trackEvent]);

  // === HIGH-CONVERSION FEATURES STATE ===
  const [activeUsers, setActiveUsers] = useState(Math.floor(Math.random() * 36) + 15);
  const [nextUpdateTimer, setNextUpdateTimer] = useState(45);
  const [showExitPopup, setShowExitPopup] = useState(false);
  const [exitPopupShown, setExitPopupShown] = useState(false);
  const [missedTrades, setMissedTrades] = useState({
    BTC: { mins: 12, gain: 1.6 },
    ETH: { mins: 8, gain: 0.9 },
    SOL: { mins: 15, gain: 2.1 }
  });
  const [recentSignals] = useState([
    { symbol: 'BTC', action: 'BUY', result: '+2.1%', time: '2h ago' },
    { symbol: 'ETH', action: 'SELL', result: '+1.4%', time: '4h ago' },
    { symbol: 'SOL', action: 'BUY', result: '+3.0%', time: '6h ago' },
    { symbol: 'BTC', action: 'SELL', result: '+1.8%', time: '8h ago' },
    { symbol: 'ETH', action: 'BUY', result: '+2.4%', time: '12h ago' }
  ]);

  // === TRADING STATE ===
  const [tradingMode, setTradingMode] = useState('simulation'); // 'simulation' or 'live'
  const [showTradeModal, setShowTradeModal] = useState(false);
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [tradeAmount, setTradeAmount] = useState(100);
  const [isExecutingTrade, setIsExecutingTrade] = useState(false);
  const [portfolio, setPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  
  // Stop-Loss / Take-Profit state
  const [enableSL, setEnableSL] = useState(false);
  const [enableTP, setEnableTP] = useState(false);
  const [stopLossPrice, setStopLossPrice] = useState(0);
  const [takeProfitPrice, setTakeProfitPrice] = useState(0);
  const [activeOrders, setActiveOrders] = useState([]);

  // Fetch trading mode and portfolio
  useEffect(() => {
    if (wallet) {
      // Get trading mode
      axios.get(`${API}/trading/mode?wallet_address=${wallet}`)
        .then(res => setTradingMode(res.data.mode || 'simulation'))
        .catch(console.error);
      
      // Get portfolio
      axios.get(`${API}/trading/portfolio?wallet_address=${wallet}&is_live=false`)
        .then(res => setPortfolio(res.data))
        .catch(console.error);
      
      // Get positions
      axios.get(`${API}/trading/positions?wallet_address=${wallet}&is_live=false`)
        .then(res => setPositions(res.data.positions || []))
        .catch(console.error);
    }
  }, [wallet]);

  const handleExecuteTradeClick = (signal) => {
    if (!wallet && !demoMode) {
      toast.error("Connect wallet to trade");
      return;
    }
    setSelectedSignal(signal);
    
    // Set default SL/TP prices (5% below/above current price)
    if (signal.price) {
      setStopLossPrice(Math.round(signal.price * 0.95 * 100) / 100);
      setTakeProfitPrice(Math.round(signal.price * 1.10 * 100) / 100);
    }
    setEnableSL(false);
    setEnableTP(false);
    
    setShowTradeModal(true);
  };

  const executeTrade = async () => {
    if (!selectedSignal) return;
    
    setIsExecutingTrade(true);
    try {
      const response = await axios.post(`${API}/trading/execute`, {
        wallet_address: wallet || 'demo_user',
        symbol: selectedSignal.symbol,
        side: selectedSignal.signal,
        amount_usd: tradeAmount,
        is_live: tradingMode === 'live'
      });
      
      if (response.data.success) {
        const executedPrice = response.data.executed_price || selectedSignal.price;
        const quantity = tradeAmount / executedPrice;
        
        // Create Stop-Loss order if enabled
        if (enableSL && stopLossPrice > 0) {
          try {
            await axios.post(`${API}/orders/sl-tp?user_id=${wallet || 'demo_user'}`, {
              symbol: selectedSignal.symbol,
              order_type: 'stop_loss',
              trigger_price: stopLossPrice,
              quantity: quantity,
              current_position_price: executedPrice,
              trading_mode: tradingMode === 'live' ? 'live' : 'paper',
              trade_id: response.data.trade_id
            });
            toast.success(`Stop-Loss set at $${stopLossPrice.toLocaleString()}`);
          } catch (slErr) {
            console.error('SL order error:', slErr);
            toast.error('Failed to create Stop-Loss order');
          }
        }
        
        // Create Take-Profit order if enabled
        if (enableTP && takeProfitPrice > 0) {
          try {
            await axios.post(`${API}/orders/sl-tp?user_id=${wallet || 'demo_user'}`, {
              symbol: selectedSignal.symbol,
              order_type: 'take_profit',
              trigger_price: takeProfitPrice,
              quantity: quantity,
              current_position_price: executedPrice,
              trading_mode: tradingMode === 'live' ? 'live' : 'paper',
              trade_id: response.data.trade_id
            });
            toast.success(`Take-Profit set at $${takeProfitPrice.toLocaleString()}`);
          } catch (tpErr) {
            console.error('TP order error:', tpErr);
            toast.error('Failed to create Take-Profit order');
          }
        }
        
        toast.success(`${selectedSignal.signal} ${selectedSignal.symbol} executed at $${executedPrice?.toLocaleString()}`);
        setShowTradeModal(false);
        
        // Refresh portfolio
        const portfolioRes = await axios.get(`${API}/trading/portfolio?wallet_address=${wallet || 'demo_user'}&is_live=${tradingMode === 'live'}`);
        setPortfolio(portfolioRes.data);
        
        // Refresh positions
        const posRes = await axios.get(`${API}/trading/positions?wallet_address=${wallet || 'demo_user'}&is_live=${tradingMode === 'live'}`);
        setPositions(posRes.data.positions || []);
        
        // Refresh active orders
        loadActiveOrders();
        
        trackEvent('conversion', 'trade_executed', { symbol: selectedSignal.symbol, side: selectedSignal.signal, amount: tradeAmount });
      } else {
        toast.error(response.data.error || "Trade failed");
      }
    } catch (error) {
      console.error("Trade error:", error);
      toast.error(error.response?.data?.detail || "Trade execution failed");
    }
    setIsExecutingTrade(false);
  };

  const loadActiveOrders = async () => {
    try {
      const res = await axios.get(`${API}/orders/active?user_id=${wallet || 'demo_user'}`);
      setActiveOrders(res.data.orders || []);
    } catch (error) {
      console.error('Error loading orders:', error);
    }
  };

  const cancelOrder = async (orderId) => {
    try {
      await axios.delete(`${API}/orders/${orderId}?user_id=${wallet || 'demo_user'}`);
      toast.success('Order cancelled');
      loadActiveOrders();
    } catch (error) {
      toast.error('Failed to cancel order');
    }
  };

  const toggleTradingMode = async () => {
    const newMode = tradingMode === 'simulation' ? 'live' : 'simulation';
    
    if (newMode === 'live' && !wallet) {
      toast.error("Connect wallet to enable live trading");
      return;
    }
    
    if (newMode === 'live') {
      toast.warning("Live trading enabled. Real funds will be used!", { duration: 5000 });
    }
    
    try {
      await axios.post(`${API}/trading/mode?wallet_address=${wallet}&mode=${newMode}`);
      setTradingMode(newMode);
      toast.success(`Switched to ${newMode} mode`);
    } catch (error) {
      toast.error("Failed to switch mode");
    }
  };

  // Active users randomizer (updates every 30s)
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveUsers(prev => {
        const change = Math.floor(Math.random() * 7) - 3;
        const newVal = prev + change;
        return Math.max(15, Math.min(50, newVal));
      });
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  // Live countdown timer (60 second loop)
  useEffect(() => {
    const interval = setInterval(() => {
      setNextUpdateTimer(prev => prev <= 0 ? 60 : prev - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  // Missed trades updater (rotates every 20s)
  useEffect(() => {
    const interval = setInterval(() => {
      setMissedTrades({
        BTC: { mins: Math.floor(Math.random() * 16) + 5, gain: +(Math.random() * 2.5 + 0.5).toFixed(1) },
        ETH: { mins: Math.floor(Math.random() * 16) + 5, gain: +(Math.random() * 2.5 + 0.5).toFixed(1) },
        SOL: { mins: Math.floor(Math.random() * 16) + 5, gain: +(Math.random() * 2.5 + 0.5).toFixed(1) }
      });
    }, 20000);
    return () => clearInterval(interval);
  }, []);

  // Exit intent detection
  useEffect(() => {
    if (isPro || exitPopupShown) return;
    
    const handleMouseLeave = (e) => {
      if (e.clientY <= 0 && !exitPopupShown) {
        setShowExitPopup(true);
        setExitPopupShown(true);
        trackEvent('view', 'exit_popup');
      }
    };

    const handleBeforeUnload = (e) => {
      if (!exitPopupShown) {
        setShowExitPopup(true);
        setExitPopupShown(true);
        trackEvent('view', 'exit_popup');
      }
    };

    document.addEventListener('mouseleave', handleMouseLeave);
    window.addEventListener('beforeunload', handleBeforeUnload);
    
    return () => {
      document.removeEventListener('mouseleave', handleMouseLeave);
      window.removeEventListener('beforeunload', handleBeforeUnload);
    };
  }, [isPro, exitPopupShown]);

  // Fetch signals from tiered backend API
  useEffect(() => {
    const fetchSignals = async () => {
      try {
        // Use tiered endpoint with wallet if available
        const endpoint = wallet 
          ? `${API}/signals/tiered?wallet_address=${wallet}`
          : `${API}/signals/free`;
        
        const res = await axios.get(endpoint);
        
        if (res.data.signals && res.data.signals.length > 0) {
          // Update signals from backend with AI explanations
          const newSignals = res.data.signals.map(s => ({
            symbol: s.symbol,
            signal: s.signal_type,
            confidence: s.confidence,
            price: s.price_at_signal,
            analysis: s.analysis,
            isDelayed: s.is_delayed,
            generatedAt: s.generated_at,
            // AI Signal Intelligence fields
            explanation: s.explanation,
            reasoning: s.reasoning,
            trendAnalysis: s.trend_analysis,
            marketSentiment: s.market_sentiment,
            keyIndicators: s.key_indicators,
            riskLevel: s.risk_level,
            confidenceFactors: s.confidence_factors,
            potentialCatalysts: s.potential_catalysts,
            suggestedAction: s.suggested_action
          }));
          setSignals(newSignals);
          
          // Update Pro status based on response
          if (res.data.tier !== 'free') {
            setIsPro(true);
          }
        }
        
        // Update refresh timer based on tier
        const refreshRate = res.data.refresh_rate_seconds || 300;
        setNextUpdateTimer(refreshRate);
        
      } catch (error) {
        console.error("Signal fetch error:", error);
        // Fallback to live prices
        try {
          const priceRes = await axios.get(`${API}/live-prices`);
          if (priceRes.data.prices) {
            const btcPrice = priceRes.data.prices.find(p => p.symbol === 'BTC')?.price || 67432;
            const ethPrice = priceRes.data.prices.find(p => p.symbol === 'ETH')?.price || 3521;
            const solPrice = priceRes.data.prices.find(p => p.symbol === 'SOL')?.price || 142;
            setSignals([
              { symbol: 'BTC', signal: 'BUY', confidence: 87, price: btcPrice },
              { symbol: 'ETH', signal: 'HOLD', confidence: 72, price: ethPrice },
              { symbol: 'SOL', signal: 'SELL', confidence: 65, price: solPrice },
            ]);
          }
        } catch (e) {
          console.error("Fallback price fetch error:", e);
        }
      }
    };

    fetchSignals();
    
    // Set up polling based on tier (Pro: 1min, Free: 5min)
    const pollInterval = isPro ? 60000 : 300000;
    const interval = setInterval(fetchSignals, pollInterval);
    
    return () => clearInterval(interval);
  }, [wallet, isPro]);

  // Check Pro status from backend on wallet connect
  useEffect(() => {
    if (wallet) {
      axios.get(`${API}/subscription/tier?wallet_address=${wallet}`)
        .then(res => {
          if (res.data.tier === 'pro' || res.data.tier === 'elite') {
            setIsPro(true);
            toast.success(`Welcome back, ${res.data.tier.charAt(0).toUpperCase() + res.data.tier.slice(1)} user!`);
          }
        })
        .catch(console.error);
    }
  }, [wallet]);

  const getSignalColor = (signal) => {
    if (signal === 'BUY') return 'text-[#00FF94] bg-[#00FF94]/10 border-[#00FF94]/30';
    if (signal === 'SELL') return 'text-red-400 bg-red-400/10 border-red-400/30';
    return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/30';
  };

  const getSignalIcon = (signal) => {
    if (signal === 'BUY') return <ArrowUpRight className="w-6 h-6" />;
    if (signal === 'SELL') return <ArrowDownRight className="w-6 h-6" />;
    return <Activity className="w-6 h-6" />;
  };

  if (!wallet && !demoMode) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <Card className="glass-card max-w-md w-full" data-testid="connect-wallet-prompt">
          <CardContent className="p-8 text-center">
            <Wallet className="w-16 h-16 mx-auto mb-4 text-[#7B61FF]" />
            <h2 className="text-2xl font-bold mb-2">Connect Your Wallet</h2>
            <p className="text-zinc-400 mb-6">Connect to view your AI signals dashboard</p>
            <div className="flex flex-col gap-3">
              <WalletConnectButton />
              <Button 
                variant="outline" 
                onClick={() => setDemoMode(true)}
                className="rounded-full border-zinc-700 hover:border-[#7B61FF] hover:text-[#7B61FF]"
                data-testid="try-demo-btn"
              >
                <Eye className="w-4 h-4 mr-2" /> Try Demo Mode
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-4xl mx-auto">
        
        {/* SOCIAL PROOF: Active Users + Live Timer */}
        {!isPro && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mb-4 flex items-center justify-between text-sm"
          >
            <div className="flex items-center gap-2 text-zinc-400">
              <div className="w-2 h-2 rounded-full bg-[#00FF94] animate-pulse" />
              <span><span className="text-white font-medium">{activeUsers}</span> users viewing signals right now</span>
            </div>
            <div className="flex items-center gap-2 text-zinc-500">
              <RefreshCw className="w-3 h-3" />
              <span>Next update in: <span className="text-white font-mono">{String(Math.floor(nextUpdateTimer / 60)).padStart(2, '0')}:{String(nextUpdateTimer % 60).padStart(2, '0')}</span></span>
            </div>
          </motion.div>
        )}

        {/* Demo Mode Banner */}
        {demoMode && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/30 flex items-center justify-between"
            data-testid="demo-mode-banner"
          >
            <div className="flex items-center gap-3">
              <Zap className="w-5 h-5 text-[#7B61FF]" />
              <span className="text-[#7B61FF] font-medium">Upgrade to unlock full features</span>
            </div>
            <Button 
              onClick={() => setShowUpgradePopup(true)}
              className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 rounded-full px-6"
              data-testid="upgrade-demo-btn"
            >
              <Zap className="w-4 h-4 mr-2" /> Upgrade Now
            </Button>
          </motion.div>
        )}

        {/* Delayed Signals Warning - Enhanced Urgency */}
        {!isPro && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-5 rounded-xl bg-gradient-to-r from-yellow-500/20 to-orange-500/10 border border-yellow-500/40 flex flex-col md:flex-row md:items-center justify-between gap-4"
            data-testid="delayed-signals-warning"
          >
            <div className="flex items-start md:items-center gap-3">
              <div className="p-2 rounded-full bg-yellow-500/20 animate-pulse">
                <Clock className="w-5 h-5 text-yellow-400" />
              </div>
              <div>
                <span className="text-yellow-400 font-semibold block">Live signals update every minute</span>
                <span className="text-yellow-400/70 text-sm">You are viewing a 15 minute delay</span>
              </div>
            </div>
            <div className="flex flex-col items-center gap-2">
              <Button 
                onClick={() => {
                  setShowUpgradePopup(true);
                  trackEvent('click', 'unlock_live_btn');
                }} 
                className="bg-gradient-to-r from-[#7B61FF] to-[#9D4EDD] hover:from-[#6B51EF] hover:to-[#8D3ECD] rounded-full px-8 py-6 text-lg font-bold shadow-lg shadow-[#7B61FF]/30 glow-primary"
                data-testid="unlock-live-btn"
              >
                <Zap className="w-5 h-5 mr-2" /> Unlock Live Signals
              </Button>
              <div className="flex flex-col items-center text-xs text-zinc-400 mt-1">
                <span className="font-medium text-zinc-300">Unlock:</span>
                <span>Real-time signals • Instant alerts • Full AI analysis</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* TODAY'S AI SIGNALS - HERO SECTION */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <Card className="glass-card overflow-hidden" data-testid="signals-card">
            <CardHeader className="border-b border-zinc-800/50 bg-gradient-to-r from-[#7B61FF]/10 to-transparent">
              <CardTitle className="flex items-center gap-3 text-2xl">
                <div className="p-2 rounded-xl bg-[#7B61FF]/20">
                  <Brain className="w-6 h-6 text-[#7B61FF]" />
                </div>
                Today's AI Signals
                {!isPro && <Badge variant="outline" className="ml-2 text-yellow-400 border-yellow-400/30">Delayed</Badge>}
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6">
              {/* Trading Mode Toggle */}
              <div className="flex items-center justify-between mb-4 p-3 rounded-lg bg-[#050505] border border-zinc-800">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-zinc-400" />
                  <span className="text-sm text-zinc-400">Trading Mode:</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`text-sm ${tradingMode === 'simulation' ? 'text-[#7B61FF]' : 'text-zinc-500'}`}>Simulation</span>
                  <button 
                    onClick={toggleTradingMode}
                    className={`w-12 h-6 rounded-full p-1 transition-colors ${tradingMode === 'live' ? 'bg-[#00FF94]' : 'bg-zinc-700'}`}
                    data-testid="trading-mode-toggle"
                  >
                    <div className={`w-4 h-4 rounded-full bg-white transition-transform ${tradingMode === 'live' ? 'translate-x-6' : ''}`} />
                  </button>
                  <span className={`text-sm ${tradingMode === 'live' ? 'text-[#00FF94]' : 'text-zinc-500'}`}>Live</span>
                </div>
              </div>

              <div className="grid gap-4">
                {signals.map((s, i) => (
                  <motion.div
                    key={s.symbol}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className="relative"
                    data-testid={`signal-${s.symbol.toLowerCase()}`}
                  >
                    <div className={`p-5 rounded-xl border ${getSignalColor(s.signal)}`}>
                      {/* Signal Header */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="text-2xl font-bold font-['JetBrains_Mono']">{s.symbol}</div>
                          <div className="text-zinc-400 text-sm">${s.price?.toLocaleString()}</div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="text-right">
                            <div className="text-xs text-zinc-500 mb-1">Confidence</div>
                            <div className="font-mono text-sm">{s.confidence}%</div>
                          </div>
                          <div className={`flex items-center gap-2 px-4 py-2 rounded-full font-bold text-lg ${getSignalColor(s.signal)}`}>
                            {getSignalIcon(s.signal)}
                            {s.signal}
                          </div>
                          {/* Execute Trade Button */}
                          {s.signal !== 'HOLD' && (
                            <Button
                              onClick={() => handleExecuteTradeClick(s)}
                              className={`ml-2 rounded-full px-4 py-2 text-sm font-bold ${
                                s.signal === 'BUY' 
                                  ? 'bg-[#00FF94]/20 text-[#00FF94] hover:bg-[#00FF94]/30 border border-[#00FF94]/50' 
                                  : 'bg-red-500/20 text-red-400 hover:bg-red-500/30 border border-red-500/50'
                              }`}
                              data-testid={`execute-${s.symbol.toLowerCase()}`}
                            >
                              <PlayCircle className="w-4 h-4 mr-1" />
                              Execute
                            </Button>
                          )}
                        </div>
                      </div>
                      
                      {/* AI Explanation Summary */}
                      {s.explanation && (
                        <div className="mt-4 pt-4 border-t border-zinc-800/50">
                          <div className="flex items-start gap-3">
                            <Brain className="w-5 h-5 text-[#7B61FF] mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                              <p className="text-sm text-zinc-300">{s.explanation}</p>
                              {s.reasoning && (
                                <p className="text-xs text-zinc-500 mt-1">{s.reasoning}</p>
                              )}
                            </div>
                          </div>
                          
                          {/* Expand/Collapse Button */}
                          <button
                            onClick={() => setExpandedSignal(expandedSignal === s.symbol ? null : s.symbol)}
                            className="mt-3 flex items-center gap-1 text-xs text-[#7B61FF] hover:text-[#7B61FF]/80 transition-colors"
                            data-testid={`expand-analysis-${s.symbol.toLowerCase()}`}
                          >
                            <Sparkles className="w-3 h-3" />
                            {expandedSignal === s.symbol ? 'Hide AI Analysis' : 'View Full AI Analysis'}
                            <ChevronDown className={`w-3 h-3 transition-transform ${expandedSignal === s.symbol ? 'rotate-180' : ''}`} />
                          </button>
                          
                          {/* Expanded AI Analysis */}
                          <AnimatePresence>
                            {expandedSignal === s.symbol && (
                              <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="overflow-hidden"
                              >
                                <div className="mt-4 grid gap-4 md:grid-cols-2">
                                  {/* Trend Analysis */}
                                  {s.trendAnalysis && (
                                    <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`trend-analysis-${s.symbol.toLowerCase()}`}>
                                      <div className="flex items-center gap-2 mb-2">
                                        <TrendingUp className="w-4 h-4 text-[#7B61FF]" />
                                        <span className="text-sm font-semibold">Trend Analysis</span>
                                      </div>
                                      <div className="space-y-2 text-xs">
                                        <div className="flex justify-between">
                                          <span className="text-zinc-500">Direction</span>
                                          <span className={`font-medium ${
                                            s.trendAnalysis.direction === 'bullish' ? 'text-[#00FF94]' : 
                                            s.trendAnalysis.direction === 'bearish' ? 'text-red-400' : 'text-yellow-400'
                                          }`}>
                                            {s.trendAnalysis.direction?.toUpperCase()}
                                          </span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="text-zinc-500">Strength</span>
                                          <span className="text-zinc-300">{s.trendAnalysis.strength}</span>
                                        </div>
                                        <div className="flex justify-between">
                                          <span className="text-zinc-500">Timeframe</span>
                                          <span className="text-zinc-300">{s.trendAnalysis.timeframe}</span>
                                        </div>
                                        {s.trendAnalysis.description && (
                                          <p className="text-zinc-400 mt-2 pt-2 border-t border-zinc-800">{s.trendAnalysis.description}</p>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {/* Market Sentiment */}
                                  {s.marketSentiment && (
                                    <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`market-sentiment-${s.symbol.toLowerCase()}`}>
                                      <div className="flex items-center gap-2 mb-2">
                                        <Activity className="w-4 h-4 text-[#00D4FF]" />
                                        <span className="text-sm font-semibold">Market Sentiment</span>
                                      </div>
                                      <div className="space-y-2 text-xs">
                                        <div className="flex justify-between items-center">
                                          <span className="text-zinc-500">Overall</span>
                                          <span className={`font-medium ${
                                            s.marketSentiment.overall === 'bullish' ? 'text-[#00FF94]' : 
                                            s.marketSentiment.overall === 'bearish' ? 'text-red-400' : 'text-yellow-400'
                                          }`}>
                                            {s.marketSentiment.overall?.toUpperCase()}
                                          </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                          <span className="text-zinc-500">Score</span>
                                          <div className="flex items-center gap-2">
                                            <div className="w-16 h-2 bg-zinc-800 rounded-full overflow-hidden">
                                              <div 
                                                className={`h-full rounded-full ${s.marketSentiment.score > 0 ? 'bg-[#00FF94]' : 'bg-red-400'}`}
                                                style={{ width: `${Math.abs(s.marketSentiment.score)}%` }}
                                              />
                                            </div>
                                            <span className={`font-mono ${s.marketSentiment.score > 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                                              {s.marketSentiment.score > 0 ? '+' : ''}{s.marketSentiment.score}
                                            </span>
                                          </div>
                                        </div>
                                        {s.marketSentiment.factors && s.marketSentiment.factors.length > 0 && (
                                          <div className="mt-2 pt-2 border-t border-zinc-800">
                                            <p className="text-zinc-500 mb-1">Key Factors:</p>
                                            <ul className="space-y-1">
                                              {s.marketSentiment.factors.slice(0, 3).map((factor, idx) => (
                                                <li key={idx} className="text-zinc-400 flex items-start gap-1">
                                                  <span className="text-[#7B61FF]">•</span> {factor}
                                                </li>
                                              ))}
                                            </ul>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {/* Key Indicators */}
                                  {s.keyIndicators && (
                                    <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`key-indicators-${s.symbol.toLowerCase()}`}>
                                      <div className="flex items-center gap-2 mb-2">
                                        <BarChart3 className="w-4 h-4 text-[#FFB800]" />
                                        <span className="text-sm font-semibold">Key Indicators</span>
                                      </div>
                                      <div className="space-y-2 text-xs">
                                        {s.keyIndicators.rsi && (
                                          <div className="flex justify-between">
                                            <span className="text-zinc-500">RSI</span>
                                            <span className={`font-mono ${
                                              s.keyIndicators.rsi.signal === 'overbought' ? 'text-red-400' :
                                              s.keyIndicators.rsi.signal === 'oversold' ? 'text-[#00FF94]' : 'text-zinc-300'
                                            }`}>
                                              {s.keyIndicators.rsi.value} ({s.keyIndicators.rsi.signal})
                                            </span>
                                          </div>
                                        )}
                                        {s.keyIndicators.macd && (
                                          <div className="flex justify-between">
                                            <span className="text-zinc-500">MACD</span>
                                            <span className={`font-mono ${
                                              s.keyIndicators.macd.signal === 'bullish' ? 'text-[#00FF94]' :
                                              s.keyIndicators.macd.signal === 'bearish' ? 'text-red-400' : 'text-zinc-300'
                                            }`}>
                                              {s.keyIndicators.macd.signal} ({s.keyIndicators.macd.histogram})
                                            </span>
                                          </div>
                                        )}
                                        {s.keyIndicators.volume && (
                                          <div className="flex justify-between">
                                            <span className="text-zinc-500">Volume</span>
                                            <span className="text-zinc-300">
                                              {s.keyIndicators.volume.trend} ({s.keyIndicators.volume.significance})
                                            </span>
                                          </div>
                                        )}
                                        {s.keyIndicators.support_resistance && (
                                          <div className="mt-2 pt-2 border-t border-zinc-800">
                                            <div className="flex justify-between">
                                              <span className="text-zinc-500">Support</span>
                                              <span className="text-[#00FF94] font-mono">
                                                ${s.keyIndicators.support_resistance.nearest_support?.toLocaleString()}
                                              </span>
                                            </div>
                                            <div className="flex justify-between mt-1">
                                              <span className="text-zinc-500">Resistance</span>
                                              <span className="text-red-400 font-mono">
                                                ${s.keyIndicators.support_resistance.nearest_resistance?.toLocaleString()}
                                              </span>
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>
                                  )}
                                  
                                  {/* Risk & Action */}
                                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`risk-action-${s.symbol.toLowerCase()}`}>
                                    <div className="flex items-center gap-2 mb-2">
                                      <Shield className="w-4 h-4 text-[#FF61DC]" />
                                      <span className="text-sm font-semibold">Risk & Action</span>
                                    </div>
                                    <div className="space-y-2 text-xs">
                                      {s.riskLevel && (
                                        <div className="flex justify-between">
                                          <span className="text-zinc-500">Risk Level</span>
                                          <Badge className={`text-xs ${
                                            s.riskLevel === 'high' ? 'bg-red-500/20 text-red-400' :
                                            s.riskLevel === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                                            'bg-[#00FF94]/20 text-[#00FF94]'
                                          }`}>
                                            {s.riskLevel.toUpperCase()}
                                          </Badge>
                                        </div>
                                      )}
                                      {s.confidenceFactors && s.confidenceFactors.length > 0 && (
                                        <div className="mt-2">
                                          <p className="text-zinc-500 mb-1">Confidence Factors:</p>
                                          <div className="flex flex-wrap gap-1">
                                            {s.confidenceFactors.slice(0, 3).map((factor, idx) => (
                                              <span key={idx} className="px-2 py-0.5 rounded-full bg-[#7B61FF]/10 text-[#7B61FF] text-xs">
                                                {factor}
                                              </span>
                                            ))}
                                          </div>
                                        </div>
                                      )}
                                      {s.suggestedAction && (
                                        <div className="mt-3 pt-2 border-t border-zinc-800">
                                          <p className="text-zinc-500 mb-1">Suggested Action:</p>
                                          <p className="text-[#00FF94] font-medium">{s.suggestedAction}</p>
                                        </div>
                                      )}
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Potential Catalysts */}
                                {s.potentialCatalysts && s.potentialCatalysts.length > 0 && (
                                  <div className="mt-4 p-3 rounded-lg bg-[#7B61FF]/5 border border-[#7B61FF]/20">
                                    <div className="flex items-center gap-2 mb-2">
                                      <Zap className="w-4 h-4 text-[#7B61FF]" />
                                      <span className="text-sm font-semibold text-[#7B61FF]">Potential Catalysts</span>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                      {s.potentialCatalysts.map((catalyst, idx) => (
                                        <span key={idx} className="px-2 py-1 rounded-full bg-[#7B61FF]/10 text-zinc-300 text-xs">
                                          {catalyst}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      )}
                    </div>
                    {/* MISSED TRADE TRIGGER - FOMO */}
                    {!isPro && missedTrades[s.symbol] && (
                      <div className="mt-2 flex items-center gap-2 text-xs text-zinc-500 pl-2">
                        <Clock className="w-3 h-3 text-yellow-500" />
                        <span>Signal triggered <span className="text-yellow-400">{missedTrades[s.symbol].mins} mins ago</span></span>
                        <span className="text-zinc-600">→</span>
                        <span className="text-[#00FF94] font-medium">+{missedTrades[s.symbol].gain}%</span>
                        <span className="text-zinc-600 italic ml-1">You missed this</span>
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
              
              {/* Performance Summary Under Signals */}
              <div className="mt-6 pt-6 border-t border-zinc-800/50">
                <p className="text-sm text-zinc-500 mb-3 font-medium">Last 30 Days Performance:</p>
                <div className="flex flex-wrap items-center gap-6">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-[#00FF94]" />
                    <span className="text-2xl font-bold text-[#00FF94] font-['JetBrains_Mono']">+{performance.return_30d}%</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-zinc-400" />
                    <span className="text-lg font-semibold text-white">{performance.win_rate}%</span>
                    <span className="text-sm text-zinc-500">win rate</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Shield className="w-4 h-4 text-zinc-400" />
                    <span className="text-lg font-semibold text-white">{performance.max_drawdown}%</span>
                    <span className="text-sm text-zinc-500">max drawdown</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* PERFORMANCE SECTION */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-8"
        >
          <Card className="glass-card" data-testid="performance-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-[#00FF94]" />
                Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800 text-center">
                  <p className="text-zinc-500 text-sm mb-1">Last 30 Days</p>
                  <p className="text-3xl font-bold text-[#00FF94] font-['JetBrains_Mono']">+{performance.return_30d}%</p>
                  <p className="text-xs text-zinc-600 mt-1">(paper trading)</p>
                </div>
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800 text-center">
                  <p className="text-zinc-500 text-sm mb-1">Win Rate</p>
                  <p className="text-3xl font-bold font-['JetBrains_Mono']">{performance.win_rate}%</p>
                </div>
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800 text-center">
                  <p className="text-zinc-500 text-sm mb-1">Max Drawdown</p>
                  <p className="text-3xl font-bold text-yellow-400 font-['JetBrains_Mono']">-{performance.max_drawdown}%</p>
                </div>
                <div className="p-4 rounded-xl bg-[#050505] border border-zinc-800 text-center">
                  <p className="text-zinc-500 text-sm mb-1">Total Signals</p>
                  <p className="text-3xl font-bold font-['JetBrains_Mono']">{performance.total_signals}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* ADVANCED PERFORMANCE METRICS - Paper vs Live */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.22 }}
          className="mb-8"
        >
          <PerformanceMetrics walletAddress={wallet || 'demo_user'} />
        </motion.div>

        {/* NOTIFICATION SETTINGS - Pro/Elite Feature */}
        {(isPro || wallet || demoMode) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.23 }}
            className="mb-8"
          >
            <NotificationSettings walletAddress={wallet || 'demo_user'} isPro={isPro || demoMode} />
          </motion.div>
        )}

        {/* RECENT SIGNALS - TRUST BUILDER */}
        {!isPro && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
            className="mb-8"
          >
            <Card className="glass-card" data-testid="recent-signals-card">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Activity className="w-5 h-5 text-[#7B61FF]" />
                  Recent Signals
                  <Badge variant="outline" className="ml-2 text-xs text-zinc-500 border-zinc-700">Last 24h</Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {recentSignals.map((signal, i) => (
                    <div 
                      key={i} 
                      className="flex items-center justify-between p-3 rounded-lg bg-[#050505]/50 border border-zinc-800/50"
                    >
                      <div className="flex items-center gap-3">
                        <span className="font-bold font-['JetBrains_Mono'] text-sm">{signal.symbol}</span>
                        <span className="text-zinc-600">→</span>
                        <span className={`text-sm font-medium ${signal.action === 'BUY' ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {signal.action}
                        </span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-[#00FF94] font-mono font-medium">{signal.result}</span>
                        <span className="text-xs text-zinc-600">{signal.time}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-zinc-600 mt-3 text-center">
                  Pro users received these signals in real-time
                </p>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* AI SUMMARY */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-8"
        >
          <Card className="glass-card" data-testid="ai-summary-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-[#FFB800]" />
                AI Market Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-zinc-300 text-lg leading-relaxed">{aiSummary}</p>
              <p className="text-xs text-zinc-600 mt-3">Updated 15 minutes ago</p>
            </CardContent>
          </Card>
        </motion.div>

        {/* UPGRADE CTA */}
        {!isPro && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="mb-8"
          >
            <Card className="overflow-hidden border-[#7B61FF]/50" data-testid="upgrade-cta-card">
              <div className="bg-gradient-to-r from-[#7B61FF]/20 via-[#7B61FF]/10 to-transparent p-8">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Unlock Live Signals</h3>
                    <p className="text-zinc-400 mb-4">Get real-time AI signals, instant alerts, and priority support.</p>
                    <div className="flex flex-wrap gap-3">
                      <div className="flex items-center gap-2 text-sm text-zinc-300">
                        <Check className="w-4 h-4 text-[#00FF94]" /> Real-time signals
                      </div>
                      <div className="flex items-center gap-2 text-sm text-zinc-300">
                        <Check className="w-4 h-4 text-[#00FF94]" /> Instant alerts
                      </div>
                      <div className="flex items-center gap-2 text-sm text-zinc-300">
                        <Check className="w-4 h-4 text-[#00FF94]" /> Advanced AI insights
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-col items-center gap-2">
                    <Button 
                      onClick={() => {
                        setShowUpgradePopup(true);
                        trackEvent('click', 'upgrade_cta');
                      }}
                      className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-white px-8 py-6 rounded-full text-lg font-bold glow-primary"
                      data-testid="upgrade-btn"
                    >
                      <Zap className="w-5 h-5 mr-2" /> Upgrade to Pro
                    </Button>
                    <span className="text-sm text-zinc-500">Starting at $29/month</span>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        )}

        {/* LOCKED FEATURES PREVIEW */}
        {!isPro && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mb-8"
          >
            <div className="grid md:grid-cols-2 gap-4">
              <Card className="glass-card relative overflow-hidden" data-testid="locked-alerts">
                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex items-center justify-center">
                  <div className="text-center">
                    <Shield className="w-8 h-8 mx-auto mb-2 text-zinc-500" />
                    <p className="text-zinc-400 font-medium">Pro Feature</p>
                  </div>
                </div>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-zinc-500">
                    <Radio className="w-5 h-5" /> Real-Time Alerts
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 opacity-50">
                    <div className="p-3 rounded-lg bg-[#050505]">Push notification: BTC signal changed</div>
                    <div className="p-3 rounded-lg bg-[#050505]">Email alert: New high-confidence trade</div>
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-card relative overflow-hidden" data-testid="locked-analytics">
                <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex items-center justify-center">
                  <div className="text-center">
                    <Shield className="w-8 h-8 mx-auto mb-2 text-zinc-500" />
                    <p className="text-zinc-400 font-medium">Pro Feature</p>
                  </div>
                </div>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-zinc-500">
                    <BarChart3 className="w-5 h-5" /> Advanced Analytics
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-32 flex items-center justify-center opacity-50">
                    <BarChart3 className="w-16 h-16 text-zinc-700" />
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        )}

        {/* OPEN POSITIONS */}
        {positions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.55 }}
            className="mb-8"
          >
            <Card className="glass-card" data-testid="positions-card">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <PieChart className="w-5 h-5 text-[#7B61FF]" />
                    Open Positions
                    <Badge variant="outline" className="ml-2 text-xs">{tradingMode}</Badge>
                  </div>
                  {portfolio && (
                    <span className={`font-mono text-sm ${portfolio.net_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {portfolio.net_pnl >= 0 ? '+' : ''}{portfolio.net_pnl?.toFixed(2)} USD
                    </span>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {positions.map((pos, i) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-lg bg-[#050505] border border-zinc-800">
                      <div className="flex items-center gap-4">
                        <div>
                          <div className="font-bold">{pos.symbol}</div>
                          <div className="text-xs text-zinc-500">{pos.side}</div>
                        </div>
                        <div className="text-sm text-zinc-400">
                          {pos.amount?.toFixed(6)} @ ${pos.entry_price?.toLocaleString()}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className={`font-mono font-bold ${pos.unrealized_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {pos.unrealized_pnl >= 0 ? '+' : ''}{pos.unrealized_pnl?.toFixed(2)} USD
                        </div>
                        <div className={`text-xs ${pos.unrealized_pnl_percent >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {pos.unrealized_pnl_percent >= 0 ? '+' : ''}{pos.unrealized_pnl_percent?.toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* ADVANCED TOGGLE (Hidden by default) */}
        <div className="text-center">
          <Button 
            variant="ghost" 
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="text-zinc-500 hover:text-zinc-300"
            data-testid="show-advanced-btn"
          >
            {showAdvanced ? 'Hide' : 'Show'} Advanced Options
            <ChevronDown className={`w-4 h-4 ml-1 transition-transform ${showAdvanced ? 'rotate-180' : ''}`} />
          </Button>
        </div>

        {showAdvanced && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-6 space-y-4"
          >
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="text-sm text-zinc-500">Paper Trading Sandbox</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-zinc-600 text-sm">Practice trading with virtual funds. Available in advanced settings.</p>
                <Button variant="outline" className="mt-3 rounded-full border-zinc-700" asChild>
                  <Link to="/simulation">Open Sandbox</Link>
                </Button>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </div>

      {/* Powered By Footer */}
      <div className="mt-8 mb-4 px-4">
        <PoweredByTag />
      </div>

      {/* UPGRADE POPUP (Shows after 2 minutes) */}
      <Dialog open={showUpgradePopup} onOpenChange={setShowUpgradePopup}>
        <DialogContent className="bg-[#121212] border-[#7B61FF]/30 max-w-md" data-testid="upgrade-popup">
          <DialogHeader>
            <DialogTitle className="text-2xl text-center">
              <Zap className="w-8 h-8 mx-auto mb-2 text-[#7B61FF]" />
              Unlock Real-Time Signals
            </DialogTitle>
            <DialogDescription className="text-center text-zinc-400">
              Get instant AI signals before the market moves
            </DialogDescription>
          </DialogHeader>
          <div className="py-6 space-y-4">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-[#050505]">
              <Check className="w-5 h-5 text-[#00FF94]" />
              <span>Real-time signals (no 15 min delay)</span>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-[#050505]">
              <Check className="w-5 h-5 text-[#00FF94]" />
              <span>Push notifications & email alerts</span>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-[#050505]">
              <Check className="w-5 h-5 text-[#00FF94]" />
              <span>Advanced AI market analysis</span>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-[#050505]">
              <Check className="w-5 h-5 text-[#00FF94]" />
              <span>Priority support</span>
            </div>
            
            {/* Package Selection */}
            <div className="pt-4 space-y-3">
              <div 
                className={`p-4 rounded-lg border cursor-pointer transition-all ${selectedPackage === 'pro_monthly' ? 'border-[#7B61FF] bg-[#7B61FF]/10' : 'border-zinc-700 hover:border-zinc-600'}`}
                onClick={() => setSelectedPackage('pro_monthly')}
                data-testid="package-monthly"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">Monthly</p>
                    <p className="text-sm text-zinc-400">Billed monthly</p>
                  </div>
                  <p className="text-xl font-bold">$29<span className="text-sm text-zinc-400">/mo</span></p>
                </div>
              </div>
              <div 
                className={`p-4 rounded-lg border cursor-pointer transition-all relative ${selectedPackage === 'pro_yearly' ? 'border-[#7B61FF] bg-[#7B61FF]/10' : 'border-zinc-700 hover:border-zinc-600'}`}
                onClick={() => setSelectedPackage('pro_yearly')}
                data-testid="package-yearly"
              >
                <Badge className="absolute -top-2 right-3 bg-[#00FF94] text-black">Save $99</Badge>
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-semibold">Yearly</p>
                    <p className="text-sm text-zinc-400">2 months FREE</p>
                  </div>
                  <p className="text-xl font-bold">$249<span className="text-sm text-zinc-400">/yr</span></p>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter className="flex-col gap-3">
            <Button 
              className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 py-6 text-lg font-bold rounded-full glow-primary"
              data-testid="upgrade-now-btn"
              onClick={() => handleUpgradeClick('timed_popup')}
              disabled={isProcessingPayment}
            >
              {isProcessingPayment ? (
                <>
                  <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5 mr-2" />
                  {selectedPackage === 'pro_monthly' ? 'Upgrade Now — $29/month' : 'Upgrade Now — $249/year'}
                </>
              )}
            </Button>
            <Button variant="ghost" onClick={() => setShowUpgradePopup(false)} className="text-zinc-500" disabled={isProcessingPayment}>
              Maybe later
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* EXIT INTENT POPUP - Recover Abandoning Users */}
      <Dialog open={showExitPopup} onOpenChange={setShowExitPopup}>
        <DialogContent className="bg-[#121212] border-red-500/30 max-w-md" data-testid="exit-popup">
          <DialogHeader>
            <DialogTitle className="text-2xl text-center">
              <AlertTriangle className="w-10 h-10 mx-auto mb-3 text-yellow-500" />
              Wait — unlock live signals before you go
            </DialogTitle>
            <DialogDescription className="text-center text-zinc-400 text-base">
              You're currently seeing <span className="text-yellow-400 font-medium">delayed signals</span>.
              <br />
              Pro users are trading with real-time data right now.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="p-4 rounded-xl bg-gradient-to-r from-[#7B61FF]/10 to-[#00FF94]/10 border border-[#7B61FF]/30">
              <p className="text-sm text-zinc-400 mb-2">What you're missing:</p>
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm">
                  <Zap className="w-4 h-4 text-[#7B61FF]" />
                  <span>Instant signal alerts (no 15 min delay)</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <TrendingUp className="w-4 h-4 text-[#00FF94]" />
                  <span>Average <span className="text-[#00FF94] font-bold">+12.4%</span> monthly returns</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Users className="w-4 h-4 text-[#FFB800]" />
                  <span><span className="text-white font-medium">{activeUsers}</span> traders using Pro right now</span>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter className="flex-col gap-3">
            <Button 
              className="w-full bg-gradient-to-r from-[#7B61FF] to-[#9D4EDD] hover:from-[#6B51EF] hover:to-[#8D3ECD] py-6 text-lg font-bold rounded-full shadow-lg shadow-[#7B61FF]/30"
              data-testid="exit-upgrade-btn"
              onClick={() => {
                trackEvent('click', 'exit_popup');
                setShowExitPopup(false);
                handleUpgradeClick('exit_popup');
              }}
            >
              <Zap className="w-5 h-5 mr-2" /> Upgrade Now — $29/month
            </Button>
            <Button variant="ghost" onClick={() => {
              trackEvent('dismiss', 'exit_popup');
              setShowExitPopup(false);
            }} className="text-zinc-500 text-sm">
              No thanks, I'll miss out
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* TRADE CONFIRMATION MODAL */}
      <Dialog open={showTradeModal} onOpenChange={setShowTradeModal}>
        <DialogContent className="bg-[#121212] border-zinc-800 max-w-md" data-testid="trade-modal">
          <DialogHeader>
            <DialogTitle className="text-xl flex items-center gap-2">
              {selectedSignal?.signal === 'BUY' ? (
                <ArrowUpRight className="w-6 h-6 text-[#00FF94]" />
              ) : (
                <ArrowDownRight className="w-6 h-6 text-red-400" />
              )}
              {selectedSignal?.signal} {selectedSignal?.symbol}
            </DialogTitle>
            <DialogDescription>
              Execute trade based on AI signal
            </DialogDescription>
          </DialogHeader>
          
          {selectedSignal && (
            <div className="space-y-4 py-4">
              {/* Mode Indicator */}
              <div className={`p-3 rounded-lg ${tradingMode === 'live' ? 'bg-red-500/10 border border-red-500/30' : 'bg-[#7B61FF]/10 border border-[#7B61FF]/30'}`}>
                <div className="flex items-center gap-2">
                  {tradingMode === 'live' ? (
                    <>
                      <AlertTriangle className="w-4 h-4 text-red-400" />
                      <span className="text-red-400 font-medium">LIVE TRADING - Real funds will be used</span>
                    </>
                  ) : (
                    <>
                      <Activity className="w-4 h-4 text-[#7B61FF]" />
                      <span className="text-[#7B61FF] font-medium">Paper Trading Mode</span>
                    </>
                  )}
                </div>
              </div>

              {/* Signal Details */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-zinc-400">Asset</span>
                  <span className="font-bold text-lg">{selectedSignal.symbol}</span>
                </div>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-zinc-400">Current Price</span>
                  <span className="font-mono">${selectedSignal.price?.toLocaleString()}</span>
                </div>
                <div className="flex justify-between items-center mb-3">
                  <span className="text-zinc-400">Signal</span>
                  <span className={`font-bold ${selectedSignal.signal === 'BUY' ? 'text-[#00FF94]' : 'text-red-400'}`}>
                    {selectedSignal.signal}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-zinc-400">Confidence</span>
                  <span className="font-mono">{selectedSignal.confidence}%</span>
                </div>
              </div>

              {/* Trade Amount */}
              <div>
                <label className="text-sm text-zinc-400 block mb-2">Trade Amount (USD)</label>
                <div className="flex gap-2">
                  {[50, 100, 250, 500].map(amt => (
                    <button
                      key={amt}
                      onClick={() => setTradeAmount(amt)}
                      className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                        tradeAmount === amt 
                          ? 'bg-[#7B61FF] text-white' 
                          : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
                      }`}
                    >
                      ${amt}
                    </button>
                  ))}
                </div>
                <input
                  type="number"
                  value={tradeAmount}
                  onChange={(e) => setTradeAmount(Number(e.target.value))}
                  className="w-full mt-2 p-3 rounded-lg bg-[#050505] border border-zinc-800 text-white font-mono"
                  placeholder="Custom amount"
                />
              </div>

              {/* Estimated Output */}
              <div className="p-3 rounded-lg bg-zinc-900 border border-zinc-800">
                <div className="flex justify-between text-sm">
                  <span className="text-zinc-500">Estimated {selectedSignal.symbol}</span>
                  <span className="font-mono">{(tradeAmount / selectedSignal.price).toFixed(6)} {selectedSignal.symbol}</span>
                </div>
                <div className="flex justify-between text-sm mt-1">
                  <span className="text-zinc-500">Est. Fee</span>
                  <span className="font-mono text-zinc-400">~$5-10</span>
                </div>
              </div>

              {/* Portfolio Quick View */}
              {portfolio && (
                <div className="p-3 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
                  <div className="text-xs text-zinc-500 mb-1">Your Portfolio</div>
                  <div className="flex justify-between text-sm">
                    <span>Paper Balance:</span>
                    <span className="font-mono text-[#00FF94]">${portfolio.total_invested?.toLocaleString() || '10,000'}</span>
                  </div>
                </div>
              )}

              {/* Stop-Loss / Take-Profit Section */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <p className="text-sm font-medium mb-3 flex items-center gap-2">
                  <Shield className="w-4 h-4 text-[#7B61FF]" />
                  Risk Management
                </p>
                
                {/* Stop-Loss */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={enableSL}
                      onCheckedChange={setEnableSL}
                      data-testid="enable-sl-toggle"
                    />
                    <span className="text-sm text-red-400">Stop-Loss</span>
                  </div>
                  {enableSL && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-zinc-500">$</span>
                      <Input
                        type="number"
                        value={stopLossPrice}
                        onChange={(e) => setStopLossPrice(Number(e.target.value))}
                        className="w-28 bg-[#121212] border-zinc-700 text-sm"
                        step="0.01"
                        data-testid="sl-price-input"
                      />
                    </div>
                  )}
                </div>
                
                {/* Take-Profit */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={enableTP}
                      onCheckedChange={setEnableTP}
                      data-testid="enable-tp-toggle"
                    />
                    <span className="text-sm text-[#00FF94]">Take-Profit</span>
                  </div>
                  {enableTP && (
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-zinc-500">$</span>
                      <Input
                        type="number"
                        value={takeProfitPrice}
                        onChange={(e) => setTakeProfitPrice(Number(e.target.value))}
                        className="w-28 bg-[#121212] border-zinc-700 text-sm"
                        step="0.01"
                        data-testid="tp-price-input"
                      />
                    </div>
                  )}
                </div>

                {(enableSL || enableTP) && (
                  <div className="mt-3 pt-3 border-t border-zinc-800 text-xs text-zinc-500">
                    {enableSL && (
                      <p>SL triggers at ${stopLossPrice.toLocaleString()} ({((stopLossPrice / selectedSignal.price - 1) * 100).toFixed(1)}%)</p>
                    )}
                    {enableTP && (
                      <p>TP triggers at ${takeProfitPrice.toLocaleString()} ({((takeProfitPrice / selectedSignal.price - 1) * 100).toFixed(1)}%)</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          <DialogFooter className="flex-col gap-2">
            <Button
              onClick={executeTrade}
              disabled={isExecutingTrade || tradeAmount <= 0}
              className={`w-full py-6 rounded-full font-bold text-lg ${
                selectedSignal?.signal === 'BUY'
                  ? 'bg-[#00FF94] hover:bg-[#00FF94]/90 text-black'
                  : 'bg-red-500 hover:bg-red-500/90 text-white'
              }`}
              data-testid="confirm-trade-btn"
            >
              {isExecutingTrade ? (
                <>
                  <RefreshCw className="w-5 h-5 mr-2 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <PlayCircle className="w-5 h-5 mr-2" />
                  Confirm {selectedSignal?.signal} ${tradeAmount}
                </>
              )}
            </Button>
            <Button variant="ghost" onClick={() => setShowTradeModal(false)} className="text-zinc-500">
              Cancel
            </Button>
          </DialogFooter>
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

// Conversion Analytics Page - A/B Testing Dashboard
const ConversionAnalyticsPage = () => {
  const [summary, setSummary] = useState(null);
  const [daily, setDaily] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [featureDetail, setFeatureDetail] = useState(null);

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/analytics/summary?days=30`),
      axios.get(`${API}/analytics/daily?days=14`)
    ]).then(([summaryRes, dailyRes]) => {
      setSummary(summaryRes.data);
      setDaily(dailyRes.data.daily || []);
    }).catch(console.error).finally(() => setLoading(false));
  }, []);

  const loadFeatureDetail = async (feature) => {
    setSelectedFeature(feature);
    try {
      const res = await axios.get(`${API}/analytics/feature/${feature}?days=30`);
      setFeatureDetail(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  if (loading) return <div className="min-h-screen pt-24 px-4 flex items-center justify-center"><RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" /></div>;

  const featureColors = {
    'exit_popup': '#FF6B6B',
    'timed_popup': '#7B61FF',
    'unlock_live_btn': '#00FF94',
    'upgrade_cta': '#FFB800',
    'missed_trade': '#FF8C42',
    'social_proof': '#4ECDC4',
    'dashboard': '#A78BFA'
  };

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="conversion-analytics-title">
            Conversion Analytics
          </h1>
          <p className="text-zinc-400 mt-1">A/B Testing & Feature Performance Dashboard</p>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Total Views</p>
              <p className="text-3xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">{summary?.total_views || 0}</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Conversions</p>
              <p className="text-3xl font-bold text-[#00FF94] font-['JetBrains_Mono']">{summary?.total_conversions || 0}</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Conversion Rate</p>
              <p className="text-3xl font-bold text-[#FFB800] font-['JetBrains_Mono']">{summary?.overall_conversion_rate || 0}%</p>
            </CardContent>
          </Card>
          <Card className="glass-card">
            <CardContent className="p-6 text-center">
              <p className="text-sm text-zinc-500 mb-2">Top Performer</p>
              <p className="text-xl font-bold text-white font-['JetBrains_Mono']">{summary?.top_performer || 'N/A'}</p>
            </CardContent>
          </Card>
        </div>

        {/* Feature Performance Table */}
        <Card className="glass-card mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-[#7B61FF]" />
              Feature Performance (Last 30 Days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summary?.features?.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-zinc-800">
                      <th className="text-left p-4 text-zinc-500">Feature</th>
                      <th className="text-right p-4 text-zinc-500">Views</th>
                      <th className="text-right p-4 text-zinc-500">Clicks</th>
                      <th className="text-right p-4 text-zinc-500">Conversions</th>
                      <th className="text-right p-4 text-zinc-500">Click Rate</th>
                      <th className="text-right p-4 text-zinc-500">Conv. Rate</th>
                      <th className="text-right p-4 text-zinc-500">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {summary.features.map((feature, index) => (
                      <tr key={index} className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors">
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <div 
                              className="w-3 h-3 rounded-full" 
                              style={{ backgroundColor: featureColors[feature.feature] || '#7B61FF' }}
                            />
                            <span className="font-medium">{feature.feature.replace(/_/g, ' ')}</span>
                          </div>
                        </td>
                        <td className="p-4 text-right font-mono text-zinc-400">{feature.views}</td>
                        <td className="p-4 text-right font-mono text-zinc-400">{feature.clicks}</td>
                        <td className="p-4 text-right font-mono text-[#00FF94]">{feature.conversions}</td>
                        <td className="p-4 text-right font-mono">{feature.click_rate}%</td>
                        <td className="p-4 text-right">
                          <span className={`font-mono font-bold ${feature.conversion_rate > 5 ? 'text-[#00FF94]' : feature.conversion_rate > 2 ? 'text-[#FFB800]' : 'text-zinc-400'}`}>
                            {feature.conversion_rate}%
                          </span>
                        </td>
                        <td className="p-4 text-right">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => loadFeatureDetail(feature.feature)}
                            className="border-zinc-700"
                          >
                            Details
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-zinc-500">
                <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No analytics data yet</p>
                <p className="text-sm mt-2">Data will appear as users interact with conversion features</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Daily Chart */}
        {daily.length > 0 && (
          <Card className="glass-card mb-8">
            <CardHeader>
              <CardTitle>Daily Conversions (Last 14 Days)</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={daily}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#27272A" />
                    <XAxis dataKey="date" stroke="#71717A" fontSize={12} />
                    <YAxis stroke="#71717A" />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#121212', border: '1px solid #27272A', borderRadius: '8px' }} 
                    />
                    <Bar dataKey="views" name="Views" fill="#7B61FF" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="conversions" name="Conversions" fill="#00FF94" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Feature Detail Modal */}
        <Dialog open={!!selectedFeature} onOpenChange={() => setSelectedFeature(null)}>
          <DialogContent className="bg-[#121212] border-zinc-800 max-w-lg">
            <DialogHeader>
              <DialogTitle className="capitalize">{selectedFeature?.replace(/_/g, ' ')} - Details</DialogTitle>
            </DialogHeader>
            {featureDetail && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Views</p>
                    <p className="text-2xl font-bold font-mono">{featureDetail.events?.view || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Clicks</p>
                    <p className="text-2xl font-bold font-mono">{featureDetail.events?.click || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Conversions</p>
                    <p className="text-2xl font-bold font-mono text-[#00FF94]">{featureDetail.events?.conversion || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Dismisses</p>
                    <p className="text-2xl font-bold font-mono text-red-400">{featureDetail.events?.dismiss || 0}</p>
                  </div>
                </div>
                <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                  <p className="text-sm text-zinc-500 mb-2">Rates</p>
                  <div className="flex justify-between">
                    <span>Click Rate: <span className="font-mono font-bold">{featureDetail.click_rate}%</span></span>
                    <span>Conversion: <span className="font-mono font-bold text-[#00FF94]">{featureDetail.conversion_rate}%</span></span>
                  </div>
                </div>
                {featureDetail.peak_hour !== null && (
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Peak Activity Hour</p>
                    <p className="text-lg font-bold">{featureDetail.peak_hour}:00</p>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

// Admin Page - Comprehensive System Admin Dashboard
const AdminPage = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [adminKey, setAdminKey] = useState(localStorage.getItem('adminKey') || '');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // Overview state
  const [dashboardData, setDashboardData] = useState(null);
  const [systemStats, setSystemStats] = useState(null);
  
  // Users state
  const [users, setUsers] = useState([]);
  const [userSearch, setUserSearch] = useState('');
  const [userPlanFilter, setUserPlanFilter] = useState('all');
  const [userStatusFilter, setUserStatusFilter] = useState('all');
  const [usersPage, setUsersPage] = useState(1);
  const [usersTotal, setUsersTotal] = useState(0);
  const [selectedUser, setSelectedUser] = useState(null);
  const [userDetailOpen, setUserDetailOpen] = useState(false);
  
  // Subscriptions state
  const [subscriptions, setSubscriptions] = useState([]);
  const [subsPage, setSubsPage] = useState(1);
  const [subsTotal, setSubsTotal] = useState(0);
  
  // Logs state
  const [logs, setLogs] = useState([]);
  const [logCategory, setLogCategory] = useState('all');
  const [logSeverity, setLogSeverity] = useState('all');
  const [logsPage, setLogsPage] = useState(1);
  const [logsTotal, setLogsTotal] = useState(0);
  const [auditLogs, setAuditLogs] = useState([]);
  
  // Features state
  const [features, setFeatures] = useState([]);
  const [featureCategories, setFeatureCategories] = useState({});
  
  // Legacy fund stats for overview
  const [fundStats, setFundStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [agents, setAgents] = useState([]);
  const [riskConfig, setRiskConfig] = useState(null);

  const ADMIN_API = `${API}/admin`;

  // Admin authentication
  const authenticateAdmin = async () => {
    if (!adminKey) {
      toast.error('Please enter admin key');
      return;
    }
    try {
      const res = await axios.get(`${ADMIN_API}/dashboard?admin_key=${adminKey}`);
      if (res.data) {
        setIsAuthenticated(true);
        localStorage.setItem('adminKey', adminKey);
        toast.success('Admin access granted');
        loadAllData();
      }
    } catch (error) {
      toast.error('Invalid admin key');
      setIsAuthenticated(false);
    }
  };

  // Load all data
  const loadAllData = async () => {
    setLoading(true);
    try {
      await Promise.all([
        loadDashboard(),
        loadSystemStats(),
        loadUsers(),
        loadSubscriptions(),
        loadLogs(),
        loadFeatures(),
        loadLegacyData()
      ]);
    } catch (error) {
      console.error('Error loading admin data:', error);
    }
    setLoading(false);
  };

  const loadDashboard = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/dashboard?admin_key=${adminKey}`);
      setDashboardData(res.data);
    } catch (error) { console.error('Dashboard load error:', error); }
  };

  const loadSystemStats = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/system/stats?admin_key=${adminKey}`);
      setSystemStats(res.data);
    } catch (error) { console.error('System stats load error:', error); }
  };

  const loadUsers = async () => {
    try {
      const params = new URLSearchParams({ admin_key: adminKey, page: usersPage, limit: 20 });
      if (userSearch) params.append('search', userSearch);
      if (userPlanFilter !== 'all') params.append('plan', userPlanFilter);
      if (userStatusFilter !== 'all') params.append('status', userStatusFilter);
      const res = await axios.get(`${ADMIN_API}/users?${params}`);
      setUsers(res.data.users);
      setUsersTotal(res.data.total);
    } catch (error) { console.error('Users load error:', error); }
  };

  const loadSubscriptions = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/subscriptions?admin_key=${adminKey}&page=${subsPage}`);
      setSubscriptions(res.data.subscriptions);
      setSubsTotal(res.data.total);
    } catch (error) { console.error('Subscriptions load error:', error); }
  };

  const loadLogs = async () => {
    try {
      const params = new URLSearchParams({ admin_key: adminKey, page: logsPage, limit: 50 });
      if (logCategory !== 'all') params.append('category', logCategory);
      if (logSeverity !== 'all') params.append('severity', logSeverity);
      const res = await axios.get(`${ADMIN_API}/logs?${params}`);
      setLogs(res.data.logs);
      setLogsTotal(res.data.total);
      
      // Load audit logs
      const auditRes = await axios.get(`${ADMIN_API}/logs/audit?admin_key=${adminKey}&limit=20`);
      setAuditLogs(auditRes.data.logs);
    } catch (error) { console.error('Logs load error:', error); }
  };

  const loadFeatures = async () => {
    try {
      const res = await axios.get(`${ADMIN_API}/features?admin_key=${adminKey}`);
      setFeatures(res.data.features);
      setFeatureCategories(res.data.categories);
    } catch (error) { console.error('Features load error:', error); }
  };

  const loadLegacyData = async () => {
    try {
      const [statsRes, alertsRes, agentsRes, configRes] = await Promise.all([
        axios.get(`${API}/fund/stats`),
        axios.get(`${API}/risk/alerts`),
        axios.get(`${API}/agents`),
        axios.get(`${API}/risk/config`)
      ]);
      setFundStats(statsRes.data);
      setAlerts(alertsRes.data);
      setAgents(agentsRes.data);
      setRiskConfig(configRes.data);
    } catch (error) { console.error('Legacy data load error:', error); }
  };

  // User actions
  const handleUserAction = async (userId, action, reason = '') => {
    try {
      await axios.post(`${ADMIN_API}/users/action?admin_key=${adminKey}`, {
        user_id: userId,
        action: action,
        reason: reason
      });
      toast.success(`Action '${action}' completed`);
      loadUsers();
      loadDashboard();
    } catch (error) {
      toast.error(`Action failed: ${error.response?.data?.detail || error.message}`);
    }
  };

  const viewUserDetails = async (userId) => {
    try {
      const res = await axios.get(`${ADMIN_API}/users/${userId}?admin_key=${adminKey}`);
      setSelectedUser(res.data);
      setUserDetailOpen(true);
    } catch (error) {
      toast.error('Failed to load user details');
    }
  };

  // Subscription actions
  const syncSubscription = async (userId) => {
    try {
      await axios.post(`${ADMIN_API}/subscriptions/sync/${userId}?admin_key=${adminKey}`);
      toast.success('Subscription synced');
      loadSubscriptions();
    } catch (error) {
      toast.error('Sync failed');
    }
  };

  const overrideSubscription = async (userId, plan, reason) => {
    try {
      await axios.post(`${ADMIN_API}/subscriptions/override?admin_key=${adminKey}`, {
        user_id: userId,
        plan: plan,
        reason: reason
      });
      toast.success(`Subscription set to ${plan}`);
      loadSubscriptions();
      loadUsers();
    } catch (error) {
      toast.error('Override failed');
    }
  };

  // Feature toggle
  const toggleFeature = async (featureId, enabled) => {
    try {
      await axios.put(`${ADMIN_API}/features?admin_key=${adminKey}`, {
        feature_id: featureId,
        enabled: enabled
      });
      toast.success(`Feature ${enabled ? 'enabled' : 'disabled'}`);
      loadFeatures();
    } catch (error) {
      toast.error('Toggle failed');
    }
  };

  // System tools
  const runSystemTool = async (tool) => {
    try {
      const res = await axios.post(`${ADMIN_API}/system/tools?admin_key=${adminKey}`, { tool });
      if (res.data.success) {
        toast.success(res.data.message);
      } else {
        toast.error(res.data.message);
      }
      loadSystemStats();
    } catch (error) {
      toast.error('Tool execution failed');
    }
  };

  // Effects
  useEffect(() => {
    if (adminKey && localStorage.getItem('adminKey')) {
      authenticateAdmin();
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loadUsers();
    }
  }, [userSearch, userPlanFilter, userStatusFilter, usersPage, isAuthenticated]);

  useEffect(() => {
    if (isAuthenticated) {
      loadLogs();
    }
  }, [logCategory, logSeverity, logsPage, isAuthenticated]);

  // Auth screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen pt-24 px-4 flex items-center justify-center">
        <Card className="glass-card w-full max-w-md">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="w-6 h-6 text-[#7B61FF]" />
              Admin Authentication
            </CardTitle>
            <CardDescription>Enter your admin key to access the dashboard</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Input
              type="password"
              placeholder="Admin Key"
              value={adminKey}
              onChange={(e) => setAdminKey(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && authenticateAdmin()}
              className="bg-[#050505] border-zinc-800"
              data-testid="admin-key-input"
            />
            <Button onClick={authenticateAdmin} className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/80" data-testid="admin-login-btn">
              Access Dashboard
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

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
        {/* Header with Brand Identity */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-6">
            <BrandLockup size="large" showSubtitle={true} />
            <div className="h-10 w-px bg-zinc-800" />
            <div>
              <h1 className="text-2xl font-bold font-['Outfit']" data-testid="admin-title">
                System Admin
              </h1>
              <p className="text-zinc-500 text-sm">Administrative Console</p>
            </div>
          </div>
          <Button variant="outline" onClick={() => { setIsAuthenticated(false); localStorage.removeItem('adminKey'); }} className="border-zinc-700">
            <LogOut className="w-4 h-4 mr-2" /> Logout
          </Button>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-[#121212] border border-zinc-800 p-1 flex-wrap h-auto">
            <TabsTrigger value="overview" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-overview">Overview</TabsTrigger>
            <TabsTrigger value="users" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-users">Users</TabsTrigger>
            <TabsTrigger value="subscriptions" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-subscriptions">Subscriptions</TabsTrigger>
            <TabsTrigger value="logs" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-logs">Logs</TabsTrigger>
            <TabsTrigger value="features" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-features">Features</TabsTrigger>
            <TabsTrigger value="tools" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-tools">System Tools</TabsTrigger>
            <TabsTrigger value="security" className="data-[state=active]:bg-[#7B61FF]" data-testid="tab-security">Security</TabsTrigger>
          </TabsList>

          {/* OVERVIEW TAB */}
          <TabsContent value="overview" className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="glass-card" data-testid="stat-total-users">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Total Users</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#00FF94]">{systemStats?.users?.total || 0}</p>
                  <p className="text-xs text-zinc-500 mt-1">+{systemStats?.users?.new_24h || 0} today</p>
                </CardContent>
              </Card>
              <Card className="glass-card" data-testid="stat-pro-users">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Pro Users</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#7B61FF]">{systemStats?.users?.pro || 0}</p>
                  <p className="text-xs text-zinc-500 mt-1">{systemStats?.users?.elite || 0} Elite</p>
                </CardContent>
              </Card>
              <Card className="glass-card" data-testid="stat-active-subs">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Active Subscriptions</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">{systemStats?.subscriptions?.active || 0}</p>
                </CardContent>
              </Card>
              <Card className="glass-card" data-testid="stat-signals">
                <CardContent className="p-6">
                  <p className="text-sm text-zinc-500 mb-1">Signals (24h)</p>
                  <p className="text-2xl font-bold font-['JetBrains_Mono']">{systemStats?.signals?.last_24h || 0}</p>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <Users className="w-5 h-5 text-[#7B61FF]" />
                    Recent Signups
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboardData?.recent_signups?.map((user, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#050505]">
                        <span className="text-sm truncate">{user.email}</span>
                        <div className="flex items-center gap-2">
                          {user.is_pro && <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-xs">PRO</Badge>}
                          <span className="text-xs text-zinc-500">{new Date(user.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <DollarSign className="w-5 h-5 text-[#00FF94]" />
                    Recent Payments
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {dashboardData?.recent_payments?.map((payment, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#050505]">
                        <span className="text-sm truncate">{payment.user_email || payment.session_id?.slice(0, 20)}</span>
                        <div className="flex items-center gap-2">
                          <Badge className="bg-[#00FF94]/20 text-[#00FF94] text-xs">${payment.amount}</Badge>
                          <span className="text-xs text-zinc-500">{payment.package_id}</span>
                        </div>
                      </div>
                    ))}
                    {(!dashboardData?.recent_payments || dashboardData.recent_payments.length === 0) && (
                      <p className="text-zinc-500 text-center py-4">No recent payments</p>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Legacy sections */}
            {riskConfig && (
              <Card className="glass-card">
                <CardHeader><CardTitle className="flex items-center gap-2"><Gauge className="w-5 h-5 text-[#FF6B6B]" />Risk Configuration</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-4 gap-4">
                    <div><label className="text-sm text-zinc-400 block mb-1">Max Drawdown %</label><p className="text-lg font-mono">{riskConfig.max_drawdown}%</p></div>
                    <div><label className="text-sm text-zinc-400 block mb-1">Max Position Size %</label><p className="text-lg font-mono">{riskConfig.max_position_size}%</p></div>
                    <div><label className="text-sm text-zinc-400 block mb-1">Max Daily Loss %</label><p className="text-lg font-mono">{riskConfig.max_daily_loss}%</p></div>
                    <div><label className="text-sm text-zinc-400 block mb-1">Stop Loss %</label><p className="text-lg font-mono">{riskConfig.stop_loss}%</p></div>
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* USERS TAB */}
          <TabsContent value="users" className="space-y-6">
            {/* Filters */}
            <Card className="glass-card">
              <CardContent className="p-4">
                <div className="flex flex-wrap gap-4">
                  <Input
                    placeholder="Search users..."
                    value={userSearch}
                    onChange={(e) => setUserSearch(e.target.value)}
                    className="bg-[#050505] border-zinc-800 max-w-xs"
                    data-testid="user-search"
                  />
                  <Select value={userPlanFilter} onValueChange={setUserPlanFilter}>
                    <SelectTrigger className="w-32 bg-[#050505] border-zinc-800"><SelectValue placeholder="Plan" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Plans</SelectItem>
                      <SelectItem value="free">Free</SelectItem>
                      <SelectItem value="pro">Pro</SelectItem>
                      <SelectItem value="elite">Elite</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={userStatusFilter} onValueChange={setUserStatusFilter}>
                    <SelectTrigger className="w-32 bg-[#050505] border-zinc-800"><SelectValue placeholder="Status" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                      <SelectItem value="verified">Verified</SelectItem>
                      <SelectItem value="unverified">Unverified</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="outline" onClick={loadUsers} className="border-zinc-700">
                    <RefreshCw className="w-4 h-4 mr-2" /> Refresh
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Users Table */}
            <Card className="glass-card">
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-zinc-800">
                        <th className="text-left p-4 text-zinc-500 text-sm">Email</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Name</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Plan</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Status</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Created</th>
                        <th className="text-right p-4 text-zinc-500 text-sm">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id} className="border-b border-zinc-800/50 hover:bg-[#050505]/50" data-testid={`user-row-${user.id}`}>
                          <td className="p-4 text-sm">{user.email}</td>
                          <td className="p-4 text-sm text-zinc-400">{user.name || '-'}</td>
                          <td className="p-4">
                            <Badge className={user.is_elite ? 'bg-[#FFB800]/20 text-[#FFB800]' : user.is_pro ? 'bg-[#7B61FF]/20 text-[#7B61FF]' : 'bg-zinc-700 text-zinc-400'}>
                              {user.is_elite ? 'Elite' : user.is_pro ? 'Pro' : 'Free'}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <Badge className={user.is_verified ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                              {user.is_verified ? 'Verified' : 'Unverified'}
                            </Badge>
                          </td>
                          <td className="p-4 text-sm text-zinc-400">{new Date(user.created_at).toLocaleDateString()}</td>
                          <td className="p-4 text-right">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="sm"><Settings className="w-4 h-4" /></Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end" className="bg-[#121212] border-zinc-800">
                                <DropdownMenuItem onClick={() => viewUserDetails(user.id)}>View Details</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'set_free')}>Set Free</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'set_pro')}>Set Pro</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'set_elite')}>Set Elite</DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, user.is_active === false ? 'activate' : 'deactivate')}>
                                  {user.is_active === false ? 'Activate' : 'Deactivate'}
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleUserAction(user.id, 'delete')} className="text-red-400">Delete User</DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="p-4 border-t border-zinc-800 flex items-center justify-between">
                  <p className="text-sm text-zinc-500">Total: {usersTotal} users</p>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => setUsersPage(p => Math.max(1, p - 1))} disabled={usersPage === 1}>Prev</Button>
                    <Button variant="outline" size="sm" onClick={() => setUsersPage(p => p + 1)} disabled={users.length < 20}>Next</Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* SUBSCRIPTIONS TAB */}
          <TabsContent value="subscriptions" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <DollarSign className="w-5 h-5 text-[#00FF94]" />
                  Subscription Management
                </CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-zinc-800">
                        <th className="text-left p-4 text-zinc-500 text-sm">User</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Plan</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Status</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Expires</th>
                        <th className="text-left p-4 text-zinc-500 text-sm">Override</th>
                        <th className="text-right p-4 text-zinc-500 text-sm">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {subscriptions.map((sub, i) => (
                        <tr key={i} className="border-b border-zinc-800/50">
                          <td className="p-4 text-sm">{sub.user_email}</td>
                          <td className="p-4">
                            <Badge className={sub.plan === 'elite' ? 'bg-[#FFB800]/20 text-[#FFB800]' : 'bg-[#7B61FF]/20 text-[#7B61FF]'}>
                              {sub.plan}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <Badge className={sub.status === 'active' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                              {sub.status}
                            </Badge>
                          </td>
                          <td className="p-4 text-sm text-zinc-400">
                            {sub.expires_at ? new Date(sub.expires_at).toLocaleDateString() : '-'}
                          </td>
                          <td className="p-4">
                            {sub.admin_override && <Badge className="bg-yellow-500/20 text-yellow-400">Manual</Badge>}
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex gap-2 justify-end">
                              <Button size="sm" variant="outline" onClick={() => syncSubscription(sub.user_id)} className="border-zinc-700">
                                Sync
                              </Button>
                              <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                  <Button size="sm" variant="outline" className="border-zinc-700">Override</Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align="end" className="bg-[#121212] border-zinc-800">
                                  <DropdownMenuItem onClick={() => overrideSubscription(sub.user_id, 'free', 'Admin override')}>Set Free</DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => overrideSubscription(sub.user_id, 'pro', 'Admin override')}>Set Pro</DropdownMenuItem>
                                  <DropdownMenuItem onClick={() => overrideSubscription(sub.user_id, 'elite', 'Admin override')}>Set Elite</DropdownMenuItem>
                                </DropdownMenuContent>
                              </DropdownMenu>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* LOGS TAB */}
          <TabsContent value="logs" className="space-y-6">
            <div className="flex gap-4 mb-4">
              <Select value={logCategory} onValueChange={setLogCategory}>
                <SelectTrigger className="w-40 bg-[#050505] border-zinc-800"><SelectValue placeholder="Category" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="backend">Backend</SelectItem>
                  <SelectItem value="webhook">Webhook</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                  <SelectItem value="auth">Auth</SelectItem>
                  <SelectItem value="payment">Payment</SelectItem>
                </SelectContent>
              </Select>
              <Select value={logSeverity} onValueChange={setLogSeverity}>
                <SelectTrigger className="w-32 bg-[#050505] border-zinc-800"><SelectValue placeholder="Severity" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                  <SelectItem value="warning">Warning</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ScrollText className="w-5 h-5 text-[#7B61FF]" />
                  System Logs
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[400px]">
                  {logs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No logs found</p>
                  ) : (
                    <div className="space-y-2 font-mono text-sm">
                      {logs.map((log, i) => (
                        <div key={i} className={`p-2 rounded ${log.severity === 'error' ? 'bg-red-500/10' : log.severity === 'warning' ? 'bg-yellow-500/10' : 'bg-[#050505]'}`}>
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs text-zinc-500">{new Date(log.timestamp).toLocaleString()}</span>
                            <Badge className={log.severity === 'error' ? 'bg-red-500/20 text-red-400' : log.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-zinc-700 text-zinc-400'}>
                              {log.severity || 'info'}
                            </Badge>
                            <Badge className="bg-zinc-800 text-zinc-400">{log.category}</Badge>
                          </div>
                          <p className="text-zinc-300">{log.message}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>

            {/* Audit Logs */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-[#FFB800]" />
                  Admin Audit Log
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {auditLogs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No audit logs</p>
                  ) : (
                    <div className="space-y-2">
                      {auditLogs.map((log, i) => (
                        <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm font-medium">{log.action}</span>
                            <span className="text-xs text-zinc-500">{new Date(log.timestamp).toLocaleString()}</span>
                          </div>
                          <p className="text-xs text-zinc-400">By: {log.admin_email}</p>
                          {log.target_id && <p className="text-xs text-zinc-500">Target: {log.target_type}/{log.target_id}</p>}
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>

          {/* FEATURES TAB */}
          <TabsContent value="features" className="space-y-6">
            {Object.entries(featureCategories).map(([category, categoryFeatures]) => (
              <Card key={category} className="glass-card">
                <CardHeader>
                  <CardTitle className="capitalize">{category} Features</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {categoryFeatures.map((feature) => (
                      <div key={feature.feature_id} className="flex items-center justify-between p-3 rounded-lg bg-[#050505] border border-zinc-800">
                        <div>
                          <p className="font-medium">{feature.name}</p>
                          <p className="text-sm text-zinc-500">{feature.description}</p>
                        </div>
                        <Switch
                          checked={feature.enabled}
                          onCheckedChange={(checked) => toggleFeature(feature.feature_id, checked)}
                          data-testid={`toggle-${feature.feature_id}`}
                        />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </TabsContent>

          {/* SYSTEM TOOLS TAB */}
          <TabsContent value="tools" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="w-5 h-5 text-[#7B61FF]" />
                    Maintenance Tools
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <Button onClick={() => runSystemTool('clear_cache')} variant="outline" className="w-full justify-start border-zinc-700">
                    <RefreshCw className="w-4 h-4 mr-2" /> Clear Cache
                  </Button>
                  <Button onClick={() => runSystemTool('refresh_data')} variant="outline" className="w-full justify-start border-zinc-700">
                    <Activity className="w-4 h-4 mr-2" /> Refresh Data
                  </Button>
                  <Button onClick={() => runSystemTool('rebuild_indexes')} variant="outline" className="w-full justify-start border-zinc-700">
                    <BarChart3 className="w-4 h-4 mr-2" /> Rebuild Indexes
                  </Button>
                  <Button onClick={() => runSystemTool('cleanup_expired_tokens')} variant="outline" className="w-full justify-start border-zinc-700">
                    <Clock className="w-4 h-4 mr-2" /> Cleanup Expired Tokens
                  </Button>
                  <Button onClick={() => runSystemTool('cleanup_old_logs')} variant="outline" className="w-full justify-start border-zinc-700">
                    <ScrollText className="w-4 h-4 mr-2" /> Cleanup Old Logs
                  </Button>
                  <Button onClick={() => runSystemTool('verify_subscriptions')} variant="outline" className="w-full justify-start border-zinc-700">
                    <Check className="w-4 h-4 mr-2" /> Verify Subscriptions
                  </Button>
                </CardContent>
              </Card>

              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="w-5 h-5 text-[#00FF94]" />
                    System Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Database Collections</p>
                    <p className="font-mono">{systemStats?.system?.database_collections?.length || 0}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Last Signal Generation</p>
                    <p className="font-mono text-sm">{systemStats?.system?.last_signal_generation ? new Date(systemStats.system.last_signal_generation).toLocaleString() : 'N/A'}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Total Signals</p>
                    <p className="font-mono">{systemStats?.signals?.total || 0}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500">Total Trades</p>
                    <p className="font-mono">{systemStats?.trades?.total || 0}</p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* SECURITY TAB */}
          <TabsContent value="security" className="space-y-6">
            <Card className="glass-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="w-5 h-5 text-[#FF6B6B]" />
                  Security Overview
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-1">Admin Auth</p>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#00FF94]" />
                      <span className="text-[#00FF94]">Protected</span>
                    </div>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-1">Audit Logging</p>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#00FF94]" />
                      <span className="text-[#00FF94]">Active</span>
                    </div>
                  </div>
                  <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-1">Rate Limiting</p>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full bg-[#00FF94]" />
                      <span className="text-[#00FF94]">Enabled</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                  <p className="font-medium mb-2">Admin Access Requirements</p>
                  <ul className="text-sm text-zinc-400 space-y-1">
                    <li>• All admin routes require admin_key parameter</li>
                    <li>• All admin actions are logged to audit trail</li>
                    <li>• User deletion requires confirmation</li>
                    <li>• Subscription overrides are tracked with reason</li>
                  </ul>
                </div>

                <div className="p-4 rounded-lg bg-yellow-500/10 border border-yellow-500/30">
                  <p className="font-medium text-yellow-400 mb-2">Security Recommendation</p>
                  <p className="text-sm text-zinc-400">For production, implement proper JWT-based admin authentication with role-based access control (RBAC).</p>
                </div>
              </CardContent>
            </Card>

            {/* Recent Audit Activity */}
            <Card className="glass-card">
              <CardHeader>
                <CardTitle>Recent Admin Activity</CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[300px]">
                  {auditLogs.length === 0 ? (
                    <p className="text-zinc-500 text-center py-8">No recent admin activity</p>
                  ) : (
                    <div className="space-y-2">
                      {auditLogs.slice(0, 10).map((log, i) => (
                        <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[#050505]">
                          <div>
                            <p className="text-sm font-medium">{log.action}</p>
                            <p className="text-xs text-zinc-500">{log.admin_email} • {log.target_type}</p>
                          </div>
                          <span className="text-xs text-zinc-500">{new Date(log.timestamp).toLocaleString()}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* User Detail Dialog */}
        <Dialog open={userDetailOpen} onOpenChange={setUserDetailOpen}>
          <DialogContent className="bg-[#121212] border-zinc-800 max-w-2xl">
            <DialogHeader>
              <DialogTitle>User Details</DialogTitle>
            </DialogHeader>
            {selectedUser && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div><p className="text-sm text-zinc-500">Email</p><p>{selectedUser.user?.email}</p></div>
                  <div><p className="text-sm text-zinc-500">Name</p><p>{selectedUser.user?.name || '-'}</p></div>
                  <div><p className="text-sm text-zinc-500">ID</p><p className="font-mono text-sm">{selectedUser.user?.id}</p></div>
                  <div><p className="text-sm text-zinc-500">Created</p><p>{new Date(selectedUser.user?.created_at).toLocaleString()}</p></div>
                </div>
                <div className="flex gap-2">
                  <Badge className={selectedUser.user?.is_verified ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                    {selectedUser.user?.is_verified ? 'Verified' : 'Unverified'}
                  </Badge>
                  <Badge className={selectedUser.user?.is_elite ? 'bg-[#FFB800]/20 text-[#FFB800]' : selectedUser.user?.is_pro ? 'bg-[#7B61FF]/20 text-[#7B61FF]' : 'bg-zinc-700 text-zinc-400'}>
                    {selectedUser.user?.is_elite ? 'Elite' : selectedUser.user?.is_pro ? 'Pro' : 'Free'}
                  </Badge>
                </div>
                {selectedUser.subscription && (
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm text-zinc-500 mb-2">Subscription</p>
                    <p>Plan: {selectedUser.subscription.plan}</p>
                    <p>Status: {selectedUser.subscription.status}</p>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Smart Contract Section */}
        <div className="mt-8">
          <SmartContractPanel />
        </div>
      </div>
    </div>
  );
};

// Smart Contract Panel Component
const SmartContractPanel = () => {
  const [contractInfo, setContractInfo] = useState(null);
  const [deploymentGuide, setDeploymentGuide] = useState(null);
  const [contractAddress, setContractAddress] = useState('');
  const [deployerAddress, setDeployerAddress] = useState('');
  const [txHash, setTxHash] = useState('');
  const [registering, setRegistering] = useState(false);
  const [showCode, setShowCode] = useState(false);
  const [sourceCode, setSourceCode] = useState('');

  useEffect(() => {
    axios.get(`${API}/contract/info`).then(res => setContractInfo(res.data)).catch(console.error);
    axios.get(`${API}/contract/deployment-guide`).then(res => setDeploymentGuide(res.data)).catch(console.error);
  }, []);

  const fetchSourceCode = async () => {
    try {
      const res = await axios.get(`${API}/contract/source`);
      setSourceCode(res.data.source);
      setShowCode(true);
    } catch (error) {
      toast.error("Failed to fetch source code");
    }
  };

  const registerContract = async () => {
    if (!contractAddress || !deployerAddress || !txHash) {
      toast.error("Please fill all fields");
      return;
    }
    setRegistering(true);
    try {
      const res = await axios.post(`${API}/contract/register?contract_address=${contractAddress}&deployer_address=${deployerAddress}&tx_hash=${txHash}`);
      toast.success(res.data.message);
      setContractInfo({ ...contractInfo, deployed: true, contract_address: contractAddress });
    } catch (error) {
      toast.error(error.response?.data?.detail || "Registration failed");
    }
    setRegistering(false);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard!");
  };

  return (
    <Card className="glass-card mt-8 border-[#7B61FF]/30" data-testid="smart-contract-panel">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileCode className="w-5 h-5 text-[#7B61FF]" />
          Smart Contract (Sepolia Testnet)
        </CardTitle>
        <CardDescription>Deploy and manage the AlphaAI Manager contract on Ethereum</CardDescription>
      </CardHeader>
      <CardContent>
        {/* Contract Status */}
        <div className="flex items-center gap-4 mb-6 p-4 rounded-lg bg-[#050505] border border-zinc-800">
          <div className={`w-3 h-3 rounded-full ${contractInfo?.deployed ? 'bg-[#00FF94]' : 'bg-[#FFB800]'}`} />
          <div className="flex-1">
            <p className="font-medium">{contractInfo?.deployed ? 'Contract Deployed' : 'Contract Not Deployed'}</p>
            <p className="text-sm text-zinc-400">
              {contractInfo?.deployed 
                ? <a href={`https://sepolia.etherscan.io/address/${contractInfo.contract_address}`} target="_blank" rel="noopener noreferrer" className="text-[#7B61FF] hover:underline">{contractInfo.contract_address}</a>
                : 'Deploy to Sepolia testnet to enable on-chain transactions'}
            </p>
          </div>
          <Badge className={contractInfo?.deployed ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-[#FFB800]/20 text-[#FFB800]'}>
            {contractInfo?.network?.toUpperCase() || 'SEPOLIA'}
          </Badge>
        </div>

        {/* Deployment Steps */}
        {!contractInfo?.deployed && deploymentGuide && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Rocket className="w-5 h-5 text-[#FFB800]" />
              Deployment Steps
            </h3>
            <div className="space-y-3">
              {deploymentGuide.steps?.map((step, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-[#050505] border border-zinc-800">
                  <div className="w-6 h-6 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] flex items-center justify-center text-sm font-bold flex-shrink-0">
                    {step.step}
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{step.title}</p>
                    <p className="text-xs text-zinc-400">{step.description}</p>
                    {step.links && (
                      <div className="mt-1 flex gap-2">
                        {step.links.map((link, j) => (
                          <a key={j} href={link} target="_blank" rel="noopener noreferrer" className="text-xs text-[#7B61FF] hover:underline flex items-center gap-1">
                            <ExternalLink className="w-3 h-3" />{link.split('/')[2]}
                          </a>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Contract Source */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Terminal className="w-5 h-5 text-[#00FF94]" />
              Contract Source Code
            </h3>
            <div className="flex gap-2">
              <Button onClick={fetchSourceCode} variant="outline" size="sm" className="rounded-full border-zinc-700">
                {showCode ? 'Refresh' : 'View Code'}
              </Button>
              {showCode && (
                <Button onClick={() => copyToClipboard(sourceCode)} variant="outline" size="sm" className="rounded-full border-zinc-700">
                  <Copy className="w-4 h-4 mr-1" />Copy
                </Button>
              )}
            </div>
          </div>
          {showCode && (
            <div className="bg-[#050505] border border-zinc-800 rounded-lg p-4 max-h-[300px] overflow-auto">
              <pre className="text-xs text-zinc-300 font-mono whitespace-pre-wrap">{sourceCode}</pre>
            </div>
          )}
        </div>

        {/* Register Deployed Contract */}
        {!contractInfo?.deployed && (
          <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Check className="w-5 h-5 text-[#00FF94]" />
              Register Deployed Contract
            </h3>
            <div className="grid md:grid-cols-3 gap-4 mb-4">
              <div>
                <label className="text-sm text-zinc-400 block mb-1">Contract Address</label>
                <Input 
                  placeholder="0x..." 
                  value={contractAddress} 
                  onChange={e => setContractAddress(e.target.value)}
                  className="bg-[#121212] border-zinc-700 font-mono text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 block mb-1">Deployer Address</label>
                <Input 
                  placeholder="0x..." 
                  value={deployerAddress}
                  onChange={e => setDeployerAddress(e.target.value)}
                  className="bg-[#121212] border-zinc-700 font-mono text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 block mb-1">Transaction Hash</label>
                <Input 
                  placeholder="0x..." 
                  value={txHash}
                  onChange={e => setTxHash(e.target.value)}
                  className="bg-[#121212] border-zinc-700 font-mono text-sm"
                />
              </div>
            </div>
            <Button 
              onClick={registerContract} 
              disabled={registering}
              className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
            >
              {registering ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-2" />}
              Register Contract
            </Button>
          </div>
        )}

        {/* Contract Functions (if deployed) */}
        {contractInfo?.deployed && (
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
              <h4 className="font-medium mb-2 flex items-center gap-2">
                <Wallet className="w-4 h-4 text-[#00FF94]" />Investor Functions
              </h4>
              <p className="text-xs text-zinc-400 mb-2">deposit(), withdraw(), getInvestorBalance()</p>
              <Button size="sm" variant="outline" className="rounded-full border-[#00FF94]/50 text-[#00FF94]">
                <ExternalLink className="w-3 h-3 mr-1" />View on Etherscan
              </Button>
            </div>
            <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
              <h4 className="font-medium mb-2 flex items-center gap-2">
                <Target className="w-4 h-4 text-[#7B61FF]" />Strategy Functions
              </h4>
              <p className="text-xs text-zinc-400 mb-2">addStrategy(), allocateToStrategy(), getStrategy()</p>
              <Button size="sm" variant="outline" className="rounded-full border-[#7B61FF]/50 text-[#7B61FF]">
                <ExternalLink className="w-3 h-3 mr-1" />View on Etherscan
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Event-Driven Agents Dashboard Component
const EventAgentsDashboard = () => {
  const [eventAgents, setEventAgents] = useState([]);
  const [recentEvents, setRecentEvents] = useState([]);
  const [investorBalances, setInvestorBalances] = useState({ data: [], summary: {} });
  const [strategyAllocation, setStrategyAllocation] = useState({ data: [], summary: {} });
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [agentsRes, eventsRes, balancesRes, allocRes] = await Promise.all([
        axios.get(`${API}/agents/event-agents`),
        axios.get(`${API}/events/recent`),
        axios.get(`${API}/dashboards/investor-balances`),
        axios.get(`${API}/dashboards/strategy-allocation`)
      ]);
      setEventAgents(agentsRes.data.agents || []);
      setRecentEvents(eventsRes.data.events || []);
      setInvestorBalances(balancesRes.data);
      setStrategyAllocation(allocRes.data);
    } catch (error) {
      console.error("Failed to fetch event data:", error);
    }
  };

  const toggleAgent = async (agentId) => {
    try {
      await axios.post(`${API}/agents/event-agents/toggle/${agentId}`);
      fetchData();
      toast.success("Agent status updated");
    } catch (error) {
      toast.error("Failed to toggle agent");
    }
  };

  const simulateEvent = async (eventName) => {
    setSimulating(true);
    try {
      const res = await axios.post(`${API}/events/simulate?event_name=${eventName}&amount_eth=${(Math.random() * 5 + 0.5).toFixed(2)}`);
      toast.success(`Event simulated: ${eventName}`);
      fetchData();
    } catch (error) {
      toast.error("Failed to simulate event");
    }
    setSimulating(false);
  };

  const getAgentTypeColor = (type) => {
    switch(type) {
      case 'watcher': return 'text-blue-400 bg-blue-400/20';
      case 'execution': return 'text-[#00FF94] bg-[#00FF94]/20';
      case 'analytics': return 'text-[#FFB800] bg-[#FFB800]/20';
      default: return 'text-zinc-400 bg-zinc-700';
    }
  };

  const getEventColor = (eventName) => {
    if (eventName.includes('Deposited')) return 'text-[#00FF94]';
    if (eventName.includes('Withdrawn')) return 'text-red-400';
    if (eventName.includes('Allocated')) return 'text-[#7B61FF]';
    return 'text-zinc-400';
  };

  return (
    <div className="space-y-6">
      {/* Event Agents Status */}
      <Card className="glass-card border-[#00FF94]/30" data-testid="event-agents-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-[#00FF94]" />
            Event-Driven Agents
          </CardTitle>
          <CardDescription>Smart contract event monitors and automated actions</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4 mb-6">
            {eventAgents.map((agent) => (
              <div key={agent.id} className="p-4 rounded-lg bg-[#050505] border border-zinc-800" data-testid={`event-agent-${agent.id}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${agent.is_active ? 'bg-[#00FF94]' : 'bg-zinc-500'}`} />
                    <span className="font-medium text-sm">{agent.name}</span>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => toggleAgent(agent.id)} className="h-6 w-6 p-0">
                    {agent.is_active ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
                  </Button>
                </div>
                <Badge className={getAgentTypeColor(agent.type)}>{agent.type}</Badge>
                <p className="text-xs text-zinc-500 mt-2">{agent.description || `Monitors: ${agent.events_to_monitor?.join(', ')}`}</p>
                <div className="flex items-center justify-between mt-3 text-xs">
                  <span className="text-zinc-500">Events processed</span>
                  <span className="font-mono text-[#00FF94]">{agent.events_processed_count || 0}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Event Simulation */}
          <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#FFB800]" />
              Simulate Contract Events
            </h4>
            <div className="flex flex-wrap gap-2">
              <Button 
                onClick={() => simulateEvent('InvestorDeposited')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-[#00FF94]/50 text-[#00FF94]"
              >
                <Plus className="w-3 h-3 mr-1" />Deposit
              </Button>
              <Button 
                onClick={() => simulateEvent('InvestorWithdrawn')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-red-400/50 text-red-400"
              >
                <Minus className="w-3 h-3 mr-1" />Withdrawal
              </Button>
              <Button 
                onClick={() => simulateEvent('StrategyAllocated')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-[#7B61FF]/50 text-[#7B61FF]"
              >
                <Target className="w-3 h-3 mr-1" />Allocate
              </Button>
              <Button 
                onClick={() => simulateEvent('StrategyDeallocated')} 
                disabled={simulating}
                size="sm"
                variant="outline"
                className="rounded-full border-zinc-500/50 text-zinc-400"
              >
                <ArrowDown className="w-3 h-3 mr-1" />Deallocate
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Dashboards Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Investor Balances Dashboard */}
        <Card className="glass-card" data-testid="investor-balances-dashboard">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Wallet className="w-5 h-5 text-[#00FF94]" />
              Investor Balances
            </CardTitle>
            <div className="flex gap-4 mt-2">
              <div className="text-center">
                <p className="text-2xl font-bold font-mono text-[#00FF94]">{investorBalances.summary?.total_deposited_eth?.toFixed(2) || '0.00'}</p>
                <p className="text-xs text-zinc-500">Total ETH</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold font-mono">{investorBalances.summary?.active_investors || 0}</p>
                <p className="text-xs text-zinc-500">Active Investors</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px]">
              <div className="space-y-2">
                {investorBalances.data?.map((investor, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${investor.status === 'active' ? 'bg-[#00FF94]' : 'bg-zinc-500'}`} />
                      <span className="font-mono text-xs">{investor.address?.slice(0, 10)}...{investor.address?.slice(-6)}</span>
                    </div>
                    <span className="font-mono text-sm text-[#00FF94]">{investor.balance?.toFixed(4)} ETH</span>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>

        {/* Strategy Allocation Dashboard */}
        <Card className="glass-card" data-testid="strategy-allocation-dashboard">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-[#7B61FF]" />
              Strategy Allocation
            </CardTitle>
            <div className="flex gap-4 mt-2">
              <div className="text-center">
                <p className="text-2xl font-bold font-mono text-[#7B61FF]">{strategyAllocation.summary?.total_allocated_eth?.toFixed(2) || '0.00'}</p>
                <p className="text-xs text-zinc-500">Total Allocated</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold font-mono">{strategyAllocation.summary?.active_strategies || 0}</p>
                <p className="text-xs text-zinc-500">Active Strategies</p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[200px]">
              <div className="space-y-2">
                {strategyAllocation.data?.map((strategy, i) => (
                  <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${strategy.active ? 'bg-[#7B61FF]' : 'bg-zinc-500'}`} />
                      <span className="text-sm">{strategy.name}</span>
                    </div>
                    <div className="text-right">
                      <span className="font-mono text-sm text-[#7B61FF]">{strategy.allocated_capital?.toFixed(2)} ETH</span>
                      <p className="text-xs text-zinc-500">{strategy.transactions} txns</p>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>

      {/* Recent Events Log */}
      <Card className="glass-card" data-testid="recent-events-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-[#FFB800]" />
            Recent Contract Events
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[200px]">
            <div className="space-y-2">
              {recentEvents.slice(0, 10).map((event, i) => (
                <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                  <div className="flex items-center gap-3">
                    <Badge className={`${getEventColor(event.event_name)} bg-opacity-20`}>{event.event_name}</Badge>
                    <span className="font-mono text-xs text-zinc-500">{event.tx_hash?.slice(0, 14)}...</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-zinc-400">{new Date(event.timestamp).toLocaleTimeString()}</span>
                    {event.processed && <Check className="w-3 h-3 text-[#00FF94]" />}
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
};

// Event Agents Page Wrapper
const EventAgentsPage = () => {
  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <h1 className="text-4xl font-bold mb-2 font-['Outfit']">Event-Driven Agents</h1>
          <p className="text-zinc-400">Smart contract event monitors with automated actions and dashboards</p>
        </motion.div>
        <EventAgentsDashboard />
      </div>
    </div>
  );
};

// Research Engine Page
const ResearchEnginePage = () => {
  const [running, setRunning] = useState(false);
  const [simResults, setSimResults] = useState(null);
  const [wfResults, setWfResults] = useState(null);
  const [report, setReport] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [targetMonths, setTargetMonths] = useState(6);

  useEffect(() => {
    axios.get(`${API}/research/metrics`).then(res => setMetrics(res.data)).catch(console.error);
  }, []);

  const runSimulation = async () => {
    setRunning(true);
    try {
      const res = await axios.post(`${API}/research/run-simulation?target_months=${targetMonths}&speed_multiplier=500&initial_capital=100000`);
      setSimResults(res.data);
      toast.success(`Simulation complete: ${res.data.metrics?.total_return}% return`);
    } catch (error) {
      toast.error("Simulation failed");
    }
    setRunning(false);
  };

  const runWalkForward = async () => {
    setRunning(true);
    try {
      const res = await axios.post(`${API}/research/walk-forward-test?training_days=90&testing_days=30&num_windows=6`);
      setWfResults(res.data);
      toast.success(`Walk-forward complete: ${res.data.recommendation}`);
    } catch (error) {
      toast.error("Walk-forward test failed");
    }
    setRunning(false);
  };

  const generateReport = async () => {
    try {
      const res = await axios.post(`${API}/research/generate-investor-report`);
      setReport(res.data.report);
      toast.success("Investor report generated!");
    } catch (error) {
      toast.error("Report generation failed");
    }
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2 font-['Outfit']">Research Engine</h1>
              <p className="text-zinc-400">500x Accelerated Simulation • Walk-Forward Validation • Investor Reports</p>
            </div>
            <Badge className="bg-[#00FF94]/20 text-[#00FF94]">v1.0</Badge>
          </div>
        </motion.div>

        {/* Control Panel */}
        <Card className="glass-card mb-6 border-[#7B61FF]/30" data-testid="research-control-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Beaker className="w-5 h-5 text-[#7B61FF]" />
              Research Controls
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              {/* Simulation Control */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <Rocket className="w-4 h-4 text-[#FFB800]" />
                  500x Accelerated Simulation
                </h4>
                <div className="flex items-center gap-2 mb-3">
                  <Input 
                    type="number" 
                    value={targetMonths}
                    onChange={e => setTargetMonths(Number(e.target.value))}
                    className="w-20 bg-[#121212] border-zinc-700"
                    min={1}
                    max={12}
                  />
                  <span className="text-sm text-zinc-400">months</span>
                </div>
                <Button 
                  onClick={runSimulation} 
                  disabled={running}
                  className="w-full rounded-full bg-[#FFB800] text-black hover:bg-[#FFB800]/90"
                  data-testid="run-research-sim-btn"
                >
                  {running ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Play className="w-4 h-4 mr-2" />}
                  Run Simulation
                </Button>
              </div>

              {/* Walk-Forward Control */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-[#00FF94]" />
                  Walk-Forward Validation
                </h4>
                <p className="text-xs text-zinc-500 mb-3">90 days training • 30 days testing • 6 windows</p>
                <Button 
                  onClick={runWalkForward} 
                  disabled={running}
                  className="w-full rounded-full bg-[#00FF94] text-black hover:bg-[#00FF94]/90"
                  data-testid="run-walk-forward-btn"
                >
                  {running ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Target className="w-4 h-4 mr-2" />}
                  Run Walk-Forward
                </Button>
              </div>

              {/* Report Generation */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h4 className="font-medium mb-3 flex items-center gap-2">
                  <FileCode className="w-4 h-4 text-[#7B61FF]" />
                  Investor Report
                </h4>
                <p className="text-xs text-zinc-500 mb-3">PDF/JSON • Performance • Risk Metrics</p>
                <Button 
                  onClick={generateReport} 
                  disabled={!simResults}
                  variant="outline"
                  className="w-full rounded-full border-[#7B61FF]/50 text-[#7B61FF]"
                  data-testid="generate-report-btn"
                >
                  <ScrollText className="w-4 h-4 mr-2" />
                  Generate Report
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Results Grid */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Simulation Results */}
          {simResults && (
            <Card className="glass-card" data-testid="simulation-results">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="w-5 h-5 text-[#FFB800]" />
                  Simulation Results
                </CardTitle>
                <CardDescription>{simResults.summary?.period} at {simResults.summary?.speed}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Total Return</p>
                    <p className={`text-2xl font-bold font-mono ${simResults.metrics?.total_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {simResults.metrics?.total_return >= 0 ? '+' : ''}{simResults.metrics?.total_return}%
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Sharpe Ratio</p>
                    <p className="text-2xl font-bold font-mono text-[#7B61FF]">{simResults.metrics?.sharpe_ratio}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Max Drawdown</p>
                    <p className="text-2xl font-bold font-mono text-red-400">-{simResults.metrics?.max_drawdown}%</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Win Rate</p>
                    <p className="text-2xl font-bold font-mono">{simResults.metrics?.win_rate}%</p>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="text-center">
                    <p className="text-zinc-500">Trades</p>
                    <p className="font-mono font-bold">{simResults.metrics?.total_trades}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-zinc-500">Profit Factor</p>
                    <p className="font-mono font-bold">{simResults.metrics?.profit_factor}</p>
                  </div>
                  <div className="text-center">
                    <p className="text-zinc-500">Final Capital</p>
                    <p className="font-mono font-bold text-[#00FF94]">${simResults.summary?.final_capital?.toLocaleString()}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Walk-Forward Results */}
          {wfResults && (
            <Card className="glass-card" data-testid="walk-forward-results">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Target className="w-5 h-5 text-[#00FF94]" />
                    Walk-Forward Validation
                  </CardTitle>
                  <Badge className={wfResults.recommendation === 'ROBUST' ? 'bg-[#00FF94]/20 text-[#00FF94]' : wfResults.recommendation === 'NEEDS_REVIEW' ? 'bg-[#FFB800]/20 text-[#FFB800]' : 'bg-red-400/20 text-red-400'}>
                    {wfResults.recommendation}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Robustness Score</p>
                    <p className="text-2xl font-bold font-mono text-[#00FF94]">{wfResults.summary?.robustness_score}</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
                    <p className="text-xs text-zinc-500">Profitable Windows</p>
                    <p className="text-2xl font-bold font-mono">{wfResults.summary?.profitable_windows}/6</p>
                  </div>
                </div>
                <ScrollArea className="h-[150px]">
                  <div className="space-y-2">
                    {wfResults.windows?.map((w, i) => (
                      <div key={i} className="flex items-center justify-between p-2 rounded bg-[#050505] border border-zinc-800">
                        <span className="text-sm">Window {w.window_id}</span>
                        <div className="flex items-center gap-4">
                          <span className="text-xs text-zinc-500">Train: {w.training_return}%</span>
                          <span className={`text-xs font-mono ${w.testing_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                            Test: {w.testing_return >= 0 ? '+' : ''}{w.testing_return}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Investor Report Preview */}
        {report && (
          <Card className="glass-card mt-6" data-testid="investor-report-preview">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <ScrollText className="w-5 h-5 text-[#7B61FF]" />
                  Investor Report
                </CardTitle>
                <span className="text-xs text-zinc-500">{new Date(report.generated_at).toLocaleString()}</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4 mb-6">
                <div className="p-4 rounded-lg bg-gradient-to-br from-[#00FF94]/20 to-transparent border border-[#00FF94]/30 text-center">
                  <p className="text-xs text-zinc-400">Total Return</p>
                  <p className="text-3xl font-bold font-mono text-[#00FF94]">+{report.executive_summary?.total_return}%</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-[#7B61FF]/20 to-transparent border border-[#7B61FF]/30 text-center">
                  <p className="text-xs text-zinc-400">Sharpe Ratio</p>
                  <p className="text-3xl font-bold font-mono text-[#7B61FF]">{report.executive_summary?.sharpe_ratio}</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-red-400/20 to-transparent border border-red-400/30 text-center">
                  <p className="text-xs text-zinc-400">Max Drawdown</p>
                  <p className="text-3xl font-bold font-mono text-red-400">-{report.executive_summary?.max_drawdown}%</p>
                </div>
                <div className="p-4 rounded-lg bg-gradient-to-br from-[#FFB800]/20 to-transparent border border-[#FFB800]/30 text-center">
                  <p className="text-xs text-zinc-400">Win Rate</p>
                  <p className="text-3xl font-bold font-mono text-[#FFB800]">{report.executive_summary?.win_rate}%</p>
                </div>
              </div>
              
              {/* Strategy Breakdown */}
              <h4 className="font-semibold mb-3">Strategy Performance</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {report.strategy_breakdown?.map((s, i) => (
                  <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                    <p className="text-sm font-medium mb-1">{s.name}</p>
                    <p className={`text-lg font-mono font-bold ${s.return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {s.return >= 0 ? '+' : ''}{s.return}%
                    </p>
                    <p className="text-xs text-zinc-500">Sharpe: {s.sharpe}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
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

        {/* Enhanced Simulation Panel */}
        <Card className="glass-card mb-8 border-[#FFB800]/30" data-testid="enhanced-simulation-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Gauge className="w-5 h-5 text-[#FFB800]" />Accelerated Simulation & Stress Testing</CardTitle>
            <CardDescription>Run 100x time-accelerated backtests and stress test scenarios</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              {/* Accelerated Simulation */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-[#FFB800]" />100x Time Acceleration
                </h3>
                <div className="flex items-center gap-3 mb-4">
                  <Input 
                    type="number" 
                    value={daysToSimulate} 
                    onChange={(e) => setDaysToSimulate(Number(e.target.value))}
                    className="w-24 bg-[#121212] border-zinc-700"
                    min={1}
                    max={365}
                  />
                  <span className="text-zinc-400">days to simulate</span>
                </div>
                <Button 
                  onClick={runAcceleratedSimulation} 
                  disabled={acceleratedRunning}
                  className="w-full rounded-full bg-[#FFB800] text-black hover:bg-[#FFB800]/90"
                  data-testid="run-accelerated-btn"
                >
                  {acceleratedRunning ? <RefreshCw className="w-4 h-4 mr-2 animate-spin" /> : <Rocket className="w-4 h-4 mr-2" />}
                  {acceleratedRunning ? 'Simulating...' : 'Run Accelerated Backtest'}
                </Button>
                
                {acceleratedResults && (
                  <div className="mt-4 p-3 rounded-lg bg-[#121212] border border-[#FFB800]/30">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-zinc-500">Days Simulated</p>
                        <p className="font-mono font-bold">{acceleratedResults.summary?.days_simulated}</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Total Trades</p>
                        <p className="font-mono font-bold">{acceleratedResults.summary?.total_trades}</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Final Capital</p>
                        <p className="font-mono font-bold text-[#00FF94]">${acceleratedResults.summary?.final_capital?.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Total Return</p>
                        <p className={`font-mono font-bold ${acceleratedResults.summary?.total_return_percent >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {acceleratedResults.summary?.total_return_percent >= 0 ? '+' : ''}{acceleratedResults.summary?.total_return_percent?.toFixed(2)}%
                        </p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Win Rate</p>
                        <p className="font-mono font-bold">{acceleratedResults.summary?.win_rate}%</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Best Day P&L</p>
                        <p className="font-mono font-bold text-[#00FF94]">+${acceleratedResults.summary?.best_day?.day_pnl?.toFixed(2)}</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Stress Testing */}
              <div className="p-4 rounded-lg bg-[#050505] border border-zinc-800">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />Stress Test Scenarios
                </h3>
                <div className="space-y-2 mb-4">
                  <Button 
                    onClick={() => runStressTest('High Volatility BTC Drop')}
                    disabled={stressTestRunning}
                    variant="outline"
                    className="w-full justify-start rounded-lg border-zinc-700 hover:border-red-500/50"
                    data-testid="stress-btc-drop-btn"
                  >
                    <TrendingUp className="w-4 h-4 mr-2 text-red-400 rotate-180" />
                    BTC 30% Drop (24h)
                  </Button>
                  <Button 
                    onClick={() => runStressTest('ETH Flash Crash')}
                    disabled={stressTestRunning}
                    variant="outline"
                    className="w-full justify-start rounded-lg border-zinc-700 hover:border-red-500/50"
                    data-testid="stress-eth-crash-btn"
                  >
                    <Zap className="w-4 h-4 mr-2 text-red-400" />
                    ETH Flash Crash 50% (12h)
                  </Button>
                  <Button 
                    onClick={() => runStressTest('Market Panic Sell')}
                    disabled={stressTestRunning}
                    variant="outline"
                    className="w-full justify-start rounded-lg border-zinc-700 hover:border-red-500/50"
                    data-testid="stress-panic-btn"
                  >
                    <Activity className="w-4 h-4 mr-2 text-red-400" />
                    Market Panic Sell 40% (6h)
                  </Button>
                </div>
                
                {stressTestResults && (
                  <div className="p-3 rounded-lg bg-[#121212] border border-red-500/30">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-zinc-400">{stressTestResults.scenario}</span>
                      <Badge className={stressTestResults.results?.survival_status === 'SURVIVED' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-500/20 text-red-400'}>
                        {stressTestResults.results?.survival_status}
                      </Badge>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <p className="text-zinc-500">Max Drawdown</p>
                        <p className="font-mono font-bold text-red-400">-{stressTestResults.results?.max_drawdown_percent?.toFixed(1)}%</p>
                      </div>
                      <div>
                        <p className="text-zinc-500">Final Capital</p>
                        <p className="font-mono font-bold">${stressTestResults.results?.final_capital?.toLocaleString()}</p>
                      </div>
                    </div>
                    {stressTestResults.results?.risk_actions_taken?.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-zinc-800">
                        <p className="text-xs text-zinc-500 mb-1">Risk Actions Triggered:</p>
                        {stressTestResults.results.risk_actions_taken.map((action, i) => (
                          <p key={i} className="text-xs text-[#FFB800]">• {action}</p>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Agent Performance */}
            {agentPerformance.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Bot className="w-5 h-5 text-[#7B61FF]" />Agent Performance
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {agentPerformance.map((agent, i) => (
                    <div key={i} className="p-3 rounded-lg bg-[#050505] border border-zinc-800">
                      <p className="text-sm font-medium mb-1">{agent.name}</p>
                      <p className={`text-xl font-bold font-mono ${agent.performance_ytd >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                        {agent.performance_ytd >= 0 ? '+' : ''}{agent.performance_ytd}%
                      </p>
                      <p className="text-xs text-zinc-500">{agent.trades_executed || agent.strategies_deployed || 0} {agent.type === 'sandbox' ? 'strategies' : 'trades'}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Export Button */}
            <div className="mt-6 flex justify-end">
              <Button onClick={exportResults} variant="outline" className="rounded-full border-zinc-700" data-testid="export-results-btn">
                <FileCode className="w-4 h-4 mr-2" />Export Results (PDF/CSV)
              </Button>
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

// Referral Page
const ReferralPage = () => {
  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        <ReferralDashboard />
      </div>
    </div>
  );
};

// Leaderboard Page
const LeaderboardPage = () => {
  const { user, tokens } = useAuth();
  const [traders, setTraders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState('all_time');
  const [sortBy, setSortBy] = useState('pnl');
  const [myRank, setMyRank] = useState(null);
  const [topPerformers, setTopPerformers] = useState(null);
  const [selectedTrader, setSelectedTrader] = useState(null);
  const [traderDetailOpen, setTraderDetailOpen] = useState(false);
  const [followModalOpen, setFollowModalOpen] = useState(false);
  const [followTarget, setFollowTarget] = useState(null);

  const userTier = user?.is_elite ? 'elite' : user?.is_pro ? 'pro' : 'free';
  const isPro = userTier !== 'free';

  useEffect(() => {
    loadLeaderboard();
    loadTopPerformers();
    if (user?.id) loadMyRank();
  }, [period, sortBy, user]);

  const loadLeaderboard = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/leaderboard?period=${period}&sort_by=${sortBy}&user_tier=${userTier}&limit=50`);
      setTraders(res.data.traders || []);
    } catch (error) {
      console.error('Leaderboard error:', error);
    }
    setLoading(false);
  };

  const loadTopPerformers = async () => {
    try {
      const res = await axios.get(`${API}/leaderboard/top-performers?limit=5`);
      setTopPerformers(res.data);
    } catch (error) {
      console.error('Top performers error:', error);
    }
  };

  const loadMyRank = async () => {
    try {
      const res = await axios.get(`${API}/leaderboard/me?user_id=${user.id}`);
      setMyRank(res.data);
    } catch (error) {
      console.error('My rank error:', error);
    }
  };

  const viewTraderProfile = async (traderId) => {
    try {
      const res = await axios.get(`${API}/leaderboard/trader/${traderId}?user_tier=${userTier}`);
      setSelectedTrader(res.data);
      setTraderDetailOpen(true);
    } catch (error) {
      toast.error('Failed to load trader profile');
    }
  };

  const formatPnl = (value) => {
    if (value === undefined || value === null) return '-';
    const formatted = Math.abs(value).toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    return value >= 0 ? `+${formatted}` : `-${formatted.replace('$', '')}`;
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold font-['Outfit']" data-testid="leaderboard-title">
              <Trophy className="inline w-8 h-8 mr-2 text-[#FFB800]" />
              Leaderboard
            </h1>
            <p className="text-zinc-400 mt-1">Top performing traders on AlphaAI</p>
          </div>
          {myRank && myRank.ranks?.pnl && (
            <div className="text-right">
              <p className="text-sm text-zinc-500">Your Rank</p>
              <p className="text-2xl font-bold text-[#7B61FF]">#{myRank.ranks.pnl}</p>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-6">
          <Select value={period} onValueChange={setPeriod}>
            <SelectTrigger className="w-36 bg-[#121212] border-zinc-800" data-testid="period-select">
              <SelectValue placeholder="Period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="daily">Daily</SelectItem>
              <SelectItem value="weekly">Weekly</SelectItem>
              <SelectItem value="monthly">Monthly</SelectItem>
              <SelectItem value="all_time">All Time</SelectItem>
            </SelectContent>
          </Select>

          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-36 bg-[#121212] border-zinc-800" data-testid="sort-select">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="pnl">Total P&L</SelectItem>
              <SelectItem value="win_rate">Win Rate</SelectItem>
              <SelectItem value="roi">ROI %</SelectItem>
              <SelectItem value="total_trades">Trades</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" onClick={loadLeaderboard} className="border-zinc-700">
            <RefreshCw className="w-4 h-4 mr-2" /> Refresh
          </Button>
        </div>

        {/* Top Performers Cards */}
        {topPerformers && (
          <div className="grid md:grid-cols-3 gap-4 mb-8">
            <Card className="glass-card border-[#FFB800]/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <DollarSign className="w-4 h-4 text-[#FFB800]" /> Top P&L
                </CardTitle>
              </CardHeader>
              <CardContent>
                {topPerformers.top_by_pnl?.slice(0, 3).map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[#FFB800] font-bold">{i + 1}</span>
                      <span className="text-sm truncate">{t.display_name || `Trader_${t.user_id?.slice(0,6)}`}</span>
                    </div>
                    <span className="text-[#00FF94] font-mono text-sm">{formatPnl(t.stats?.total_pnl)}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="glass-card border-[#00FF94]/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Target className="w-4 h-4 text-[#00FF94]" /> Top Win Rate
                </CardTitle>
              </CardHeader>
              <CardContent>
                {topPerformers.top_by_win_rate?.slice(0, 3).map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[#00FF94] font-bold">{i + 1}</span>
                      <span className="text-sm truncate">{t.display_name || `Trader_${t.user_id?.slice(0,6)}`}</span>
                    </div>
                    <span className="text-white font-mono text-sm">{t.stats?.win_rate?.toFixed(1)}%</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="glass-card border-[#7B61FF]/30">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-[#7B61FF]" /> Top ROI
                </CardTitle>
              </CardHeader>
              <CardContent>
                {topPerformers.top_by_roi?.slice(0, 3).map((t, i) => (
                  <div key={i} className="flex items-center justify-between py-1">
                    <div className="flex items-center gap-2">
                      <span className="text-[#7B61FF] font-bold">{i + 1}</span>
                      <span className="text-sm truncate">{t.display_name || `Trader_${t.user_id?.slice(0,6)}`}</span>
                    </div>
                    <span className="text-white font-mono text-sm">{t.stats?.roi_percentage?.toFixed(1)}%</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Leaderboard */}
        <Card className="glass-card">
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="w-8 h-8 animate-spin text-[#7B61FF]" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-zinc-800">
                      <th className="text-left p-4 text-zinc-500 text-sm">Rank</th>
                      <th className="text-left p-4 text-zinc-500 text-sm">Trader</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Total P&L</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Win Rate</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">ROI</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Trades</th>
                      <th className="text-right p-4 text-zinc-500 text-sm">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {traders.map((trader, i) => (
                      <tr key={trader.user_id} className="border-b border-zinc-800/50 hover:bg-[#050505]/50" data-testid={`leaderboard-row-${i}`}>
                        <td className="p-4">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                            trader.rank_position === 1 ? 'bg-[#FFB800]/20 text-[#FFB800]' :
                            trader.rank_position === 2 ? 'bg-zinc-400/20 text-zinc-400' :
                            trader.rank_position === 3 ? 'bg-[#CD7F32]/20 text-[#CD7F32]' :
                            'bg-zinc-800 text-zinc-400'
                          }`}>
                            {trader.rank_position}
                          </div>
                        </td>
                        <td className="p-4">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">{trader.display_name || `Trader_${trader.user_id?.slice(0,6)}`}</span>
                            {trader.is_elite && <Badge className="bg-[#FFB800]/20 text-[#FFB800] text-xs">ELITE</Badge>}
                            {trader.is_pro && !trader.is_elite && <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-xs">PRO</Badge>}
                          </div>
                        </td>
                        <td className={`p-4 text-right font-mono ${trader.stats?.total_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {formatPnl(trader.stats?.total_pnl)}
                        </td>
                        <td className="p-4 text-right font-mono">
                          {trader.stats?.win_rate?.toFixed(1) || '-'}%
                        </td>
                        <td className={`p-4 text-right font-mono ${(trader.stats?.roi_percentage || 0) >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                          {trader.stats?.roi_percentage?.toFixed(1) || '-'}%
                        </td>
                        <td className="p-4 text-right font-mono text-zinc-400">
                          {trader.stats?.total_trades || 0}
                        </td>
                        <td className="p-4 text-right">
                          <div className="flex justify-end gap-1">
                            {isPro && trader.user_id !== user?.id && (
                              <Button size="sm" onClick={() => { setFollowTarget(trader); setFollowModalOpen(true); }}
                                className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-xs"
                                data-testid={`follow-btn-${trader.user_id}`}
                              >
                                <Copy className="w-3 h-3 mr-1" /> Copy
                              </Button>
                            )}
                            <Button size="sm" variant="outline" onClick={() => viewTraderProfile(trader.user_id)} className="border-zinc-700">
                              View
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {!isPro && traders.length >= 10 && (
              <div className="p-4 border-t border-zinc-800 bg-[#7B61FF]/5 text-center">
                <p className="text-sm text-zinc-400">
                  <Shield className="inline w-4 h-4 mr-1 text-[#7B61FF]" />
                  Upgrade to Pro to see the full leaderboard and detailed trader stats
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Trader Detail Dialog */}
        <Dialog open={traderDetailOpen} onOpenChange={setTraderDetailOpen}>
          <DialogContent className="bg-[#121212] border-zinc-800 max-w-lg">
            <DialogHeader>
              <DialogTitle>Trader Profile</DialogTitle>
            </DialogHeader>
            {selectedTrader && (
              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 rounded-full bg-[#7B61FF]/20 flex items-center justify-center">
                    <User className="w-8 h-8 text-[#7B61FF]" />
                  </div>
                  <div>
                    <p className="text-xl font-bold">{selectedTrader.display_name || `Trader_${selectedTrader.user_id?.slice(0,6)}`}</p>
                    <div className="flex gap-2 mt-1">
                      {selectedTrader.is_elite && <Badge className="bg-[#FFB800]/20 text-[#FFB800]">ELITE</Badge>}
                      {selectedTrader.is_pro && !selectedTrader.is_elite && <Badge className="bg-[#7B61FF]/20 text-[#7B61FF]">PRO</Badge>}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">Total P&L</p>
                    <p className={`text-lg font-mono ${selectedTrader.stats?.total_pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {formatPnl(selectedTrader.stats?.total_pnl)}
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">Win Rate</p>
                    <p className="text-lg font-mono">{selectedTrader.stats?.win_rate?.toFixed(1) || '-'}%</p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">ROI</p>
                    <p className={`text-lg font-mono ${(selectedTrader.stats?.roi_percentage || 0) >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                      {selectedTrader.stats?.roi_percentage?.toFixed(1) || '-'}%
                    </p>
                  </div>
                  <div className="p-3 rounded-lg bg-[#050505]">
                    <p className="text-xs text-zinc-500">Total Trades</p>
                    <p className="text-lg font-mono">{selectedTrader.stats?.total_trades || 0}</p>
                  </div>
                </div>

                {selectedTrader.recent_trades && selectedTrader.recent_trades.length > 0 && (
                  <div>
                    <p className="text-sm text-zinc-500 mb-2">Recent Trades</p>
                    <div className="space-y-2">
                      {selectedTrader.recent_trades.slice(0, 5).map((trade, i) => (
                        <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[#050505]">
                          <div className="flex items-center gap-2">
                            <Badge className={trade.side === 'buy' ? 'bg-[#00FF94]/20 text-[#00FF94]' : 'bg-red-400/20 text-red-400'}>
                              {trade.side?.toUpperCase()}
                            </Badge>
                            <span className="font-mono">{trade.symbol}</span>
                          </div>
                          <span className={`font-mono ${trade.pnl >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                            {formatPnl(trade.pnl)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {!isPro && (
                  <div className="p-3 rounded-lg bg-[#7B61FF]/10 border border-[#7B61FF]/30 text-center">
                    <p className="text-sm text-zinc-400">
                      Upgrade to Pro to see full trade history and copy this trader
                    </p>
                  </div>
                )}

                {isPro && selectedTrader.user_id !== user?.id && (
                  <Button
                    onClick={() => { setFollowTarget(selectedTrader); setFollowModalOpen(true); setTraderDetailOpen(false); }}
                    className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90"
                    data-testid="follow-from-profile-btn"
                  >
                    <Copy className="w-4 h-4 mr-2" /> Copy This Trader
                  </Button>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Follow Trader Modal */}
        {followTarget && (
          <FollowTraderModal
            open={followModalOpen}
            onOpenChange={setFollowModalOpen}
            traderId={followTarget.user_id}
            traderName={followTarget.display_name || `Trader_${followTarget.user_id?.slice(0,6)}`}
            token={tokens?.access_token}
            onSuccess={() => toast.success('Navigate to Copy Trading to manage your follows')}
          />
        )}
      </div>
    </div>
  );
};

// ============= SPLASH SCREEN =============
const SplashScreen = ({ onComplete }) => {
  return (
    <motion.div
      className="fixed inset-0 z-[100] bg-[#050505] flex items-center justify-center"
      initial={{ opacity: 1 }}
      animate={{ opacity: 0 }}
      transition={{ delay: 1.8, duration: 0.5, ease: "easeInOut" }}
      onAnimationComplete={onComplete}
      data-testid="splash-screen"
    >
      {/* Ambient glow */}
      <motion.div
        className="absolute w-[300px] h-[300px] rounded-full"
        style={{ background: "radial-gradient(circle, rgba(123,97,255,0.15) 0%, transparent 70%)" }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: [0, 1.6, 1.2], opacity: [0, 0.8, 0.4] }}
        transition={{ duration: 1.2, ease: "easeOut" }}
      />

      <div className="flex flex-col items-center relative">
        {/* Icon */}
        <motion.div
          className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#7B61FF] to-[#00FF94] flex items-center justify-center mb-5"
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.6, ease: [0.34, 1.56, 0.64, 1] }}
        >
          <Brain className="w-12 h-12 text-white" />
        </motion.div>

        {/* Title */}
        <motion.span
          className="text-4xl font-bold font-['Outfit'] tracking-tight"
          initial={{ opacity: 0, y: 15, filter: "blur(8px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{ delay: 0.4, duration: 0.5, ease: "easeOut" }}
        >
          AlphaAI
        </motion.span>

        {/* Subtitle with line reveal */}
        <motion.div className="mt-2 overflow-hidden">
          <motion.span
            className="block text-sm text-zinc-400 font-light tracking-[0.25em] uppercase"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.75, duration: 0.5, ease: "easeOut" }}
          >
            Signal Intelligence System
          </motion.span>
        </motion.div>

        {/* Accent line */}
        <motion.div
          className="mt-4 h-[1px] bg-gradient-to-r from-transparent via-[#7B61FF] to-transparent"
          initial={{ width: 0 }}
          animate={{ width: 160 }}
          transition={{ delay: 1.0, duration: 0.6, ease: "easeOut" }}
        />
      </div>
    </motion.div>
  );
};

// Main App
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
        <AnimatePresence>
          {showSplash && <SplashScreen onComplete={handleSplashComplete} />}
        </AnimatePresence>
        <div className="App min-h-screen bg-[#050505]">
          <BrowserRouter>
            <Navigation />
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/leaderboard" element={<LeaderboardPage />} />
              <Route path="/copy-trading" element={<CopyTradingPage />} />
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
      </WalletProvider>
    </AuthProvider>
  );
}

export default App;
