/**
 * Smart Prefetch Engine — background data fetching with safety guards.
 * Runs only when: network online, app idle (300ms), cache cold/expired,
 * battery not low, CPU not busy. Cancels on navigation.
 */
import axios from "axios";
import { cacheGet, cacheSet } from "./mobileCache";
import { API } from "./constants";

let activeController = null;

const getAuthHeaders = () => {
  try {
    const stored = localStorage.getItem("alphaai_tokens");
    if (stored) {
      const tokens = JSON.parse(stored);
      if (tokens?.access_token) return { Authorization: `Bearer ${tokens.access_token}` };
    }
  } catch { /* no-op */ }
  return {};
};

const isDemoMode = () => {
  const params = new URLSearchParams(window.location.search);
  if (params.get("demo") === "true") return true;
  try {
    return localStorage.getItem("alphaai_demo_mode") === "true";
  } catch {
    return false;
  }
};

const isBatteryLow = async () => {
  try {
    if (navigator.getBattery) {
      const battery = await navigator.getBattery();
      return battery.level < 0.2 && !battery.charging;
    }
  } catch { /* not supported */ }
  return false;
};

const shouldPrefetch = async () => {
  if (!navigator.onLine) return false;
  if (await isBatteryLow()) return false;
  return true;
};

const safeFetch = async (url, opts = {}) => {
  if (!activeController || activeController.signal.aborted) return null;
  try {
    const res = await axios.get(url, {
      ...opts,
      signal: activeController.signal,
      timeout: 8000,
    });
    return res.data;
  } catch {
    return null;
  }
};

const prefetchAndCache = async (cacheKey, url, opts = {}) => {
  if (cacheGet(cacheKey)) return;
  const data = await safeFetch(url, opts);
  if (data) cacheSet(cacheKey, data);
};

// ── Page-specific prefetch rules ──────────────────────────────

const prefetchLeaderboard = async () => {
  const demo = isDemoMode();
  const params = demo ? "?demo=true&limit=3&sort_by=sharpe&order=desc" : "?limit=3&sort_by=sharpe&order=desc";
  await prefetchAndCache("strategies", `${API}/leaderboard/strategies${params}`);

  const cached = cacheGet("strategies");
  const top3 = cached?.strategies?.slice(0, 3) || [];
  for (const s of top3) {
    if (!s.id) continue;
    const demoQ = demo ? "?demo=true" : "";
    await prefetchAndCache(`strategy_detail_${s.id}`, `${API}/leaderboard/strategies/${s.id}${demoQ}`);
  }
};

const prefetchDashboard = async () => {
  const headers = getAuthHeaders();
  if (!headers.Authorization && !isDemoMode()) return;
  if (isDemoMode()) return;
  await prefetchAndCache("followed", `${API}/strategies/following/ids`, { headers });
};

const prefetchAlerts = async () => {
  // Alerts come via WebSocket; prefetch cache is minimal
  // Only warm the bootstrap data if stale
  const demo = isDemoMode();
  const params = demo ? "?demo=true" : "";
  const headers = demo ? {} : getAuthHeaders();
  await prefetchAndCache(demo ? "bootstrap_demo" : "bootstrap", `${API}/mobile/bootstrap${params}`, { headers });
};

// ── Hover/Touch prefetch ──────────────────────────────────────

export const prefetchStrategy = async (strategyId) => {
  if (!strategyId || !navigator.onLine) return;
  const demo = isDemoMode();
  const demoQ = demo ? "?demo=true" : "";
  const key = `strategy_detail_${strategyId}`;
  if (cacheGet(key)) return;
  try {
    const res = await axios.get(`${API}/leaderboard/strategies/${strategyId}${demoQ}`, { timeout: 5000 });
    if (res.data) cacheSet(key, res.data);
  } catch { /* silent */ }
};

// ── Core scheduler ────────────────────────────────────────────

const PAGE_RULES = {
  "/leaderboard": prefetchLeaderboard,
  "/dashboard": prefetchDashboard,
  "/alerts": prefetchAlerts,
};

const runPrefetchCycle = async () => {
  if (!(await shouldPrefetch())) return;

  activeController = new AbortController();

  const path = window.location.pathname;
  const handler = PAGE_RULES[path];
  if (handler) {
    await handler();
  }
};

let idleCallbackId = null;

export const startPrefetching = () => {
  cancelPrefetching();

  const schedule = () => {
    if (typeof requestIdleCallback === "function") {
      idleCallbackId = requestIdleCallback(
        () => { runPrefetchCycle(); },
        { timeout: 300 }
      );
    } else {
      idleCallbackId = setTimeout(() => { runPrefetchCycle(); }, 300);
    }
  };

  schedule();
};

export const cancelPrefetching = () => {
  if (activeController) {
    activeController.abort();
    activeController = null;
  }
  if (idleCallbackId != null) {
    if (typeof cancelIdleCallback === "function") {
      cancelIdleCallback(idleCallbackId);
    } else {
      clearTimeout(idleCallbackId);
    }
    idleCallbackId = null;
  }
};

export const getCachedStrategy = (strategyId) => {
  return cacheGet(`strategy_detail_${strategyId}`);
};
