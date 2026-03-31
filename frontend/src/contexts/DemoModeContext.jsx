import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { toast } from 'sonner';
import analytics from '../lib/analytics';
import {
  mockSignals, mockPortfolioStats, mockAgents, mockStrategies,
  mockMarketplaceItems, mockEventAgents, mockResearchQueries,
  mockSimulationResults, mockCopyTraders, mockChartData, mockLeaderboard
} from '../lib/mockData';

const DemoModeContext = createContext(null);

export const useDemoMode = () => {
  const ctx = useContext(DemoModeContext);
  if (!ctx) throw new Error('useDemoMode must be used within DemoModeProvider');
  return ctx;
};

// Randomize a numeric value by +/- pct
const jitter = (val, pct = 0.05) => {
  const n = typeof val === 'string' ? parseFloat(val.replace(/[^0-9.-]/g, '')) : val;
  if (isNaN(n)) return val;
  const delta = n * pct * (Math.random() * 2 - 1);
  return +(n + delta).toFixed(2);
};

const randomPick = (arr) => arr[Math.floor(Math.random() * arr.length)];

export const DemoModeProvider = ({ children }) => {
  const [isDemoMode, setIsDemoMode] = useState(() => {
    // Check URL param first, then sessionStorage
    const params = new URLSearchParams(window.location.search);
    if (params.get('demo') === 'true') {
      sessionStorage.setItem('alphaai_demo_mode', 'true');
      return true;
    }
    return sessionStorage.getItem('alphaai_demo_mode') === 'true';
  });

  // Live-updating demo data
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

  // Fire demo_link_opened event once per session when ?demo=true is detected
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('demo') !== 'true') return;
    if (sessionStorage.getItem('alphaai_demo_link_tracked')) return;

    sessionStorage.setItem('alphaai_demo_link_tracked', '1');
    analytics.track('demo_link_opened', {
      referrer: document.referrer || '(direct)',
      userAgent: navigator.userAgent,
      path: window.location.pathname,
      isAuthenticated: false,
    });
  }, []);

  const toggleDemoMode = useCallback(() => {
    setIsDemoMode(prev => {
      const next = !prev;
      sessionStorage.setItem('alphaai_demo_mode', String(next));
      return next;
    });
  }, []);

  const shareDemoLink = useCallback(() => {
    const base = window.location.origin + '/dashboard';
    const url = base + '?demo=true';
    navigator.clipboard.writeText(url).then(() => {
      toast.success('Demo link copied!', {
        description: 'Share it with anyone to let them explore My-AlphaAI instantly.',
      });
    }).catch(() => {
      // Fallback: select text for manual copy
      const input = document.createElement('input');
      input.value = url;
      document.body.appendChild(input);
      input.select();
      document.execCommand('copy');
      document.body.removeChild(input);
      toast.success('Demo link copied!', {
        description: 'Share it with anyone to let them explore My-AlphaAI instantly.',
      });
    });
  }, []);

  // Simulate live updates every 3-5 seconds
  useEffect(() => {
    if (!isDemoMode) {
      if (timerRef.current) clearInterval(timerRef.current);
      return;
    }

    const tick = () => {
      // Signals — fluctuate prices and confidence
      setDemoSignals(prev => prev.map(s => ({
        ...s,
        confidence: Math.min(99, Math.max(50, s.confidence + Math.floor(Math.random() * 5 - 2))),
        price: '$' + jitter(parseFloat(s.price.replace(/[$,]/g, '')), 0.008).toLocaleString(),
        time: randomPick(['just now', '1 min ago', '2 min ago', '5 min ago']),
        status: randomPick(['active', 'active', 'active', 'closed']),
      })));

      // Portfolio stats — slight changes
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

      // Chart — append a new point, slide window
      setDemoChart(prev => {
        const last = prev[prev.length - 1]?.value || 12480;
        const next = jitter(last, 0.01);
        const days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
        const newPoint = { time: days[prev.length % 7], value: next };
        return [...prev.slice(-6), newPoint];
      });

      // Agents — fluctuate signals count
      setDemoAgents(prev => prev.map(a => ({
        ...a,
        signals: Math.max(0, a.signals + Math.floor(Math.random() * 3 - 1)),
        accuracy: Math.min(99, Math.max(50, a.accuracy + Math.floor(Math.random() * 3 - 1))),
      })));
    };

    // First tick immediately
    tick();
    const interval = 3000 + Math.random() * 2000; // 3-5s
    timerRef.current = setInterval(tick, interval);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isDemoMode]);

  const value = {
    isDemoMode,
    toggleDemoMode,
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
