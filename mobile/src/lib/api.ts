import { API_BASE } from "@/config";

export type Category = "bar" | "club" | "live_music";
export type VibeFilter = Category | "all";
export type Trend = "rising" | "peaking" | "falling" | "steady";
export type TouristLabel = "tourist_trap" | "local_gem" | "neutral";
export type VoteType = "busy" | "dead" | "good";

export interface Top3Item {
  id: string;
  name: string;
  category: Category;
  vibe_score: number;
  adjusted_score: number;
  lat: number;
  lng: number;
  distance_km: number | null;
  tourist_label: TouristLabel;
}

export interface HeatPoint {
  id: string;
  name: string;
  category: Category;
  lat: number;
  lng: number;
  heat: number;
}

export interface LiveMusicItem {
  venue_id: string;
  name: string;
  category: Category;
  lat: number;
  lng: number;
  live_music: boolean;
  confidence: number;
  event_score: number;
  vibe_score: number;
  reason: string;
}

export interface TouristFlagItem {
  venue_id: string;
  name: string;
  category: Category;
  label: TouristLabel;
  reason: string;
  signals: { google_score: number; social_score: number; user_votes_score: number };
}

export interface ForecastItem {
  venue_id: string;
  name: string;
  trend: Trend;
  delta_next_hour: number;
  current_vibe_score: number;
  as_of: string;
}

export interface Directions {
  venue_id: string;
  duration_minutes: number;
  distance_meters: number;
  deeplink: string;
  provider: "stub" | "google";
}

// ---------------------------------------------------------------------------
// fetch wrapper (no axios — keep RN bundle small)
// ---------------------------------------------------------------------------
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText} — ${body || path}`);
  }
  return (await res.json()) as T;
}

const qs = (p: Record<string, unknown>) => {
  const s = new URLSearchParams();
  for (const [k, v] of Object.entries(p)) {
    if (v === undefined || v === null || v === "") continue;
    s.append(k, String(v));
  }
  const str = s.toString();
  return str ? `?${str}` : "";
};

// ---------------------------------------------------------------------------
// Endpoints
// ---------------------------------------------------------------------------
export const getTop3 = (params: {
  user_lat?: number;
  user_lng?: number;
  vibe?: Category;
  avoid_tourist_traps?: boolean;
  radius_km?: number;
}) => request<{ count: number; items: Top3Item[] }>(`/vibes/top3${qs(params)}`);

export const getHeatmap = () =>
  request<{ count: number; points: HeatPoint[] }>(`/vibes/heatmap`);

export const getLiveMusic = (include_all = false) =>
  request<{ count: number; items: LiveMusicItem[] }>(
    `/vibes/live-music${qs({ include_all })}`
  );

export const getTouristFlags = () =>
  request<{ count: number; buckets: Record<TouristLabel, number>; items: TouristFlagItem[] }>(
    `/vibes/tourist-flags`
  );

export const getForecastAll = () =>
  request<{ count: number; items: ForecastItem[] }>(`/vibes/forecast`);

export const getDirections = (venue_id: string, user_lat: number, user_lng: number) =>
  request<Directions>(`/vibes/directions${qs({ venue_id, user_lat, user_lng })}`);

export const postFeedback = (venue_id: string, vote: VoteType) =>
  request<{ venue_id: string; new_vibe_score: number; new_crowd_level: string; updated_at: string }>(
    `/feedback`,
    { method: "POST", body: JSON.stringify({ venue_id, vote }) }
  );
