import React, { Suspense, lazy, useState } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ToastProvider, LoadingScreen, IconButton } from "./components/v2n";
import MainLayout from "./layouts/MainLayout";
import { Locate } from "lucide-react";
import { LocationContext } from "./context/LocationContext";

const Home = lazy(() => import("./pages/Home"));
const Brand = lazy(() => import("./pages/Brand"));
const Admin = lazy(() => import("./pages/Admin"));
const Owner = lazy(() => import("./pages/Owner"));
const Profile = lazy(() => import("./pages/Profile"));

const ADMIN_STORAGE_KEY = "v2n_admin_session";

function AdminGuardedBrand() {
  const hasSession =
    typeof window !== "undefined" &&
    !!localStorage.getItem(ADMIN_STORAGE_KEY);

  if (!hasSession) return <Navigate to="/admin" replace />;
  return <Brand />;
}

export default function App() {
  const [myLocationFn, setMyLocationFn] = useState(() => () => {});

  return (
    <ToastProvider>
      <LocationContext.Provider value={{ setMyLocationFn }}>
        <Suspense fallback={<LoadingScreen />}>
          <MainLayout
            rightSlot={
              <IconButton
                onClick={() => myLocationFn()}
                aria-label="Use my location"
              >
                <Locate size={18} />
              </IconButton>
            }
          >
            <Routes>
              <Route
                path="/"
                element={<Home registerLocationFn={setMyLocationFn} />}
              />
              <Route path="/brand" element={<AdminGuardedBrand />} />
              <Route path="/admin" element={<Admin />} />
              <Route path="/owner" element={<Owner />} />
              <Route path="/me" element={<Profile />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </MainLayout>
        </Suspense>
      </LocationContext.Provider>
    </ToastProvider>
  );
}
