import { motion } from "framer-motion";
import { Users, Gift, Share2, Copy, Trophy, DollarSign } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { toast } from "sonner";
import { PageHeader, StatsRow, LoadingSkeleton, ErrorState } from "../components/PlaceholderUI";
import { useDemoMode } from "../contexts/DemoModeContext";
import { useAuth } from "../contexts/AuthContext";
import { useApiData } from "../lib/useApiData";

const ReferralPage = () => {
  const { isDemoMode } = useDemoMode();
  const { tokens } = useAuth();
  const token = tokens?.access_token;

  const { data: refStats, loading, error, refetch } = useApiData('/referrals/stats', { skip: isDemoMode || !token, token });
  const { data: refActivity } = useApiData('/referrals/activity', { skip: isDemoMode || !token, token });

  const referralCode = refStats?.referral_code || 'YOUR_CODE';
  const referralLink = `${window.location.origin}/register?ref=${referralCode}`;

  const stats = isDemoMode || !refStats ? [
    { label: 'Total Referrals', value: '0', change: 'Get started', positive: true },
    { label: 'Active Users', value: '0', change: 'From referrals', positive: true },
    { label: 'Earnings', value: '$0.00', change: '20% commission', positive: true },
    { label: 'Conversion Rate', value: '--', change: 'No data yet', positive: true },
  ] : [
    { label: 'Total Referrals', value: String(refStats.total_referrals ?? 0), change: `${refStats.active_referrals ?? 0} active`, positive: true },
    { label: 'Active Users', value: String(refStats.active_referrals ?? 0), change: 'From referrals', positive: true },
    { label: 'Earnings', value: `$${(refStats.total_earnings ?? 0).toFixed(2)}`, change: '20% commission', positive: (refStats.total_earnings ?? 0) > 0 },
    { label: 'Conversion Rate', value: refStats.conversion_rate ? `${refStats.conversion_rate.toFixed(1)}%` : '--', change: 'Clicks to signups', positive: true },
  ];

  const tiers = [
    { min: 0, label: 'Starter', reward: '20% commission', color: 'text-zinc-400' },
    { min: 10, label: 'Builder', reward: '25% commission', color: 'text-[#7B61FF]' },
    { min: 25, label: 'Champion', reward: '30% + Pro month', color: 'text-[#00FF94]' },
    { min: 50, label: 'Legend', reward: '35% + Elite month', color: 'text-[#FFB800]' },
  ];

  const copyLink = () => {
    navigator.clipboard.writeText(referralLink);
    toast.success('Referral link copied!');
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="referral-page">
      <div className="max-w-5xl mx-auto">
        <PageHeader icon={Users} title="Referral Program" description="Earn commissions by inviting traders to AlphaAI" badge="20% Commission" testId="referral-header" />

        {loading && !isDemoMode ? <LoadingSkeleton rows={3} /> : error && !isDemoMode ? <ErrorState message="Could not load referral data" onRetry={refetch} /> : (
          <>
            <StatsRow stats={stats} />

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-3"><CardTitle className="text-sm font-medium flex items-center gap-2"><Share2 className="w-4 h-4 text-[#7B61FF]" /> Your Referral Link</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex gap-3">
                    <Input value={referralLink} readOnly className="bg-[#050505] border-zinc-800 text-sm font-mono text-zinc-400" data-testid="referral-link-input" />
                    <Button onClick={copyLink} className="rounded-xl bg-[#7B61FF] hover:bg-[#7B61FF]/90 shrink-0"><Copy className="w-4 h-4 mr-2" /> Copy</Button>
                  </div>
                  <p className="text-[11px] text-zinc-600 mt-2">Share this link with friends. You earn 20% of their subscription for the first 12 months.</p>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="mb-8">
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-3"><CardTitle className="text-sm font-medium flex items-center gap-2"><Trophy className="w-4 h-4 text-[#FFB800]" /> Reward Tiers</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-4 gap-3">
                    {tiers.map((tier, i) => (
                      <div key={i} className={`p-4 rounded-lg border ${i === 0 ? 'bg-[#7B61FF]/5 border-[#7B61FF]/20' : 'bg-[#050505] border-zinc-800/30'}`}>
                        <div className="flex items-center gap-2 mb-2">
                          <Gift className={`w-4 h-4 ${tier.color}`} />
                          <span className={`text-sm font-semibold ${tier.color}`}>{tier.label}</span>
                        </div>
                        <p className="text-xs text-zinc-500">{tier.min}+ referrals</p>
                        <p className="text-xs text-zinc-300 mt-1 font-medium">{tier.reward}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50">
                <CardHeader className="pb-3"><CardTitle className="text-sm font-medium">How It Works</CardTitle></CardHeader>
                <CardContent>
                  <div className="grid sm:grid-cols-3 gap-6">
                    {[
                      { step: '01', title: 'Share Your Link', desc: 'Send your unique referral link to traders who want an edge' },
                      { step: '02', title: 'They Subscribe', desc: 'When they sign up for Pro or Elite, you start earning' },
                      { step: '03', title: 'Earn Commissions', desc: '20-35% of their subscription, paid monthly for 12 months' },
                    ].map((s, i) => (
                      <div key={i} className="flex gap-3">
                        <span className="text-2xl font-bold font-mono text-[#7B61FF]/30">{s.step}</span>
                        <div>
                          <h4 className="text-sm font-semibold text-zinc-200 mb-1">{s.title}</h4>
                          <p className="text-xs text-zinc-600 leading-relaxed">{s.desc}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
};

export default ReferralPage;
