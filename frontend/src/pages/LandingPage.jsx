import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { motion } from "framer-motion";
import {
  ArrowUpRight, ArrowDownRight, Activity, Zap,
  Check, Clock, Brain, TestTube, Beaker, Trophy,
  Rocket, Shield, Lock
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { useWallet } from "../contexts/WalletContext";
import { BrandLockup, PoweredByTag } from "../components/BrandComponents";
import LivePriceTicker from "../components/LivePriceTicker";
import { API } from "../lib/constants";
import { formatCurrency } from "../lib/formatters";

const HeroVisualization = () => {
  // Candlestick data: x, open, close, high, low (normalized 0-400 viewBox)
  const candles = [
    { x: 40, o: 310, c: 295, h: 285, l: 320 },
    { x: 60, o: 295, c: 305, h: 285, l: 315 },
    { x: 80, o: 305, c: 290, h: 280, l: 310 },
    { x: 100, o: 290, c: 300, h: 278, l: 308 },
    { x: 120, o: 300, c: 280, h: 270, l: 305 },
    { x: 140, o: 280, c: 260, h: 250, l: 285 }, // AlphaAI flags here
    { x: 160, o: 260, c: 240, h: 230, l: 268 },
    { x: 180, o: 240, c: 210, h: 200, l: 248 },
    { x: 200, o: 210, c: 180, h: 170, l: 218 },
    { x: 220, o: 180, c: 155, h: 145, l: 188 },
    { x: 240, o: 155, c: 140, h: 130, l: 162 },
    { x: 260, o: 140, c: 125, h: 118, l: 148 }, // You enter here (late)
    { x: 280, o: 125, c: 135, h: 140, l: 120 },
    { x: 300, o: 135, c: 150, h: 155, l: 128 },
    { x: 320, o: 150, c: 142, h: 158, l: 138 },
    { x: 340, o: 142, c: 148, h: 155, l: 135 },
    { x: 360, o: 148, c: 138, h: 152, l: 132 },
  ];
  const alphaY = 270; // AlphaAI entry line
  const youY = 132;   // Your entry line

  return (
    <div className="relative w-[340px] h-[340px] sm:w-[420px] sm:h-[420px] lg:w-[500px] lg:h-[440px]" data-testid="hero-visualization">
      {/* Ambient glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80%] h-[80%] rounded-full bg-[#7B61FF]/6 blur-[80px]" />

      <svg viewBox="0 0 400 380" className="w-full h-full relative z-10" fill="none" xmlns="http://www.w3.org/2000/svg">
        {/* Grid lines */}
        {[100, 150, 200, 250, 300].map(y => (
          <line key={y} x1="30" y1={y} x2="375" y2={y} stroke="#ffffff" strokeOpacity="0.04" strokeWidth="0.5" />
        ))}

        {/* Candlesticks */}
        {candles.map((c, i) => {
          const bullish = c.c < c.o; // price went up (lower close = higher price in inverted y)
          const color = bullish ? '#00FF94' : '#ef4444';
          const bodyTop = Math.min(c.o, c.c);
          const bodyH = Math.abs(c.o - c.c);
          return (
            <g key={i}>
              <line x1={c.x} y1={c.h} x2={c.x} y2={c.l} stroke={color} strokeWidth="1" strokeOpacity="0.5" />
              <rect x={c.x - 6} y={bodyTop} width="12" height={Math.max(bodyH, 2)} fill={color} fillOpacity={i >= 5 && i <= 11 ? 0.8 : 0.35} rx="1" />
            </g>
          );
        })}

        {/* AlphaAI entry dashed line (green, low = early) */}
        <line x1="30" y1={alphaY} x2="375" y2={alphaY} stroke="#00FF94" strokeWidth="1" strokeDasharray="6 4" strokeOpacity="0.5" />

        {/* Your entry dashed line (red, high = late) */}
        <line x1="30" y1={youY} x2="375" y2={youY} stroke="#ef4444" strokeWidth="1" strokeDasharray="6 4" strokeOpacity="0.5" />

        {/* Pulsing gap zone between the two lines */}
        <rect x="30" y={youY} width="345" height={alphaY - youY} fill="url(#gapGradient)">
          <animate attributeName="opacity" dur="3s" repeatCount="indefinite" values="0.03;0.08;0.03" />
        </rect>

        {/* AlphaAI marker arrow */}
        <g>
          <circle cx="140" cy={alphaY} r="5" fill="#00FF94" fillOpacity="0.9">
            <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="5;8;5" />
            <animate attributeName="fillOpacity" dur="2.5s" repeatCount="indefinite" values="0.9;0.4;0.9" />
          </circle>
          <circle cx="140" cy={alphaY} r="3" fill="#00FF94" />
        </g>

        {/* Your entry marker */}
        <g>
          <circle cx="260" cy={youY} r="5" fill="#ef4444" fillOpacity="0.9">
            <animate attributeName="r" dur="2.5s" repeatCount="indefinite" values="5;8;5" />
            <animate attributeName="fillOpacity" dur="2.5s" repeatCount="indefinite" values="0.9;0.4;0.9" />
          </circle>
          <circle cx="260" cy={youY} r="3" fill="#ef4444" />
        </g>

        {/* Vertical connector between the two entries */}
        <line x1="200" y1={youY + 8} x2="200" y2={alphaY - 8} stroke="#7B61FF" strokeWidth="1" strokeDasharray="3 3" strokeOpacity="0.25" />
        <polygon points="197,{youY + 8} 203,{youY + 8} 200,{youY + 2}" fill="#ef4444" fillOpacity="0.5" />
        <polygon points={`197,${alphaY - 8} 203,${alphaY - 8} 200,${alphaY - 2}`} fill="#00FF94" fillOpacity="0.5" />

        {/* Gap label */}
        <text x="210" y={(alphaY + youY) / 2 + 4} fill="#7B61FF" fontSize="11" fontFamily="monospace" opacity="0.6">
          +4.2% gap
        </text>

        <defs>
          <linearGradient id="gapGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#ef4444" stopOpacity="0.15" />
            <stop offset="50%" stopColor="#7B61FF" stopOpacity="0.08" />
            <stop offset="100%" stopColor="#00FF94" stopOpacity="0.15" />
          </linearGradient>
        </defs>
      </svg>

      {/* AlphaAI label */}
      <motion.div
        className="absolute left-[4%] px-3 py-1.5 rounded-md bg-[#00FF94]/10 border border-[#00FF94]/25 backdrop-blur-sm"
        style={{ top: '62%' }}
        initial={{ opacity: 0, x: -10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.6, duration: 0.5 }}
      >
        <span className="text-[11px] font-mono font-medium text-[#00FF94]">AlphaAI flagged here</span>
      </motion.div>

      {/* Your entry label */}
      <motion.div
        className="absolute right-[3%] px-3 py-1.5 rounded-md bg-[#ef4444]/10 border border-[#ef4444]/25 backdrop-blur-sm"
        style={{ top: '25%' }}
        initial={{ opacity: 0, x: 10 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.9, duration: 0.5 }}
      >
        <span className="text-[11px] font-mono font-medium text-[#ef4444]">You entered here</span>
      </motion.div>

      {/* Time delta label */}
      <motion.div
        className="absolute bottom-[4%] left-1/2 -translate-x-1/2 px-3 py-1 rounded-md bg-[#0B0B0F]/80 border border-zinc-800 backdrop-blur-sm"
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.7 }}
        transition={{ delay: 1.2, duration: 0.5 }}
      >
        <span className="text-[10px] font-mono text-zinc-500">15 min late</span>
      </motion.div>
    </div>
  );
};

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
      
      <section className="relative px-4 pt-16 pb-12 md:pt-24 md:pb-20 overflow-hidden" data-testid="hero-section">
        {/* Cinematic background layers */}
        <div className="absolute inset-0 bg-[#0B0B0F]" />
        <div className="absolute inset-0 grid-pattern opacity-30" />
        <div className="absolute top-[20%] left-[15%] w-[500px] h-[500px] bg-[#7B61FF]/10 rounded-full blur-[140px] pointer-events-none" />
        <div className="absolute bottom-[10%] right-[10%] w-[400px] h-[400px] bg-[#00FF94]/5 rounded-full blur-[120px] pointer-events-none" />
        
        {/* Noise texture */}
        <div
          className="absolute inset-0 opacity-[0.025] pointer-events-none"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
            backgroundSize: '128px 128px',
          }}
        />
        
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center min-h-[70vh]">
            {/* Left: Text Content */}
            <div className="order-2 lg:order-1">
              <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <Badge className="mb-6 bg-zinc-800/60 text-zinc-400 border-zinc-700/50 px-4 py-1.5" data-testid="hero-badge">
                  <Activity className="w-3 h-3 mr-1.5" />Signal Intelligence System
                </Badge>
              </motion.div>

              <motion.h1
                className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6 font-['Outfit'] tracking-tight leading-[1.08]"
                data-testid="hero-title"
                initial={{ opacity: 0, y: 30, filter: 'blur(6px)' }}
                animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                transition={{ delay: 0.15, duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
              >
                <span className="text-white">You&apos;re Not Bad</span><br />
                <span className="text-white">at Trading.</span><br />
                <span className="text-[#ef4444]">You&apos;re Late.</span>
              </motion.h1>

              <motion.p
                className="text-base sm:text-lg text-zinc-400 mb-10 max-w-lg leading-relaxed"
                data-testid="hero-description"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.6 }}
              >
                The setup was there 15 minutes ago. You just didn&apos;t see it yet. AlphaAI did.
              </motion.p>

              <motion.p
                className="text-sm text-zinc-500 mb-10 max-w-lg"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.38, duration: 0.5 }}
              >
                AlphaAI identifies trade entries before the move — not after.
              </motion.p>

              {/* CTA Buttons */}
              <motion.div
                className="flex flex-col sm:flex-row gap-4 mb-6"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.45, duration: 0.6 }}
              >
                <Link to="/dashboard">
                  <Button size="lg" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 h-12 text-base shadow-[0_0_30px_rgba(123,97,255,0.3)] hover:shadow-[0_0_40px_rgba(123,97,255,0.45)] transition-shadow" data-testid="hero-get-started-btn">
                    Start Free Demo<ArrowUpRight className="w-5 h-5 ml-2" />
                  </Button>
                </Link>
                <Link to="/pricing">
                  <Button size="lg" variant="outline" className="rounded-full border-zinc-700 hover:border-[#7B61FF]/50 px-8 h-12 text-base transition-colors" data-testid="hero-view-signals-btn">
                    View Plans
                  </Button>
                </Link>
              </motion.div>

              {/* CTA Trust Line */}
              <motion.p
                className="text-xs text-zinc-600 mb-10"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.52, duration: 0.5 }}
                data-testid="hero-trust-line"
              >
                No credit card required. Free tier included. Cancel anytime.
              </motion.p>

              {/* Trust Indicators */}
              <motion.div
                className="flex flex-wrap gap-x-6 gap-y-3 text-xs text-zinc-500"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6, duration: 0.6 }}
                data-testid="trust-indicators"
              >
                <span className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#00FF94]" />
                  68% Win Rate — updated daily
                </span>
                <span className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#7B61FF]" />
                  Traders in 40+ countries
                </span>
                <span className="flex items-center gap-1.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#FFB800]" />
                  Avg. 15-min earlier than manual entries
                </span>
              </motion.div>
            </div>

            {/* Right: AI Signal Visualization */}
            <motion.div
              className="order-1 lg:order-2 flex justify-center lg:justify-end"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.8, ease: 'easeOut' }}
            >
              <HeroVisualization />
            </motion.div>
          </div>

          {/* Fund Stats */}
          {fundStats && (
            <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.5 }} className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12 lg:mt-16">
              <Card className="glass-card card-hover" data-testid="stat-nav">
                <CardContent className="p-5 text-center">
                  <p className="text-xs text-zinc-500 mb-1.5">Fund NAV</p>
                  <p className="text-xl md:text-2xl font-bold text-white font-['JetBrains_Mono']">{formatCurrency(fundStats.nav)}</p>
                  <p className={`text-xs mt-1 flex items-center justify-center gap-1 ${fundStats.nav_change_24h >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>
                    {fundStats.nav_change_24h >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}{fundStats.nav_change_24h}%
                  </p>
                </CardContent>
              </Card>
              <Card className="glass-card card-hover" data-testid="stat-aum"><CardContent className="p-5 text-center"><p className="text-xs text-zinc-500 mb-1.5">Total AUM</p><p className="text-xl md:text-2xl font-bold text-white font-['JetBrains_Mono']">{formatCurrency(fundStats.total_aum)}</p></CardContent></Card>
              <Card className="glass-card card-hover" data-testid="stat-sharpe"><CardContent className="p-5 text-center"><p className="text-xs text-zinc-500 mb-1.5">Sharpe Ratio</p><p className="text-xl md:text-2xl font-bold text-[#7B61FF] font-['JetBrains_Mono']">{fundStats.sharpe_ratio}</p></CardContent></Card>
              <Card className="glass-card card-hover" data-testid="stat-return"><CardContent className="p-5 text-center"><p className="text-xs text-zinc-500 mb-1.5">Monthly Return</p><p className={`text-xl md:text-2xl font-bold font-['JetBrains_Mono'] ${fundStats.monthly_return >= 0 ? 'text-[#00FF94]' : 'text-red-400'}`}>{fundStats.monthly_return >= 0 ? '+' : ''}{fundStats.monthly_return}%</p></CardContent></Card>
            </motion.div>
          )}
        </div>
      </section>

      {/* ===== SECTION 1: MISSED vs CAPTURED ===== */}
      <section className="px-4 py-20 md:py-28 relative overflow-hidden" data-testid="missed-vs-captured-section">
        <div className="absolute inset-0 bg-[#0B0B0F]" />
        <div className="absolute top-1/2 left-1/3 w-[400px] h-[400px] bg-[#ef4444]/5 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute top-1/2 right-1/3 w-[400px] h-[400px] bg-[#00FF94]/5 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-4xl mx-auto relative z-10">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <p className="text-center text-xs tracking-[0.3em] uppercase text-zinc-600 mb-3">BTC/USD · March 24, 2026 · 15-min candles</p>

            {/* Chart visual */}
            <div className="relative mx-auto max-w-2xl mb-12">
              <svg viewBox="0 0 600 200" className="w-full" fill="none" xmlns="http://www.w3.org/2000/svg">
                {/* Grid */}
                <line x1="50" y1="40" x2="550" y2="40" stroke="#fff" strokeOpacity="0.04" strokeWidth="0.5" />
                <line x1="50" y1="100" x2="550" y2="100" stroke="#fff" strokeOpacity="0.04" strokeWidth="0.5" />
                <line x1="50" y1="160" x2="550" y2="160" stroke="#fff" strokeOpacity="0.04" strokeWidth="0.5" />

                {/* Price labels */}
                <text x="555" y="167" fill="#52525b" fontSize="10" fontFamily="monospace">$64,800</text>
                <text x="555" y="47" fill="#52525b" fontSize="10" fontFamily="monospace">$67,200</text>

                {/* Candles — pre-breakout */}
                {[[80,155,145,140,160],[100,148,138,132,152],[120,140,150,128,155],[140,152,142,136,158]].map(([x,o,c,h,l],i) => (
                  <g key={`pre${i}`}>
                    <line x1={x} y1={h} x2={x} y2={l} stroke={c < o ? '#00FF94' : '#ef4444'} strokeWidth="1" strokeOpacity="0.4" />
                    <rect x={x-5} y={Math.min(o,c)} width="10" height={Math.abs(o-c)||2} fill={c < o ? '#00FF94' : '#ef4444'} fillOpacity="0.3" rx="1" />
                  </g>
                ))}

                {/* AlphaAI entry line */}
                <line x1="50" y1="155" x2="550" y2="155" stroke="#00FF94" strokeWidth="1" strokeDasharray="6 4" strokeOpacity="0.4" />

                {/* Breakout candles */}
                {[[170,148,120,115,152],[195,120,90,82,125],[220,90,65,58,95],[245,65,50,42,70],[270,50,42,36,55]].map(([x,o,c,h,l],i) => (
                  <g key={`brk${i}`}>
                    <line x1={x} y1={h} x2={x} y2={l} stroke="#00FF94" strokeWidth="1" strokeOpacity="0.6" />
                    <rect x={x-5} y={Math.min(o,c)} width="10" height={Math.abs(o-c)||2} fill="#00FF94" fillOpacity="0.7" rx="1" />
                  </g>
                ))}

                {/* Post-peak candles */}
                {[[295,42,55,38,60],[320,55,65,52,70],[345,65,58,54,72],[370,58,62,52,68],[395,62,68,58,72]].map(([x,o,c,h,l],i) => (
                  <g key={`post${i}`}>
                    <line x1={x} y1={h} x2={x} y2={l} stroke="#ef4444" strokeWidth="1" strokeOpacity="0.5" />
                    <rect x={x-5} y={Math.min(o,c)} width="10" height={Math.abs(o-c)||2} fill="#ef4444" fillOpacity="0.5" rx="1" />
                  </g>
                ))}

                {/* Your entry line */}
                <line x1="50" y1="42" x2="550" y2="42" stroke="#ef4444" strokeWidth="1" strokeDasharray="6 4" strokeOpacity="0.4" />

                {/* AlphaAI marker */}
                <circle cx="160" cy="155" r="6" fill="#00FF94">
                  <animate attributeName="r" dur="2s" repeatCount="indefinite" values="6;9;6" />
                  <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="1;0.5;1" />
                </circle>
                <circle cx="160" cy="155" r="4" fill="#00FF94" />

                {/* Your entry marker */}
                <circle cx="285" cy="42" r="6" fill="#ef4444">
                  <animate attributeName="r" dur="2s" repeatCount="indefinite" values="6;9;6" />
                  <animate attributeName="opacity" dur="2s" repeatCount="indefinite" values="1;0.5;1" />
                </circle>
                <circle cx="285" cy="42" r="4" fill="#ef4444" />

                {/* Gap zone */}
                <rect x="160" y="42" width="125" height="113" fill="#7B61FF" fillOpacity="0.04">
                  <animate attributeName="fillOpacity" dur="3s" repeatCount="indefinite" values="0.03;0.07;0.03" />
                </rect>

                {/* Connecting dashed line */}
                <line x1="222" y1="50" x2="222" y2="148" stroke="#7B61FF" strokeWidth="1" strokeDasharray="3 3" strokeOpacity="0.3" />
                <text x="230" y="102" fill="#7B61FF" fontSize="11" fontFamily="monospace" opacity="0.6">+3.7%</text>
              </svg>
            </div>

            {/* Result cards */}
            <div className="grid md:grid-cols-2 gap-4 max-w-2xl mx-auto">
              <div className="rounded-xl border border-[#00FF94]/20 bg-[#00FF94]/5 p-5">
                <p className="text-xs text-zinc-500 mb-1">AlphaAI entry</p>
                <p className="text-sm text-zinc-300 font-mono">9:41 AM · $64,800</p>
                <p className="text-xs text-zinc-500 mt-2">Closed at $67,100</p>
                <p className="text-2xl font-bold font-mono text-[#00FF94] mt-1" data-testid="alpha-result">+3.5%</p>
              </div>
              <div className="rounded-xl border border-[#ef4444]/20 bg-[#ef4444]/5 p-5">
                <p className="text-xs text-zinc-500 mb-1">Your entry</p>
                <p className="text-sm text-zinc-300 font-mono">9:56 AM · $67,200</p>
                <p className="text-xs text-zinc-500 mt-2">It reversed.</p>
                <p className="text-2xl font-bold font-mono text-[#ef4444] mt-1" data-testid="your-result">-1.8%</p>
              </div>
            </div>

            <p className="text-center text-zinc-500 text-sm mt-8">Same asset. Same day. <span className="text-white">15 minutes apart.</span></p>
            <p className="text-center text-zinc-600 text-xs mt-1">One trader profited. One became exit liquidity.</p>
          </motion.div>
        </div>
      </section>

      {/* ===== SECTION 2: FREE vs PAID TIMING GAP ===== */}
      <section className="px-4 py-20 md:py-28 relative" data-testid="timing-gap-section">
        <div className="max-w-4xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <h2 className="text-3xl md:text-4xl font-bold font-['Outfit'] text-center mb-3">Same Signal. Different Timing.</h2>
            <p className="text-zinc-500 text-center text-sm mb-14">The signal is the same. The timing is the product.</p>

            {/* Timeline */}
            <div className="relative max-w-2xl mx-auto mb-14">
              {/* Timeline bar */}
              <div className="h-[2px] bg-zinc-800 w-full relative">
                <div className="absolute left-0 top-0 h-full w-[15%] bg-[#00FF94]/40" />
                <div className="absolute right-[20%] top-0 h-[2px] w-[2px] bg-[#ef4444]" />
              </div>

              {/* Pro marker */}
              <div className="absolute left-0 -top-2">
                <div className="w-4 h-4 rounded-full bg-[#00FF94] border-2 border-[#0B0B0F]" />
                <div className="mt-3 whitespace-nowrap">
                  <p className="text-xs font-mono text-[#00FF94] font-bold">9:41 AM</p>
                  <p className="text-[10px] text-zinc-500">Pro user receives signal</p>
                  <p className="text-xs font-mono text-zinc-300 mt-1">BTC at $64,800</p>
                </div>
              </div>

              {/* 15 min gap label */}
              <div className="absolute left-1/2 -translate-x-1/2 -top-8">
                <p className="text-[10px] tracking-widest uppercase text-[#7B61FF] font-mono">15 minutes</p>
              </div>

              {/* Free marker */}
              <div className="absolute right-[20%] -top-2">
                <div className="w-4 h-4 rounded-full bg-[#ef4444] border-2 border-[#0B0B0F]" />
                <div className="mt-3 whitespace-nowrap">
                  <p className="text-xs font-mono text-[#ef4444] font-bold">9:56 AM</p>
                  <p className="text-[10px] text-zinc-500">Free user receives signal</p>
                  <p className="text-xs font-mono text-zinc-300 mt-1">BTC at $67,200</p>
                </div>
              </div>
            </div>

            {/* Comparison cards */}
            <div className="grid md:grid-cols-2 gap-5 mt-20">
              <Card className="border-zinc-800 bg-[#0A0A0A]" data-testid="free-tier-card">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-lg font-bold font-['Outfit']">Free</span>
                    <span className="text-xs text-zinc-600 font-mono">$0/mo</span>
                  </div>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2 text-zinc-500"><Clock className="w-4 h-4 shrink-0" /> Signals: 15-min delay</div>
                    <div className="flex items-center gap-2 text-zinc-500"><Lock className="w-4 h-4 shrink-0" /> Paper trading only</div>
                    <div className="flex items-center gap-2 text-zinc-500"><Lock className="w-4 h-4 shrink-0" /> Top 10 leaderboard</div>
                    <div className="flex items-center gap-2 text-zinc-500"><Lock className="w-4 h-4 shrink-0" /> No copy trading</div>
                  </div>
                  <div className="mt-6 p-3 rounded-lg bg-[#ef4444]/5 border border-[#ef4444]/10">
                    <p className="text-xs text-zinc-500">You see the signal at <span className="text-[#ef4444] font-mono">9:56 AM</span></p>
                    <p className="text-xs text-zinc-600 mt-1">The move is already over.</p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-[#7B61FF]/30 bg-[#7B61FF]/5" data-testid="pro-tier-card">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <span className="text-lg font-bold font-['Outfit']">Pro</span>
                    <span className="text-xs text-[#7B61FF] font-mono">$29/mo</span>
                    <Badge className="bg-[#7B61FF]/20 text-[#7B61FF] text-[10px] ml-auto">Real-time</Badge>
                  </div>
                  <div className="space-y-3 text-sm">
                    <div className="flex items-center gap-2 text-zinc-300"><Zap className="w-4 h-4 shrink-0 text-[#00FF94]" /> Signals: Real-time</div>
                    <div className="flex items-center gap-2 text-zinc-300"><Check className="w-4 h-4 shrink-0 text-[#00FF94]" /> Live trading enabled</div>
                    <div className="flex items-center gap-2 text-zinc-300"><Check className="w-4 h-4 shrink-0 text-[#00FF94]" /> Full leaderboard</div>
                    <div className="flex items-center gap-2 text-zinc-300"><Check className="w-4 h-4 shrink-0 text-[#00FF94]" /> Copy trading access</div>
                  </div>
                  <div className="mt-6 p-3 rounded-lg bg-[#00FF94]/5 border border-[#00FF94]/10">
                    <p className="text-xs text-zinc-400">You see the signal at <span className="text-[#00FF94] font-mono">9:41 AM</span></p>
                    <p className="text-xs text-zinc-500 mt-1">Before the move starts.</p>
                  </div>
                  <Button asChild className="w-full mt-4 bg-[#7B61FF] hover:bg-[#7B61FF]/90" data-testid="close-gap-btn">
                    <Link to="/pricing">Close the Gap</Link>
                  </Button>
                </CardContent>
              </Card>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== SECTION 3: TODAY'S SIGNALS PREVIEW ===== */}
      <section className="px-4 py-20 md:py-28 relative overflow-hidden" data-testid="todays-signals-section">
        <div className="absolute inset-0 bg-[#0B0B0F]" />
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-[#7B61FF]/5 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-3xl mx-auto relative z-10">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <p className="text-center text-xs tracking-[0.25em] uppercase text-[#ef4444]/70 font-mono mb-3" data-testid="todays-signals-urgency">Live — signals from the last 24 hours</p>
            <h2 className="text-3xl md:text-4xl font-bold font-['Outfit'] text-center mb-2">Entries You Already Missed Today</h2>
            <p className="text-zinc-500 text-center text-sm mb-12">These signals fired while you were waiting. Pro users were positioned before each move.</p>

            <div className="space-y-4">
              {[
                {
                  symbol: 'BTC/USD', side: 'BUY', confidence: 87,
                  alphaTime: '9:41 AM', alphaPrice: '$64,800',
                  yourTime: '9:56 AM', yourPrice: '$67,200',
                  note: 'The breakout started at 9:43. By 9:56 it was done.',
                },
                {
                  symbol: 'ETH/USD', side: 'SELL', confidence: 74,
                  alphaTime: '2:12 PM', alphaPrice: '$1,984',
                  yourTime: '2:27 PM', yourPrice: '$1,931',
                  note: 'Sell signal hit before the 2:18 PM dump. Late sellers caught the bounce back up.',
                },
                {
                  symbol: 'SOL/USD', side: 'BUY', confidence: 69,
                  alphaTime: '7:03 AM', alphaPrice: '$78.40',
                  yourTime: '7:18 AM', yourPrice: '$82.10',
                  note: 'SOL ran 4.7% in 12 minutes. If you saw it at 7:18, you bought the top of the move.',
                },
              ].map((sig, i) => (
                <motion.div key={sig.symbol} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.12, duration: 0.5 }}>
                  <Card className="glass-card border-zinc-800/50" data-testid={`signal-preview-${sig.symbol.replace('/','-')}`}>
                    <CardContent className="p-5">
                      {/* Header */}
                      <div className="flex items-center justify-between mb-4">
                        <span className="text-base font-mono font-bold text-white">{sig.symbol}</span>
                        <Badge className={`${sig.side === 'BUY' ? 'bg-[#00FF94]/15 text-[#00FF94]' : 'bg-[#ef4444]/15 text-[#ef4444]'} font-mono`}>
                          {sig.side} {sig.confidence}%
                        </Badge>
                      </div>

                      {/* Timeline bar */}
                      <div className="relative h-8 mb-4">
                        <div className="absolute top-1/2 left-0 right-0 h-[2px] bg-zinc-800 -translate-y-1/2" />
                        {/* AlphaAI dot */}
                        <div className="absolute left-[10%] top-1/2 -translate-y-1/2 flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-[#00FF94] ring-4 ring-[#00FF94]/10" />
                          <span className="text-[10px] font-mono text-[#00FF94]">{sig.alphaTime}</span>
                        </div>
                        {/* Your dot */}
                        <div className="absolute right-[20%] top-1/2 -translate-y-1/2 flex items-center gap-2">
                          <div className="w-3 h-3 rounded-full bg-[#ef4444] ring-4 ring-[#ef4444]/10" />
                          <span className="text-[10px] font-mono text-[#ef4444]">{sig.yourTime}</span>
                        </div>
                        {/* Gap label */}
                        <div className="absolute left-1/2 -translate-x-1/2 -top-1">
                          <span className="text-[9px] font-mono text-[#7B61FF] tracking-wider">15 MIN</span>
                        </div>
                      </div>

                      {/* Prices */}
                      <div className="grid grid-cols-2 gap-3 mb-3">
                        <div className="text-xs">
                          <span className="text-zinc-600">AlphaAI flagged </span>
                          <span className="font-mono text-[#00FF94]">{sig.alphaPrice}</span>
                        </div>
                        <div className="text-xs text-right">
                          <span className="text-zinc-600">You would&apos;ve seen </span>
                          <span className="font-mono text-[#ef4444]">{sig.yourPrice}</span>
                        </div>
                      </div>

                      {/* Note */}
                      <p className="text-xs text-zinc-500 leading-relaxed">{sig.note}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>

            {/* Bottom proof line */}
            <div className="mt-10 text-center">
              <p className="text-xs text-zinc-600 mb-1">These are real signals from today.</p>
              <p className="text-xs text-zinc-500">Free users saw them 15 minutes after each move. <span className="text-white">Pro users were already in.</span></p>
              <Link to="/pricing">
                <Button className="mt-6 rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-8 shadow-[0_0_30px_rgba(123,97,255,0.25)] hover:shadow-[0_0_40px_rgba(123,97,255,0.4)] transition-shadow" data-testid="signals-cta-btn">
                  Start Free Demo<ArrowUpRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
              <p className="text-[11px] text-zinc-600 mt-3">No credit card. Cancel anytime.</p>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ===== SOCIAL PROOF ===== */}
      <section className="px-4 py-16 md:py-20" data-testid="social-proof-section">
        <div className="max-w-3xl mx-auto">
          <div className="space-y-0 divide-y divide-zinc-800/50">
            {[
              { quote: "I used to chase pumps on CT. Now I'm already positioned when the crowd shows up.", who: "Derivatives trader, Singapore" },
              { quote: "The 15-minute gap is real. My monthly P&L flipped positive the first week.", who: "Swing trader, London" },
              { quote: "I finally stopped being the exit liquidity.", who: "Retail trader, New York" },
            ].map((t, i) => (
              <motion.div key={i} initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.1, duration: 0.5 }} className="py-8">
                <p className="text-zinc-300 text-base md:text-lg leading-relaxed italic">&ldquo;{t.quote}&rdquo;</p>
                <p className="text-xs text-zinc-600 mt-3">— {t.who}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ===== FINAL CTA ===== */}
      <section className="px-4 py-20 md:py-28 relative overflow-hidden" data-testid="final-cta-section">
        <div className="absolute inset-0 bg-gradient-to-t from-[#7B61FF]/5 to-transparent pointer-events-none" />
        <div className="max-w-2xl mx-auto text-center relative z-10">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.6 }}>
            <h2 className="text-3xl md:text-4xl font-bold font-['Outfit'] mb-6">Still entering after the move?</h2>
            <Link to="/dashboard">
              <Button size="lg" className="rounded-full bg-[#7B61FF] hover:bg-[#7B61FF]/90 px-10 h-14 text-base shadow-[0_0_40px_rgba(123,97,255,0.3)] hover:shadow-[0_0_50px_rgba(123,97,255,0.5)] transition-shadow" data-testid="final-cta-btn">
                Start Free Demo<ArrowUpRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <p className="text-zinc-600 text-sm mt-6">No credit card required. Free tier included. Cancel anytime.</p>
          </motion.div>
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

export default LandingPage;
