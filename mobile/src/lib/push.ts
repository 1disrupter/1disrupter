import { Platform } from "react-native";
import * as Device from "expo-device";
import * as Notifications from "expo-notifications";

import { API_BASE } from "@/config";
import { getUserId } from "@/lib/identity";

// Show notifications in-foreground too — users almost never have Vibe2Nite in focus
// when their credit totals tick over.
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

/** Request permissions, fetch an Expo push token, and POST it to the backend. */
export async function registerForPushAsync(): Promise<string | null> {
  // Emulators / web / simulators can't receive pushes.
  if (!Device.isDevice) return null;

  try {
    if (Platform.OS === "android") {
      await Notifications.setNotificationChannelAsync("default", {
        name: "default",
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: "#B15CFF",
      });
    }

    const { status: existing } = await Notifications.getPermissionsAsync();
    let status = existing;
    if (status !== "granted") {
      const req = await Notifications.requestPermissionsAsync();
      status = req.status;
    }
    if (status !== "granted") return null;

    const tokenResp = await Notifications.getExpoPushTokenAsync();
    const token = tokenResp?.data;
    if (!token) return null;

    const wallet_id = await getUserId();
    await fetch(`${API_BASE}/api/notifications/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wallet_id, expo_push_token: token }),
    }).catch(() => null);

    return token;
  } catch {
    return null;
  }
}
