/**
 * Mobile Cache — localStorage wrapper with TTL and invalidation.
 */

const PREFIX = "alphaai_cache_";
const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

const TTL_MAP = {
  bootstrap: 2 * 60 * 1000,
  strategies: 5 * 60 * 1000,
  followed: 3 * 60 * 1000,
  profile: 5 * 60 * 1000,
  alerts: 30 * 1000,
  strategy_detail: 5 * 60 * 1000,
  metadata: 10 * 60 * 1000,
  chart: 2 * 60 * 1000,
};

export const cacheGet = (key) => {
  try {
    const raw = localStorage.getItem(PREFIX + key);
    if (!raw) return null;
    const { data, expiry } = JSON.parse(raw);
    if (Date.now() > expiry) {
      localStorage.removeItem(PREFIX + key);
      return null;
    }
    return data;
  } catch {
    return null;
  }
};

export const cacheSet = (key, data) => {
  try {
    const ttl = TTL_MAP[key] || DEFAULT_TTL;
    localStorage.setItem(PREFIX + key, JSON.stringify({
      data,
      expiry: Date.now() + ttl,
    }));
  } catch {
    // storage full — silently fail
  }
};

export const cacheRemove = (key) => {
  localStorage.removeItem(PREFIX + key);
};

export const cacheClearAll = () => {
  const keys = Object.keys(localStorage).filter(k => k.startsWith(PREFIX));
  keys.forEach(k => localStorage.removeItem(k));
};

export const cacheInvalidateOnAuth = () => {
  cacheClearAll();
};
