import axios from "axios";

export const BACKEND_URL =
  process.env.REACT_APP_BACKEND_URL || window.location.origin;

export const api = axios.create({
  baseURL: `${BACKEND_URL}/api`,
  timeout: 15000,
});

export const getTopVibes = (lat, lng, radius_km = 50) =>
  api.get("/vibes/top", { params: { lat, lng, radius_km } }).then((r) => r.data);

export const submitFeedback = (venue_id, vote) =>
  api.post("/feedback", { venue_id, vote }).then((r) => r.data);

export const listAdminVenues = () => api.get("/admin/venues").then((r) => r.data);

export const createVenue = (payload) =>
  api.post("/admin/venues", payload).then((r) => r.data);

export const updateSignals = (venue_id, signals) =>
  api.patch(`/admin/venues/${venue_id}/signals`, signals).then((r) => r.data);

export const triggerSignalRefresh = () =>
  api.post("/admin/signals/refresh").then((r) => r.data);

export const getForecast = (venue_id) =>
  api.get("/vibes/forecast", { params: venue_id ? { venue_id } : {} }).then((r) => r.data);

export const getTouristFlags = () =>
  api.get("/vibes/tourist-flags").then((r) => r.data);

export const getLiveMusic = () =>
  api.get("/vibes/live-music").then((r) => r.data);

export const getHeatmap = () =>
  api.get("/vibes/heatmap").then((r) => r.data);

// --- Iteration 13: claims, providers, webhooks -----------------------------
export const submitClaim = (payload) =>
  api.post("/claims/submit", payload).then((r) => r.data);

export const listClaims = (status) =>
  api.get("/admin/claims", { params: status ? { status } : {} }).then((r) => r.data);

export const reviewClaim = (claim_id, action, reviewer = "admin", note = "") =>
  api.post(`/admin/claims/${claim_id}/review`, { action, reviewer, note }).then((r) => r.data);

export const getVenueOwner = (venue_id) =>
  api.get(`/venues/${venue_id}/owner`).then((r) => r.data);

export const getProviderStatus = () =>
  api.get("/admin/providers/status").then((r) => r.data);

export const getRecentWebhooks = (limit = 20) =>
  api.get("/admin/webhooks/recent", { params: { limit } }).then((r) => r.data);

// --- Iteration 14: owner-scoped dashboard ----------------------------------
const ownerHeaders = (key) => ({ headers: { "X-Owner-Key": key } });

export const getOwnerMe = (key) =>
  api.get("/owner/me", ownerHeaders(key)).then((r) => r.data);

export const getOwnerInbox = (key, limit = 20) =>
  api.get("/owner/inbox", { ...ownerHeaders(key), params: { limit } }).then((r) => r.data);

export const setOwnerHandles = (key, payload) =>
  api.put("/owner/venue/handles", payload, ownerHeaders(key)).then((r) => r.data);

// --- Iteration 15: multi-venue + owner webhooks ----------------------------
export const getOwnerVenues = (key) =>
  api.get("/owner/venues", ownerHeaders(key)).then((r) => r.data);

export const setOwnerHandlesForVenue = (key, venue_id, payload) =>
  api.put(`/owner/venue/${venue_id}/handles`, payload, ownerHeaders(key)).then((r) => r.data);

export const setOwnerWebhooks = (key, venue_id, payload) =>
  api.put(`/owner/venue/${venue_id}/webhooks`, payload, ownerHeaders(key)).then((r) => r.data);

export const testOwnerWebhook = (key, venue_id) =>
  api.post(`/owner/venue/${venue_id}/webhooks/test`, {}, ownerHeaders(key)).then((r) => r.data);

// --- Iteration 16: ownership transfer / expire / reverify / first-visit ----
export const requestOwnerTransfer = (key, venue_id, email) =>
  api.post(`/owner/venue/${venue_id}/transfer/request`, { email }, ownerHeaders(key)).then((r) => r.data);

export const acceptOwnerTransfer = (token) =>
  api.get(`/owner/transfer/accept/${token}`).then((r) => r.data);

export const adminExpireOwnership = (venue_id, reviewer = "admin") =>
  api.post(`/admin/venue/${venue_id}/ownership/expire`, null, { params: { reviewer } }).then((r) => r.data);

export const submitReverify = (payload) =>
  api.post("/claims/reverify", payload).then((r) => r.data);

export const checkInVenue = (venue_id, device_id) =>
  api.post("/intel/visits/check-in", { venue_id, device_id }).then((r) => r.data);
