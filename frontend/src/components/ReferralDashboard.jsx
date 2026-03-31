/**
 * AlphaAI Referral Dashboard
 * - Unique referral link generation
 * - Earnings tracking and stats
 * - Activity history
 * - Payout requests
 * - Tier progress
 */
import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Input } from '../components/ui/input';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter
} from '../components/ui/dialog';
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from '../components/ui/select';
import {
  Users, DollarSign, Link2, Copy, Check, Gift, TrendingUp,
  Award, Clock, ArrowUpRight, Share2, Twitter, MessageCircle,
  Mail, Zap, Crown, Star, ChevronRight, Wallet, AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Tier Badge Component
const TierBadge = ({ tier, color, size = "default" }) => {
  const sizeClasses = size === "large" ? "px-4 py-2 text-base" : "px-2 py-1 text-xs";
  
  return (
    <Badge 
      className={`${sizeClasses} font-bold`}
      style={{ backgroundColor: `${color}20`, color: color, borderColor: color }}
    >
      {tier === "Gold" && <Crown className="w-3 h-3 mr-1" />}
      {tier === "Platinum" && <Star className="w-3 h-3 mr-1" />}
      {tier}
    </Badge>
  );
};

// Stats Card Component
const StatsCard = ({ icon: Icon, label, value, subtext, color = "#7B61FF" }) => (
  <Card className="glass-card">
    <CardContent className="p-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-zinc-500 mb-1">{label}</p>
          <p className="text-2xl font-bold font-['JetBrains_Mono']" style={{ color }}>
            {value}
          </p>
          {subtext && <p className="text-xs text-zinc-600 mt-1">{subtext}</p>}
        </div>
        <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}20` }}>
          <Icon className="w-5 h-5" style={{ color }} />
        </div>
      </div>
    </CardContent>
  </Card>
);

// Referral Link Component
const ReferralLinkCard = ({ code, link, onCopy }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(link);
    setCopied(true);
    onCopy?.();
    setTimeout(() => setCopied(false), 2000);
  };

  const shareOnTwitter = () => {
    const text = encodeURIComponent(`Join me on My-AlphaAI and get 7 days FREE Pro access! AI-powered crypto trading signals`);
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${encodeURIComponent(link)}`, '_blank');
  };

  const shareOnTelegram = () => {
    const text = encodeURIComponent(`Join me on My-AlphaAI and get 7 days FREE Pro access!`);
    window.open(`https://t.me/share/url?url=${encodeURIComponent(link)}&text=${text}`, '_blank');
  };

  return (
    <Card className="glass-card border-[#7B61FF]/30">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Link2 className="w-5 h-5 text-[#7B61FF]" />
          Your Referral Link
        </CardTitle>
        <CardDescription>Share to earn 20-35% commission + 7 days free Pro</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex gap-2 mb-4">
          <div className="flex-1 relative">
            <Input
              value={link}
              readOnly
              className="pr-20 bg-[#050505] border-zinc-800 font-mono text-sm"
            />
            <Button
              size="sm"
              onClick={handleCopy}
              className="absolute right-1 top-1/2 -translate-y-1/2 h-7 bg-[#7B61FF] hover:bg-[#7B61FF]/90"
            >
              {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              {copied ? 'Copied!' : 'Copy'}
            </Button>
          </div>
        </div>
        
        {/* Share buttons */}
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={shareOnTwitter} className="flex-1 border-zinc-700">
            <Twitter className="w-4 h-4 mr-2" />
            Twitter
          </Button>
          <Button variant="outline" size="sm" onClick={shareOnTelegram} className="flex-1 border-zinc-700">
            <MessageCircle className="w-4 h-4 mr-2" />
            Telegram
          </Button>
          <Button variant="outline" size="sm" className="flex-1 border-zinc-700" onClick={() => {
            navigator.clipboard.writeText(`Join me on My-AlphaAI and get 7 days FREE Pro access! ${link}`);
            toast.success('Share text copied!');
          }}>
            <Share2 className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
        
        {/* Referral code */}
        <div className="mt-4 p-3 rounded-lg bg-[#050505] border border-zinc-800 text-center">
          <p className="text-xs text-zinc-500 mb-1">Your Referral Code</p>
          <p className="text-2xl font-bold font-['JetBrains_Mono'] text-[#7B61FF] tracking-wider">{code}</p>
        </div>
      </CardContent>
    </Card>
  );
};

