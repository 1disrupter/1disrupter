import { useState, useEffect } from "react";
import axios from "axios";
import { ArrowUpRight, ArrowDownRight, Radio, RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { API } from "../lib/constants";

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
    const interval = setInterval(fetchPrices, 30000);
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
      <div className="relative z-40 flex items-center gap-6 overflow-x-auto py-3 px-6 bg-[#050505] border-b border-zinc-800/60" data-testid="price-ticker-compact">
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

export default LivePriceTicker;
