import AsyncStorage from "@react-native-async-storage/async-storage";

const KEY = "v2n.device_id";

function randomUuid(): string {
  // Lightweight UUIDv4 (enough for opaque device IDs; no PII).
  const hex = "0123456789abcdef";
  let out = "";
  for (let i = 0; i < 32; i += 1) {
    let n = Math.floor(Math.random() * 16);
    if (i === 12) n = 4;
    if (i === 16) n = (n & 0x3) | 0x8;
    out += hex[n];
    if (i === 7 || i === 11 || i === 15 || i === 19) out += "-";
  }
  return out;
}

let cached: string | null = null;

export async function getDeviceId(): Promise<string> {
  if (cached) return cached;
  const existing = await AsyncStorage.getItem(KEY);
  if (existing) {
    cached = existing;
    return existing;
  }
  const fresh = randomUuid();
  await AsyncStorage.setItem(KEY, fresh);
  cached = fresh;
  return fresh;
}

/** Same opaque id is reused as the wallet user_id — backend treats it as opaque. */
export async function getUserId(): Promise<string> {
  return getDeviceId();
}
