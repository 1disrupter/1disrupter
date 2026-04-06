import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'sonner';
import axios from 'axios';
import {
  mockSignals, mockPortfolioStats, mockAgents, mockStrategies,
  mockMarketplaceItems, mockEventAgents, mockResearchQueries,
  mockSimulationResults, mockCopyTraders, mockChartData, mockLeaderboard
} from '../lib/mockData';

const API = process.env.REACT_APP_BACKEND_URL;

const DemoModeContext = createContext(null);

export const useDemoMode = () => {
  const ctx = useContext(DemoModeContext);
  if (!ctx) throw new Error('useDemoMode must be used within DemoModeProvider');
  return ctx;
};

/** Alias hook matching the user's spec. Admin users always see live. */
export const useSystemMode = () => {
  const ctx = useDemoMode();
  // Admin override: admins never see demo mode
  let authData = null;
  try {
    const raw = localStorage.getItem('alphaai_auth');
    if (raw) authData = JSON.parse(raw);
  } catch { /* ignore */ }
  const isAdmin = authData?.user?.role === 'admin';
  const effectiveDemo = isAdmin ? false : ctx.isDemoMode;

  return {
    mode: effectiveDemo ? 'demo' : 'live',
    isDemo: effectiveDemo,
    isLive: !effectiveDemo,
    isAdmin,
    setMode: ctx.setSystemMode,
    loading: ctx.modeLoading,
  };
};

const jitter = (val, pct = 0.05) => {
  const n = typeof val === 'string' ? parseFloat(val.replace(/[^0-9.-]/g, '')) : val;
  if (isNaN(n)) return val;
  const delta = n * pct * (Math.random() * 2 - 1);
  return +(n + delta).toFixed(2);
};

const randomPick = (arr) => arr[Math.floor(Math.random() * arr.length)];

export const DemoModeProvider = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [modeLoading, setModeLoading] = useState(true);

  // Fetch system mode from backend (single source of truth)
  const fetchMode = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/api/system/mode`);
      const isDemo = res.data.mode === 'demo';
      setIsDemoMode(isDemo);
    } catch {
      // Fallback: keep current
    } finally {
      setModeLoading(false);
    }
  }, []);

  useEffect(() => {
    // Check URL param override
    const params = new URLSearchParams(window.location.search);
    if (params.get('demo') === 'true') {
      setIsDemoMode(true);
      setModeLoading(false);
    } else {
      fetchMode();
    }
    // Re-sync every 30s
    const interval = setInterval(fetchMode, 30000);
    return () => clearInterval(interval);
  }, [fetchMode]);

  // Admin action: switch system mode
  const setSystemMode = useCallback(async (newMode) => {
    const adminKey = localStorage.getItem('adminKey') || 'alphaai_admin_2026';
    try {
      setModeLoading(true);
      await axios.post(
        `${API}/api/system/mode?admin_key=${adminKey}`,
        { mode: newMode }
      );
      setIsDemoMode(newMode === 'demo');
      toast.success(`Switched to ${newMode.toUpperCase()} mode`);
    } catch (e) {
      toast.error('Failed to switch mode — admin access required');
    } finally {
      setModeLoading(false);
    }
  }, []);

  // Legacy toggle (for DemoModeBanner close button)
  const toggleDemoMode = useCallback(() => {
    const newMode = isDemoMode ? 'live' : 'demo';
    setSystemMode(newMode);
  }, [isDemoMode, setSystemMode]);

  const shareDemoLink = useCallback(() => {
    const url = window.location.origin + '/dashboard?demo=true';
    navigator.clipboard.writeText(url).then(() => {
      toast.success('Demo link copied!', {
        description: 'Share it with anyone to let them explore My-AlphaAI instantly.',
      });
    }).catch(() => {
      const input = document.createElement('input');
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      toast.success('Demo link copied!');
    });
  }, []);

  // Live-updating demo data (only ticks in demo mode)
  const [demoSignals, setDemoSignals] = useState(mockSignals);
  const [demoStats, setDemoStats] = useState(mockPortfolioStats);
  const [demoAgents, setDemoAgents] = useState(mockAgents);
  const [demoStrategies, setDemoStrategies] = useState(mockStrategies);
  const [demoMarketplace, setDemoMarketplace] = useState(mockMarketplaceItems);
  const [demoEventAgents, setDemoEventAgents] = useState(mockEventAgents);
  const [demoResearch, setDemoResearch] = useState(mockResearchQueries);
  const [demoSimulations, setDemoSimulations] = useState(mockSimulationResults);
  const [demoCopyTraders, setDemoCopyTraders] = useState(mockCopyTraders);
  const [demoChart, setDemoChart] = useState(mockChartData);
  const [demoLeaderboard, setDemoLeaderboard] = useState(mockLeaderboard);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!isDemoMode) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    const tick = () => {
      setDemoSignals(prev => prev.map(s => ({
        ...s,
        confidence: Math.min(99, Math.max(50, s.confidence + Math.floor(Math.random() * 5 - 2))),
        price: '$' + jitter(parseFloat(s.price.replace(/[$,]/g, '')), 0.008).toLocaleString(),
        time: randomPick(['just now', '1 min ago', '2 min ago', '5 min ago']),
        status: randomPick(['active', 'active', 'active', 'closed']),
      })));

      setDemoStats(prev => prev.map(s => {
        if (s.label === 'Portfolio Value') {
          const base = jitter(12480, 0.004);
          return { ...s, value: '$' + base.toLocaleString(undefined, { minimumFractionDigits: 2 }) };
        }
        if (s.label === "Today's P&L") {
          const v = jitter(340.2, 0.08);
          return { ...s, value: (v >= 0 ? '+' : '') + '$' + Math.abs(v).toFixed(2), positive: v >= 0, change: (v >= 0 ? '+' : '') + (v / 124.8).toFixed(1) + '%' };
        }
        return s;
      }));

      setDemoChart(prev => {
        const last = prev[prev.length - 1]?.value || 12480;
        const next = jitter(last, 0.01);
        const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
        const newPoint = { time: days[prev.length % 7], value: next };
        return [...prev.slice(-6), newPoint];
      });

      setDemoAgents(prev => prev.map(a => ({
        ...a,
        signals: Math.max(0, a.signals + Math.floor(Math.random() * 3 - 1)),
        accuracy: Math.min(99, Math.max(50, a.accuracy + Math.floor(Math.random() * 3 - 1))),
      })));
    };

    tick();
    const interval = 3000 + Math.random() * 2000;
    timerRef.current = setInterval(tick, interval);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [isDemoMode]);

  const value = {
    isDemoMode,
    modeLoading,
    toggleDemoMode,
    setSystemMode,
    shareDemoLink,
    demoSignals,
    demoStats,
    demoAgents,
    demoStrategies,
    demoMarketplace,
    demoEventAgents,
    demoResearch,
    demoSimulations,
    demoCopyTraders,
    demoChart,
    demoLeaderboard,
  };

  return (
    <DemoModeContext.Provider value={value}>
      {children}
    </DemoModeContext.Provider>
  );
};

export default DemoModeContext;
