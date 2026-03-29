import { motion } from "framer-motion";
import {
  Store, Star, Users, Search, ShoppingCart
} from "lucide-react";
import { Card, CardContent } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { PageHeader, StatsRow } from "../components/PlaceholderUI";
import { mockMarketplaceItems } from "../lib/mockData";
import { useDemoMode } from "../contexts/DemoModeContext";

const MarketplacePage = () => {
  const { isDemoMode, demoMarketplace } = useDemoMode();
  const marketplaceItems = isDemoMode ? demoMarketplace : mockMarketplaceItems;
  const stats = [
    { label: 'Listed Items', value: '24', change: '+6 this month', positive: true },
    { label: 'Active Users', value: '4.2K', change: '+12%', positive: true },
    { label: 'Avg Rating', value: '4.7', change: 'out of 5', positive: true },
    { label: 'Total Revenue', value: '$18.4K', change: 'Marketplace fees', positive: true },
  ];

  const categoryColors = {
    'Trading Bot': 'bg-[#7B61FF]/15 text-[#7B61FF]',
    'Signal Plugin': 'bg-[#00FF94]/15 text-[#00FF94]',
    'Portfolio Tool': 'bg-[#FFB800]/15 text-[#FFB800]',
    'On-chain': 'bg-blue-400/15 text-blue-400',
  };

  return (
    <div className="min-h-screen pt-24 pb-12 px-4" data-testid="marketplace-page">
      <div className="max-w-7xl mx-auto">
        <PageHeader
          icon={Store}
          title="Marketplace"
          description="Browse and install trading bots, signal plugins, and portfolio tools"
          testId="marketplace-header"
        />

        {/* Search */}
        <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-600" />
            <Input
              placeholder="Search bots, plugins, and tools..."
              className="bg-[#0A0A0A] border-zinc-800/50 h-12 pl-11 rounded-xl text-sm"
              data-testid="marketplace-search"
            />
          </div>
        </motion.div>

        <StatsRow stats={stats} />

        {/* Marketplace Items */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {marketplaceItems.map((item, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.08 }}>
              <Card className="bg-[#0A0A0A] border-zinc-800/50 hover:border-zinc-700/50 transition-colors" data-testid={`marketplace-item-${i}`}>
                <CardContent className="p-5">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-sm font-semibold text-zinc-200 mb-1">{item.name}</h3>
                      <p className="text-xs text-zinc-600">by {item.creator}</p>
                    </div>
                    <Badge className={categoryColors[item.category]}>{item.category}</Badge>
                  </div>

                  <div className="flex items-center gap-4 mb-4 text-xs text-zinc-500">
                    <span className="flex items-center gap-1">
                      <Star className="w-3 h-3 text-[#FFB800]" /> {item.rating}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-3 h-3" /> {item.users.toLocaleString()} users
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-sm font-mono font-bold text-[#7B61FF]">{item.price}</span>
                    <Button disabled size="sm" className="rounded-full bg-[#7B61FF]/20 text-[#7B61FF]/60 text-xs">
                      <ShoppingCart className="w-3 h-3 mr-1" /> Install
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default MarketplacePage;
