import Constants from "expo-constants";

const fromExpo = (Constants.expoConfig?.extra as any)?.apiUrl as string | undefined;

/** Single source of truth for backend base URL. */
export const API_BASE: string =
  process.env.EXPO_PUBLIC_API_URL ||
  fromExpo ||
  "http://localhost:8001";

export const DEFAULT_LOCATION = { lat: 40.73, lng: -73.99, label: "Manhattan, NY" };

/** City label shown on the Tonight header. Replace with real reverse-geocoding later. */
export const CITY_LABEL = "Manhattan";
