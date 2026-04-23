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
