/**
 * Mobile Cache — localStorage wrapper with TTL and invalidation.
 */

const PREFIX = "alphaai_cache_";
const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

const TTL_MAP = {
  bootstrap: 2 * 60 * 1000,      // 2 min
  strategies: 5 * 60 * 1000,     // 5 min
  followed: 3 * 60 * 1000,       // 3 min
  profile: 5 * 60 * 1000,        // 5 min
  alerts: 60 * 1000,             // 1 min
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
