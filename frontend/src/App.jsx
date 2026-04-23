import React, { Suspense, lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ToastProvider, LoadingScreen } from "@/components/v2n";

const Home = lazy(() => import("@/pages/Home"));
const Brand = lazy(() => import("@/pages/Brand"));
const Admin = lazy(() => import("@/pages/Admin"));

export default function App() {
  return (
    <ToastProvider>
      <Suspense fallback={<LoadingScreen />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/brand" element={<Brand />} />
          <Route path="/admin" element={<Admin />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </ToastProvider>
  );
}
