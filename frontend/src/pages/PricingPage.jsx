/**
 * AlphaAI Tier System Components
 * Tier badges, upgrade CTAs, lock overlays, and pricing section.
 */
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import axios from 'axios';
import { toast } from 'sonner';
import { useAuth } from '../contexts/AuthContext';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription
} from '../components/ui/dialog';
import {
  Lock, Crown, Zap, Shield, ArrowRight, Check, Loader2, Star
} from 'lucide-react';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

// ============= TIER BADGE =============
export const TierBadge = ({ tier = 'free', size = 'sm' }) => {
  const config = {
    free: { label: 'Free', className: 'bg-zinc-700/50 text-zinc-300 border-zinc-600' },
    pro: { label: 'Pro', className: 'bg-[#7B61FF]/20 text-[#7B61FF] border-[#7B61FF]/30' },
    elite: { label: 'Elite', className: 'bg-[#FFB800]/20 text-[#FFB800] border-[#FFB800]/30' },
  };
  const c = config[tier] || config.free;
  const sizeClass = size === 'lg' ? 'text-sm px-3 py-1' : 'text-xs px-2 py-0.5';

  return (
    <Badge className={`${c.className} border ${sizeClass} font-medium`} data-testid={`tier-badge-${tier}`}>
      {tier === 'elite' && <Crown className="w-3 h-3 mr-1" />}
      {tier === 'pro' && <Zap className="w-3 h-3 mr-1" />}
      {c.label}
    </Badge>
  );
};

// ============= LOCK OVERLAY for restricted features =============
export const FeatureLock = ({ requiredTier = 'pro', children, feature = 'this feature' }) => {
  const { user } = useAuth();
  const userTier = user?.user_tier || 'free';
  const tierOrder = { free: 0, pro: 1, elite: 2 };
  const hasAccess = tierOrder[userTier] >= tierOrder[requiredTier];

  if (hasAccess) return children;

  return (
    <div className="relative" data-testid={`feature-lock-${feature}`}>
      <div className="pointer-events-none opacity-30 blur-[2px] select-none">
        {children}
      </div>
      <div className="absolute inset-0 flex items-center justify-center bg-black/40 backdrop-blur-sm rounded-lg">
        <div className="text-center p-4">
          <Lock className="w-6 h-6 mx-auto text-zinc-400 mb-2" />
          <p className="text-sm text-zinc-300 mb-2">
            Requires <TierBadge tier={requiredTier} />
          </p>
          <Button asChild size="sm" className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 rounded-full text-xs">
            <Link to="/pricing">Upgrade Now</Link>
          </Button>
        </div>
      </div>
    </div>
  );
};

// ============= UPGRADE BANNER for dashboard =============
export const UpgradeBanner = ({ className = '' }) => {
  const { user } = useAuth();
  const tier = user?.user_tier || 'free';

  if (tier !== 'free') return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`relative overflow-hidden rounded-xl border border-[#7B61FF]/30 bg-gradient-to-r from-[#7B61FF]/10 via-[#050505] to-[#00FF94]/10 p-4 ${className}`}
      data-testid="upgrade-banner"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#7B61FF]/20 flex items-center justify-center">
            <Zap className="w-5 h-5 text-[#7B61FF]" />
          </div>
          <div>
            <p className="font-medium text-sm">You&apos;re on the Free plan</p>
            <p className="text-xs text-zinc-500">Signals are delayed 15 min. Upgrade for real-time signals, live trading, and more.</p>
          </div>
        </div>
        <Button asChild size="sm" className="bg-[#7B61FF] hover:bg-[#7B61FF]/90 rounded-full shrink-0">
          <Link to="/pricing" data-testid="upgrade-banner-btn">
            Upgrade <ArrowRight className="w-3 h-3 ml-1" />
          </Link>
        </Button>
      </div>
    </motion.div>
  );
};

// ============= PAPER TRADING BADGE =============
export const PaperTradingBadge = () => {
  const { user } = useAuth();
  const tier = user?.user_tier || 'free';

  if (tier !== 'free') return null;

  return (
    <Badge className="bg-[#FFB800]/15 text-[#FFB800] border border-[#FFB800]/30 text-xs" data-testid="paper-trading-badge">
      Paper Trading Mode
    </Badge>
  );
};

