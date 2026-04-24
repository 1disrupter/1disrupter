import React from "react";
import { Ionicons } from "@expo/vector-icons";
import { NavigationContainer, DarkTheme } from "@react-navigation/native";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { colors } from "@/theme";

import TonightScreen from "@/screens/TonightScreen";
import MapScreen from "@/screens/MapScreen";
import VenueDetailScreen from "@/screens/VenueDetailScreen";
import SettingsScreen from "@/screens/SettingsScreen";
import WalletScreen from "@/screens/WalletScreen";
import InboxScreen from "@/screens/InboxScreen";

const Tab = createBottomTabNavigator();
const Stack = createNativeStackNavigator();

function Tabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarActiveTintColor: colors.text,
        tabBarInactiveTintColor: colors.textFaint,
        tabBarStyle: {
          backgroundColor: colors.bg,
          borderTopColor: colors.border,
          borderTopWidth: 1,
          height: 72,
          paddingTop: 6,
          paddingBottom: 14,
        },
        tabBarLabelStyle: { fontSize: 10, fontWeight: "700" },
        tabBarIcon: ({ color, focused }) => {
          const icon =
            route.name === "Tonight"
              ? focused ? "flame" : "flame-outline"
              : route.name === "Map"
              ? focused ? "map" : "map-outline"
              : route.name === "Wallet"
              ? focused ? "wallet" : "wallet-outline"
              : route.name === "Inbox"
              ? focused ? "notifications" : "notifications-outline"
              : focused ? "settings" : "settings-outline";
          return <Ionicons name={icon as any} size={20} color={color} />;
        },
      })}
    >
      <Tab.Screen name="Tonight" component={TonightScreen} />
      <Tab.Screen name="Map" component={MapScreen} />
      <Tab.Screen name="Wallet" component={WalletScreen} />
      <Tab.Screen name="Inbox" component={InboxScreen} />
      <Tab.Screen name="Settings" component={SettingsScreen} />
    </Tab.Navigator>
  );
}

const navTheme: typeof DarkTheme = {
  ...DarkTheme,
  colors: {
    ...DarkTheme.colors,
    background: colors.bg,
    card: colors.bg,
    border: colors.border,
    primary: colors.primaryGlow,
    text: colors.text,
    notification: colors.pink,
  },
};

export default function RootNavigator() {
  return (
    <NavigationContainer theme={navTheme}>
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: colors.bg },
          headerTintColor: colors.text,
          headerTitleStyle: { fontWeight: "900" },
          contentStyle: { backgroundColor: colors.bg },
        }}
      >
        <Stack.Screen name="Root" component={Tabs} options={{ headerShown: false }} />
        <Stack.Screen
          name="VenueDetail"
          component={VenueDetailScreen}
          options={{ title: "VENUE" }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
