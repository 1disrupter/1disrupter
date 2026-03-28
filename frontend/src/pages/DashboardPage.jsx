import { useState, useEffect, useMemo, useCallback } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { motion, AnimatePresence } from "framer-motion";
import {
  Wallet, TrendingUp, BarChart3, Shield,
  ChevronDown, ArrowUpRight, ArrowDownRight, Activity, Zap,
  AlertTriangle, Check, Clock, Users, Target, Brain,
  RefreshCw, Sparkles, Radio, Eye, PlayCircle, Lock
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Switch } from "../components/ui/switch";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from "../components/ui/dialog";
import { useWallet } from "../contexts/WalletContext";
import { useAuth } from "../contexts/AuthContext";
import { UpgradeBanner, PaperTradingBadge } from "./PricingPage";
import PerformanceMetrics from "../components/PerformanceMetrics";
import NotificationSettings from "../components/NotificationSettings";
import { PoweredByTag } from "../components/BrandComponents";
import LivePriceTicker from "../components/LivePriceTicker";
import { API } from "../lib/constants";

const WalletConnectButton = () => {
  const { connectWallet, loading } = useWallet();
  return (<Button onClick={connectWallet} disabled={loading} className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 glow-primary" data-testid="wallet-connect-btn"><Wallet className="w-5 h-5 mr-2" />{loading ? "Connecting..." : "Connect Wallet"}</Button>);
};


const DashboardPage = () => {
  const { wallet, investor, refreshInvestor } = useWallet();
  const { user: authUser } = useAuth();
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
  const userTier = authUser?.user_tier || (isPro ? 'pro' : 'free');

  // Sync isPro from auth context
  useEffect(() => {
    if (authUser?.user_tier && authUser.user_tier !== 'free') {
      setIsPro(true);
    }
  }, [authUser?.user_tier]);

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
      <div className="min-h-screen pt-24 px-4 pb-12" data-testid="dashboard-onboarding">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 rounded-lg bg-[#7B61FF]/10">
                <BarChart3 className="w-6 h-6 text-[#7B61FF]" />
              </div>
              <h1 className="text-3xl md:text-4xl font-bold font-['Outfit'] tracking-tight">Dashboard</h1>
            </div>
            <p className="text-zinc-500 text-sm md:text-base ml-0 md:ml-14">Real-time AI signals, portfolio tracking, and trading controls</p>
          </motion.div>

          {/* Preview Stats */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: 'Active Signals', value: '12', sub: 'Real-time' },
              { label: 'Win Rate', value: '68%', sub: 'Last 30 days' },
              { label: 'Avg Return', value: '+4.2%', sub: 'Per signal' },
              { label: 'Active Pairs', value: '8', sub: 'BTC, ETH, SOL...' },
            ].map((s, i) => (
              <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50">
                <CardContent className="p-5">
                  <p className="text-xs text-zinc-500 mb-1.5 uppercase tracking-wider">{s.label}</p>
                  <p className="text-xl font-bold font-['JetBrains_Mono'] text-white/40">{s.value}</p>
                  <p className="text-[11px] text-zinc-700 mt-1">{s.sub}</p>
                </CardContent>
              </Card>
            ))}
          </motion.div>

          {/* Connect Card */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card className="bg-[#0A0A0A] border-zinc-800/50" data-testid="connect-wallet-prompt">
              <CardContent className="p-8 text-center">
                <Wallet className="w-12 h-12 mx-auto mb-4 text-[#7B61FF]" />
                <h2 className="text-xl font-bold font-['Outfit'] mb-2">Connect to unlock your dashboard</h2>
                <p className="text-sm text-zinc-500 mb-6 max-w-md mx-auto">
                  Connect your wallet to view live AI signals, track your portfolio, and start trading
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
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
          </motion.div>

          {/* Preview Signal Cards */}
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="mt-8">
            <h3 className="text-sm text-zinc-600 uppercase tracking-wider mb-4">Recent Signal Preview</h3>
            <div className="grid md:grid-cols-3 gap-4 opacity-50">
              {[
                { pair: 'BTC/USD', side: 'BUY', conf: 87, price: '$67,240' },
                { pair: 'ETH/USD', side: 'SELL', conf: 74, price: '$1,984' },
                { pair: 'SOL/USD', side: 'BUY', conf: 69, price: '$82.10' },
              ].map((s, i) => (
                <Card key={i} className="bg-[#0A0A0A] border-zinc-800/50">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-mono font-bold">{s.pair}</span>
                      <Badge className={s.side === 'BUY' ? 'bg-[#00FF94]/15 text-[#00FF94]' : 'bg-[#ef4444]/15 text-[#ef4444]'}>{s.side}</Badge>
                    </div>
                    <p className="text-lg font-mono font-bold text-white/60">{s.price}</p>
                    <p className="text-xs text-zinc-600 mt-1">{s.conf}% confidence</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen pt-24 px-4 pb-12">
      <div className="max-w-4xl mx-auto">
        
        {/* Free Tier Upgrade Banner */}
        <UpgradeBanner className="mb-4" />
        
        {/* Paper Trading Mode Badge */}
        {!isPro && (
          <div className="mb-4 flex items-center gap-2">
            <PaperTradingBadge />
            <span className="text-xs text-zinc-600">Paper trades only. Upgrade for live trading.</span>
          </div>
        )}
        
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
                  <div className="relative">
                    <button 
                      onClick={isPro ? toggleTradingMode : undefined}
                      className={`w-12 h-6 rounded-full p-1 transition-colors ${tradingMode === 'live' ? 'bg-[#00FF94]' : 'bg-zinc-700'} ${!isPro ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                      data-testid="trading-mode-toggle"
                      disabled={!isPro}
                    >
                      <div className={`w-4 h-4 rounded-full bg-white transition-transform ${tradingMode === 'live' ? 'translate-x-6' : ''}`} />
                    </button>
                    {!isPro && (
                      <Lock className="w-3 h-3 text-zinc-500 absolute -top-1 -right-1" />
                    )}
                  </div>
                  <span className={`text-sm ${tradingMode === 'live' ? 'text-[#00FF94]' : 'text-zinc-500'}`}>Live</span>
                  {!isPro && <span className="text-xs text-zinc-600 ml-1">(Pro)</span>}
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
                    <span className="text-sm text-zinc-500">Starting at $49/month</span>
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
                  <p className="text-xl font-bold">$49<span className="text-sm text-zinc-400">/mo</span></p>
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
                  {selectedPackage === 'pro_monthly' ? 'Upgrade Now — $49/month' : 'Upgrade Now — $419/year'}
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
              <Zap className="w-5 h-5 mr-2" /> Upgrade Now — $49/month
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


export default DashboardPage;