// Tier Progress Component
const TierProgress = ({ currentTier, tierColor, conversions, nextTier }) => {
  const progress = nextTier 
    ? ((conversions) / (conversions + nextTier.referrals_needed)) * 100 
    : 100;

  return (
    <Card className="glass-card">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Award className="w-5 h-5 text-[#FFB800]" />
            Your Tier
          </CardTitle>
          <TierBadge tier={currentTier} color={tierColor} size="large" />
        </div>
      </CardHeader>
      <CardContent>
        {nextTier ? (
          <>
            <div className="flex justify-between text-sm mb-2">
              <span className="text-zinc-400">Progress to {nextTier.label}</span>
              <span className="text-zinc-300">{nextTier.referrals_needed} more referrals</span>
            </div>
            <Progress value={progress} className="h-2 mb-3" />
            <div className="flex justify-between text-xs text-zinc-500">
              <span>{currentTier} ({Math.round(progress)}%)</span>
              <span>{nextTier.label} ({Math.round(nextTier.commission_rate * 100)}% commission)</span>
            </div>
          </>
        ) : (
          <div className="text-center py-4">
            <Star className="w-8 h-8 text-[#FFD700] mx-auto mb-2" />
            <p className="text-zinc-300">You've reached the highest tier!</p>
            <p className="text-sm text-zinc-500">Enjoying maximum 35% commission</p>
          </div>
        )}
        
        {/* Tier Benefits */}
        <div className="mt-4 pt-4 border-t border-zinc-800">
          <p className="text-xs text-zinc-500 mb-2">Your Benefits:</p>
          <div className="grid grid-cols-2 gap-2">
            <div className="p-2 rounded-lg bg-[#050505] text-center">
              <p className="text-lg font-bold text-[#00FF94]">{currentTier === "Bronze" ? 20 : currentTier === "Silver" ? 25 : currentTier === "Gold" ? 30 : 35}%</p>
              <p className="text-xs text-zinc-500">Commission Rate</p>
            </div>
            <div className="p-2 rounded-lg bg-[#050505] text-center">
              <p className="text-lg font-bold text-[#7B61FF]">7 days</p>
              <p className="text-xs text-zinc-500">Free Pro / Referral</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Activity Item Component
const ActivityItem = ({ activity }) => {
  const getIcon = () => {
    switch (activity.type) {
      case 'signup': return <Users className="w-4 h-4 text-blue-400" />;
      case 'conversion': return <DollarSign className="w-4 h-4 text-[#00FF94]" />;
      case 'payout': return <Wallet className="w-4 h-4 text-[#FFB800]" />;
      default: return <Clock className="w-4 h-4 text-zinc-400" />;
    }
  };

  const getMessage = () => {
    switch (activity.type) {
      case 'signup': 
        return `${activity.referee_email} signed up using your link`;
      case 'conversion': 
        return `${activity.referee_email} upgraded to ${activity.plan}`;
      case 'payout': 
        return `Payout of $${activity.amount?.toFixed(2)} ${activity.status}`;
      default: 
        return 'Activity';
    }
  };

  const statusColors = {
    pending: 'text-yellow-400',
    converted: 'text-[#00FF94]',
    completed: 'text-[#00FF94]',
    failed: 'text-red-400'
  };

  return (
    <div className="flex items-center gap-3 p-3 rounded-lg bg-[#050505] border border-zinc-800">
      <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center">
        {getIcon()}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm text-zinc-300 truncate">{getMessage()}</p>
        <p className="text-xs text-zinc-600">
          {new Date(activity.timestamp).toLocaleDateString()}
        </p>
      </div>
      {activity.amount && activity.type === 'conversion' && (
        <div className="text-right">
          <p className="text-sm font-bold text-[#00FF94]">+${activity.amount.toFixed(2)}</p>
          <p className="text-xs text-zinc-500">commission</p>
        </div>
      )}
      <Badge className={`${statusColors[activity.status]} bg-transparent border-0 text-xs`}>
        {activity.status}
      </Badge>
    </div>
  );
};

// Payout Modal Component
const PayoutModal = ({ open, onClose, availableBalance, onSubmit }) => {
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('');
  const [details, setDetails] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!amount || !method || !details) {
      toast.error('Please fill all fields');
      return;
    }

    if (parseFloat(amount) > availableBalance) {
      toast.error('Insufficient balance');
      return;
    }

    if (parseFloat(amount) < 25) {
      toast.error('Minimum payout is $25');
      return;
    }

    setLoading(true);
    await onSubmit({
      amount: parseFloat(amount),
      method,
      details: { [method]: details }
    });
    setLoading(false);
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="bg-[#121212] border-zinc-800">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Wallet className="w-5 h-5 text-[#00FF94]" />
            Request Payout
          </DialogTitle>
          <DialogDescription>
            Minimum payout: $25. Processing time: 3-5 business days.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div>
            <label className="text-sm text-zinc-400 mb-1 block">Available Balance</label>
            <p className="text-2xl font-bold text-[#00FF94]">${availableBalance.toFixed(2)}</p>
          </div>
          
          <div>
            <label className="text-sm text-zinc-400 mb-1 block">Payout Amount</label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
              <Input
                type="number"
                min="25"
                max={availableBalance}
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Enter amount"
                className="pl-9 bg-[#050505] border-zinc-800"
              />
            </div>
          </div>
          
          <div>
            <label className="text-sm text-zinc-400 mb-1 block">Payout Method</label>
            <Select value={method} onValueChange={setMethod}>
              <SelectTrigger className="bg-[#050505] border-zinc-800">
                <SelectValue placeholder="Select method" />
              </SelectTrigger>
              <SelectContent className="bg-[#121212] border-zinc-800">
                <SelectItem value="paypal">PayPal</SelectItem>
                <SelectItem value="crypto">Crypto (USDC)</SelectItem>
                <SelectItem value="bank_transfer">Bank Transfer</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label className="text-sm text-zinc-400 mb-1 block">
              {method === 'paypal' ? 'PayPal Email' : 
               method === 'crypto' ? 'USDC Wallet Address (Ethereum)' : 
               'Bank Account Details'}
            </label>
            <Input
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              placeholder={
                method === 'paypal' ? 'your@email.com' :
                method === 'crypto' ? '0x...' :
                'Account number and routing'
              }
              className="bg-[#050505] border-zinc-800"
            />
          </div>
        </div>
        
        <DialogFooter>
          <Button variant="outline" onClick={onClose} className="border-zinc-700">
            Cancel
          </Button>
          <Button 
            onClick={handleSubmit} 
            disabled={loading}
            className="bg-[#00FF94] text-black hover:bg-[#00FF94]/90"
          >
            {loading ? 'Processing...' : 'Request Payout'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// Main Referral Dashboard Component
export const ReferralDashboard = () => {
  const { user, isAuthenticated } = useAuth();
  const [stats, setStats] = useState(null);
  const [activity, setActivity] = useState([]);
  const [earnings, setEarnings] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [payoutModalOpen, setPayoutModalOpen] = useState(false);

  const fetchData = useCallback(async () => {
    if (!isAuthenticated) return;
    
    setLoading(true);
    try {
      const [statsRes, activityRes, earningsRes, configRes] = await Promise.allSettled([
        axios.get(`${API}/referrals/stats`),
        axios.get(`${API}/referrals/activity`),
        axios.get(`${API}/referrals/earnings`),
        axios.get(`${API}/referrals/config`)
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value.data);
      if (activityRes.status === 'fulfilled') setActivity(activityRes.value.data.activity || []);
      if (earningsRes.status === 'fulfilled') setEarnings(earningsRes.value.data);
      if (configRes.status === 'fulfilled') setConfig(configRes.value.data);
    } catch (error) {
      console.error('Error fetching referral data:', error);
    }
    setLoading(false);
  }, [isAuthenticated]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handlePayout = async (payoutData) => {
    try {
      await axios.post(`${API}/referrals/request-payout`, null, {
        params: payoutData
      });
      toast.success('Payout request submitted!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Payout request failed');
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <Card className="glass-card max-w-md">
          <CardContent className="text-center py-8">
            <Users className="w-12 h-12 mx-auto text-[#7B61FF] mb-4" />
            <h3 className="text-xl font-bold mb-2">Join Our Referral Program</h3>
            <p className="text-zinc-400 mb-4">
              Earn up to 35% commission on every referral. Plus 7 days free Pro for you and your friends!
            </p>
            <Button className="bg-[#7B61FF]" onClick={() => window.location.href = '/login'}>
              Sign In to Get Started
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-32 rounded-xl bg-zinc-900/50" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-24 rounded-xl bg-zinc-900/50" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="referral-dashboard">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Gift className="w-7 h-7 text-[#7B61FF]" />
            Referral Program
          </h1>
          <p className="text-zinc-500">Earn commissions and free Pro access by sharing My-AlphaAI</p>
        </div>
        {stats?.available_earnings >= 25 && (
          <Button 
            onClick={() => setPayoutModalOpen(true)}
            className="bg-[#00FF94] text-black hover:bg-[#00FF94]/90"
          >
            <Wallet className="w-4 h-4 mr-2" />
            Request Payout
          </Button>
        )}
      </div>

      {/* Referral Link Card */}
      {stats && (
        <ReferralLinkCard 
          code={stats.referral_code} 
          link={stats.referral_link}
          onCopy={() => toast.success('Referral link copied!')}
        />
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard
          icon={Users}
          label="Total Referrals"
          value={stats?.total_referrals || 0}
          subtext={`${stats?.pending_referrals || 0} pending`}
          color="#7B61FF"
        />
        <StatsCard
          icon={TrendingUp}
          label="Conversions"
          value={stats?.converted_referrals || 0}
          subtext={`${stats?.commission_rate ? Math.round(stats.commission_rate * 100) : 20}% rate`}
          color="#00FF94"
        />
        <StatsCard
          icon={DollarSign}
          label="Total Earnings"
          value={`$${(stats?.total_earnings || 0).toFixed(2)}`}
          subtext={`$${(stats?.available_earnings || 0).toFixed(2)} available`}
          color="#FFB800"
        />
        <StatsCard
          icon={Zap}
          label="Free Days Earned"
          value={stats?.free_days_earned || 0}
          subtext="Pro subscription"
          color="#FF6B6B"
        />
      </div>

      {/* Main Content */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Tier Progress */}
        <div className="md:col-span-1">
          {stats && (
            <TierProgress
              currentTier={stats.tier}
              tierColor={stats.tier_color}
              conversions={stats.converted_referrals}
              nextTier={stats.next_tier}
            />
          )}
          
          {/* Commission Tiers */}
          <Card className="glass-card mt-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Commission Tiers</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {config?.tiers?.map((tier, i) => (
                <div 
                  key={i}
                  className={`flex items-center justify-between p-2 rounded-lg ${
                    stats?.tier === tier.name ? 'bg-[#7B61FF]/10 border border-[#7B61FF]/30' : 'bg-[#050505]'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <div 
                      className="w-3 h-3 rounded-full" 
                      style={{ backgroundColor: tier.color }}
                    />
                    <span className="text-sm">{tier.name}</span>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold" style={{ color: tier.color }}>
                      {tier.commission_rate}
                    </span>
                    <span className="text-xs text-zinc-500 ml-1">
                      ({tier.min_referrals}+ refs)
                    </span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* Activity Feed */}
        <div className="md:col-span-2">
          <Card className="glass-card">
            <CardHeader className="pb-2">
              <CardTitle className="flex items-center gap-2 text-lg">
                <Clock className="w-5 h-5 text-blue-400" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              {activity.length > 0 ? (
                <div className="space-y-2 max-h-[400px] overflow-y-auto">
                  {activity.map((item, i) => (
                    <ActivityItem key={i} activity={item} />
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 mx-auto text-zinc-700 mb-3" />
                  <p className="text-zinc-500">No referral activity yet</p>
                  <p className="text-sm text-zinc-600">Share your link to get started!</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* How it Works */}
          <Card className="glass-card mt-4">
            <CardHeader className="pb-2">
              <CardTitle className="text-base">How It Works</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <div className="w-10 h-10 rounded-full bg-[#7B61FF]/20 flex items-center justify-center mx-auto mb-2">
                    <Share2 className="w-5 h-5 text-[#7B61FF]" />
                  </div>
                  <p className="text-sm font-medium">1. Share</p>
                  <p className="text-xs text-zinc-500">Send your unique link</p>
                </div>
                <div>
                  <div className="w-10 h-10 rounded-full bg-[#00FF94]/20 flex items-center justify-center mx-auto mb-2">
                    <Users className="w-5 h-5 text-[#00FF94]" />
                  </div>
                  <p className="text-sm font-medium">2. They Join</p>
                  <p className="text-xs text-zinc-500">Friend gets 7 days free</p>
                </div>
                <div>
                  <div className="w-10 h-10 rounded-full bg-[#FFB800]/20 flex items-center justify-center mx-auto mb-2">
                    <DollarSign className="w-5 h-5 text-[#FFB800]" />
                  </div>
                  <p className="text-sm font-medium">3. Earn</p>
                  <p className="text-xs text-zinc-500">20-35% commission</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Payout Modal */}
      <PayoutModal
        open={payoutModalOpen}
        onClose={() => setPayoutModalOpen(false)}
        availableBalance={stats?.available_earnings || 0}
        onSubmit={handlePayout}
      />
    </div>
  );
};

export default ReferralDashboard;
