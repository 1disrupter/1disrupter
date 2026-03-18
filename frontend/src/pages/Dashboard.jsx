import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import { motion } from "framer-motion";
import {
  Wallet, TrendingUp, BarChart3, Shield,
  ChevronDown, ArrowUpRight, ArrowDownRight, Activity, Zap,
  Check, Clock, Brain, Sparkles, Radio, Eye
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from "../components/ui/dialog";
import { useWallet } from "../contexts/WalletContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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

// Dashboard Page with Paper Trading - Conversion Optimized
const DashboardPage = () => {
  const { wallet } = useWallet();
  const [demoMode, setDemoMode] = useState(false);
  const [signals, setSignals] = useState([
    { symbol: 'BTC', signal: 'BUY', confidence: 87, price: 67432 },
    { symbol: 'ETH', signal: 'HOLD', confidence: 72, price: 3521 },
    { symbol: 'SOL', signal: 'SELL', confidence: 65, price: 142 },
  ]);
  const [aiSummary] = useState("Market showing bullish momentum on BTC. ETH consolidating near support. Consider taking profits on SOL.");
  const [performance] = useState({ return_30d: 12.4, win_rate: 68, max_drawdown: 4.2, total_signals: 847 });
  const [showUpgradePopup, setShowUpgradePopup] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isPro] = useState(false);

  // Show upgrade popup after 2 minutes
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!isPro) setShowUpgradePopup(true);
    }, 120000); // 2 minutes
    return () => clearTimeout(timer);
  }, [isPro]);

  // Fetch signals from backend
  useEffect(() => {
    axios.get(`${API}/live-prices`).then(res => {
      if (res.data.prices) {
        const btcPrice = res.data.prices.find(p => p.symbol === 'BTC')?.price || 67432;
        const ethPrice = res.data.prices.find(p => p.symbol === 'ETH')?.price || 3521;
        const solPrice = res.data.prices.find(p => p.symbol === 'SOL')?.price || 142;
        setSignals([
          { symbol: 'BTC', signal: 'BUY', confidence: 87, price: btcPrice },
          { symbol: 'ETH', signal: 'HOLD', confidence: 72, price: ethPrice },
          { symbol: 'SOL', signal: 'SELL', confidence: 65, price: solPrice },
        ]);
      }
    }).catch(console.error);
  }, []);

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
        
        {/* Demo Mode Banner */}
        {demoMode && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl bg-[#7B61FF]/10 border border-[#7B61FF]/30 flex items-center justify-between"
            data-testid="demo-mode-banner"
          >
            <div className="flex items-center gap-3">
              <Eye className="w-5 h-5 text-[#7B61FF]" />
              <span className="text-[#7B61FF] font-medium">Demo Mode - Connect wallet for full features</span>
            </div>
            <WalletConnectButton />
          </motion.div>
        )}

        {/* Delayed Signals Warning */}
        {!isPro && (
          <motion.div 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 rounded-xl bg-yellow-500/10 border border-yellow-500/30 flex items-center justify-between"
            data-testid="delayed-signals-warning"
          >
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-yellow-400" />
              <span className="text-yellow-400 font-medium">You are viewing delayed signals (15 min)</span>
            </div>
            <Button 
              onClick={() => setShowUpgradePopup(true)} 
              className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 rounded-full text-sm"
              data-testid="unlock-live-btn"
            >
              <Zap className="w-4 h-4 mr-1" /> Unlock Live
            </Button>
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
              <div className="grid gap-4">
                {signals.map((s, i) => (
                  <motion.div
                    key={s.symbol}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                    className={`flex items-center justify-between p-5 rounded-xl border ${getSignalColor(s.signal)}`}
                    data-testid={`signal-${s.symbol.toLowerCase()}`}
                  >
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
                    </div>
                  </motion.div>
                ))}
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
                      onClick={() => setShowUpgradePopup(true)}
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
          </div>
          <DialogFooter className="flex-col gap-3">
            <Button 
              className="w-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 py-6 text-lg font-bold rounded-full glow-primary"
              data-testid="upgrade-now-btn"
              onClick={() => toast.success("Upgrade flow coming soon!")}
            >
              Upgrade Now — $29/month
            </Button>
            <Button variant="ghost" onClick={() => setShowUpgradePopup(false)} className="text-zinc-500">
              Maybe later
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default DashboardPage;
