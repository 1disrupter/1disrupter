import React, { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ToastProvider, LoadingScreen } from "@/components/v2n";
import MainLayout from "@/layouts/MainLayout";

const Home = lazy(() => import("@/pages/Home"));
const Brand = lazy(() => import("@/pages/Brand"));
const Admin = lazy(() => import("@/pages/Admin"));
const Owner = lazy(() => import("@/pages/Owner"));

const ADMIN_STORAGE_KEY = "v2n_admin_session";

function AdminGuardedBrand() {
  const hasSession =
    typeof window !== "undefined" &&
    !!localStorage.getItem(ADMIN_STORAGE_KEY);

  if (!hasSession) return <Navigate to="/admin" replace />;
  return <Brand />;
}

export default function App() {
  return (
    <ToastProvider>
      <Suspense fallback={<LoadingScreen />}>
        <MainLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/brand" element={<AdminGuardedBrand />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/owner" element={<Owner />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </MainLayout>
      </Suspense>
    </ToastProvider>
  );
}