// ============= INLINE UPGRADE CTA =============
export const InlineUpgradeCTA = ({ feature, requiredTier = 'pro' }) => {
  return (
    <div className="flex items-center gap-2 p-3 rounded-lg bg-[#7B61FF]/10 border border-[#7B61FF]/20" data-testid={`upgrade-cta-${feature}`}>
      <Lock className="w-4 h-4 text-[#7B61FF] shrink-0" />
      <p className="text-sm text-zinc-400">
        <span className="text-white">{feature}</span> requires {requiredTier === 'elite' ? 'Elite' : 'Pro'}.
      </p>
      <Button asChild size="sm" variant="ghost" className="ml-auto text-[#7B61FF] hover:text-[#7B61FF]/80 shrink-0">
        <Link to="/pricing">Upgrade <ArrowRight className="w-3 h-3 ml-1" /></Link>
      </Button>
    </div>
  );
};

// ============= PRICING PAGE =============
const PricingPage = () => {
  const { user, tokens } = useAuth();
  const userTier = user?.user_tier || 'free';
  const [loading, setLoading] = useState(null);
  const [billingPeriod, setBillingPeriod] = useState('monthly');

  const handleCheckout = async (packageId) => {
    setLoading(packageId);
    try {
      const res = await axios.post(`${API}/payments/checkout`, {
        package_id: packageId,
        origin_url: window.location.origin,
        wallet_address: user?.wallet_address || 'demo_user',
        user_email: user?.email || '',
      });
      if (res.data.checkout_url) {
        window.location.href = res.data.checkout_url;
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to create checkout session');
    }
    setLoading(null);
  };

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      period: 'forever',
      description: 'Explore AlphaAI with paper trading',
      features: [
        { text: 'AI signals (15-min delay)', included: true },
        { text: 'Paper trading', included: true },
        { text: 'Top 10 leaderboard', included: true },
        { text: 'Basic portfolio view', included: true },
        { text: 'Real-time signals', included: false },
        { text: 'Live trading', included: false },
        { text: 'Copy Trading', included: false },
        { text: 'Advanced analytics', included: false },
      ],
      cta: userTier === 'free' ? 'Current Plan' : null,
      disabled: true,
    },
    {
      id: 'pro',
      name: 'Pro',
      monthlyPrice: 29,
      yearlyPrice: 249,
      monthlyPkgId: 'pro_monthly',
      yearlyPkgId: 'pro_yearly',
      popular: true,
      description: 'Full trading power unlocked',
      features: [
        { text: 'Real-time AI signals', included: true },
        { text: 'Live trading enabled', included: true },
        { text: 'Copy Trading access', included: true },
        { text: 'Full leaderboard access', included: true },
        { text: 'Follow & be followed', included: true },
        { text: 'Advanced analytics', included: true },
        { text: 'Push notifications', included: true },
        { text: 'Priority support', included: true },
      ],
      cta: userTier === 'pro' ? 'Current Plan' : 'Upgrade to Pro',
      disabled: userTier === 'pro' || userTier === 'elite',
    },
    {
      id: 'elite',
      name: 'Elite',
      monthlyPrice: 79,
      yearlyPrice: 699,
      monthlyPkgId: 'elite_monthly',
      yearlyPkgId: 'elite_yearly',
      description: 'Maximum edge for serious traders',
      features: [
        { text: 'Everything in Pro', included: true },
        { text: 'Priority signal delivery', included: true },
        { text: 'Early access to features', included: true },
        { text: 'Higher rate limits', included: true },
        { text: 'Advanced research tools', included: true },
        { text: 'Dedicated support', included: true },
      ],
      cta: userTier === 'elite' ? 'Current Plan' : 'Upgrade to Elite',
      disabled: userTier === 'elite',
    },
  ];

  return (
    <div className="min-h-screen pt-24 pb-16 px-4" data-testid="pricing-page">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold font-['Outfit'] mb-3" data-testid="pricing-title">
            Choose Your Plan
          </h1>
          <p className="text-zinc-400 text-lg max-w-xl mx-auto">
            Start free. Upgrade when you&apos;re ready for real-time signals and live trading.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center gap-3 mt-8">
            <button onClick={() => setBillingPeriod('monthly')}
              className={`px-4 py-2 rounded-full text-sm transition-colors ${billingPeriod === 'monthly' ? 'bg-[#7B61FF] text-white' : 'bg-zinc-800 text-zinc-400'}`}
              data-testid="billing-monthly-btn"
            >Monthly</button>
            <button onClick={() => setBillingPeriod('yearly')}
              className={`px-4 py-2 rounded-full text-sm transition-colors ${billingPeriod === 'yearly' ? 'bg-[#7B61FF] text-white' : 'bg-zinc-800 text-zinc-400'}`}
              data-testid="billing-yearly-btn"
            >
              Yearly <span className="text-xs text-[#00FF94] ml-1">Save ~30%</span>
            </button>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-3 gap-6">
          {plans.map((plan, i) => {
            const price = plan.id === 'free' ? 0 : billingPeriod === 'monthly' ? plan.monthlyPrice : plan.yearlyPrice;
            const pkgId = plan.id === 'free' ? null : billingPeriod === 'monthly' ? plan.monthlyPkgId : plan.yearlyPkgId;
            const isCurrentTier = plan.id === userTier;

            return (
              <motion.div key={plan.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
                <Card className={`relative h-full ${plan.popular ? 'border-[#7B61FF] bg-[#7B61FF]/5' : 'border-zinc-800 bg-[#0A0A0A]'} ${isCurrentTier ? 'ring-2 ring-[#7B61FF]/50' : ''}`}
                  data-testid={`plan-card-${plan.id}`}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <Badge className="bg-[#7B61FF] text-white px-3 py-1 text-xs">Most Popular</Badge>
                    </div>
                  )}

                  <CardHeader className="pt-8 pb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <CardTitle className="text-xl font-['Outfit']">{plan.name}</CardTitle>
                      {isCurrentTier && <Badge className="bg-[#00FF94]/20 text-[#00FF94] text-xs">Current</Badge>}
                    </div>
                    <p className="text-sm text-zinc-500">{plan.description}</p>
                    <div className="mt-4">
                      <span className="text-4xl font-bold font-mono">${price}</span>
                      {plan.id !== 'free' && (
                        <span className="text-zinc-500 text-sm ml-1">/{billingPeriod === 'monthly' ? 'mo' : 'yr'}</span>
                      )}
                    </div>
                    {billingPeriod === 'yearly' && plan.id !== 'free' && (
                      <p className="text-xs text-[#00FF94] mt-1">
                        Save ${plan.id === 'pro' ? '99' : '249'}/year
                      </p>
                    )}
                  </CardHeader>

                  <CardContent className="space-y-3 pb-8">
                    {plan.features.map((f, j) => (
                      <div key={j} className="flex items-center gap-2 text-sm">
                        {f.included ? (
                          <Check className="w-4 h-4 text-[#00FF94] shrink-0" />
                        ) : (
                          <Lock className="w-4 h-4 text-zinc-600 shrink-0" />
                        )}
                        <span className={f.included ? 'text-zinc-300' : 'text-zinc-600'}>{f.text}</span>
                      </div>
                    ))}

                    <div className="pt-4">
                      {plan.id === 'free' ? (
                        <Button disabled className="w-full" variant="outline" data-testid="plan-free-btn">
                          {isCurrentTier ? 'Current Plan' : 'Free Forever'}
                        </Button>
                      ) : (
                        <Button
                          onClick={() => pkgId && handleCheckout(pkgId)}
                          disabled={plan.disabled || !!loading}
                          className={`w-full ${plan.popular ? 'bg-[#7B61FF] hover:bg-[#7B61FF]/90' : 'bg-zinc-800 hover:bg-zinc-700'}`}
                          data-testid={`plan-${plan.id}-btn`}
                        >
                          {loading === pkgId ? <Loader2 className="w-4 h-4 animate-spin" /> : (
                            isCurrentTier ? 'Current Plan' : plan.cta
                          )}
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* FAQ */}
        <div className="mt-16 text-center">
          <p className="text-zinc-500 text-sm">
            All plans include paper trading. Upgrade or downgrade anytime. Payments secured by Stripe.
          </p>
        </div>
      </div>
    </div>
  );
};

export default PricingPage;
