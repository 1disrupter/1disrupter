/**
 * Mobile API Client — Enhanced API layer with retry, offline queue, and caching.
 */
import axios from "axios";
import { API } from "./constants";
import { cacheGet, cacheSet } from "./mobileCache";

const MAX_RETRIES = 3;
const RETRY_BASE_DELAY = 1000;

// ── Offline event queue ────────────────────────────────────────

const QUEUE_KEY = "alphaai_offline_queue";
const NON_CRITICAL_EVENTS = ["page_view", "strategy_view", "api_call", "ws_connect", "ws_disconnect"];

const getQueue = () => {
  try {
    return JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
  } catch {
    return [];
  }
};

const saveQueue = (queue) => {
  try {
    localStorage.setItem(QUEUE_KEY, JSON.stringify(queue.slice(-50)));
  } catch {
    // storage full
  }
};

export const queueOfflineEvent = (type, metadata) => {
  if (!NON_CRITICAL_EVENTS.includes(type)) return;
  const queue = getQueue();
  queue.push({ type, metadata, queued_at: new Date().toISOString() });
  saveQueue(queue);
};

export const flushOfflineQueue = async () => {
  const queue = getQueue();
  if (queue.length === 0) return;

  const stored = localStorage.getItem("alphaai_tokens");
  const headers = {};
  if (stored) {
    try {
      const tokens = JSON.parse(stored);
      if (tokens?.access_token) headers.Authorization = `Bearer ${tokens.access_token}`;
    } catch { /* no-op */ }
  }

  // Batch flush
  const batch = queue.splice(0, 20);
  saveQueue(queue);

  for (const event of batch) {
    try {
      await axios.post(`${API}/admin/events`, event, { headers, timeout: 5000 });
    } catch {
      // Re-queue on failure
      const remaining = getQueue();
      remaining.push(event);
      saveQueue(remaining);
      break;
    }
  }
};

// ── Retry with exponential backoff ─────────────────────────────

export const fetchWithRetry = async (url, options = {}, retries = MAX_RETRIES) => {
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const response = await axios({ url, timeout: 10000, ...options });
      return response;
    } catch (error) {
      if (attempt === retries) throw error;
      if (error.response && error.response.status < 500) throw error; // Don't retry client errors
      const delay = RETRY_BASE_DELAY * Math.pow(2, attempt);
      await new Promise(r => setTimeout(r, delay));
    }
  }
};

// ── Cached fetch ───────────────────────────────────────────────

export const fetchCached = async (cacheKey, url, options = {}) => {
  const cached = cacheGet(cacheKey);
  if (cached) return { data: cached, fromCache: true };

  const response = await fetchWithRetry(url, options);
  if (response.data) {
    cacheSet(cacheKey, response.data);
  }
  return { data: response.data, fromCache: false };
};

// ── Bootstrap fetch ────────────────────────────────────────────

export const fetchBootstrap = async (isDemoMode, token) => {
  const cacheKey = isDemoMode ? "bootstrap_demo" : "bootstrap";
  const cached = cacheGet(cacheKey);
  if (cached) return { data: cached, fromCache: true };

  const params = isDemoMode ? "?demo=true" : "";
  const headers = {};
  if (!isDemoMode && token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const res = await fetchWithRetry(`${API}/mobile/bootstrap${params}`, { headers });
  if (res.data) cacheSet(cacheKey, res.data);
  return { data: res.data, fromCache: false };
};
