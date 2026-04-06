import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useDemoMode } from "../contexts/DemoModeContext";

/**
 * Wraps authenticated routes. Redirects to /login if not authenticated and not in demo mode.
 */
export const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  const { isDemoMode } = useDemoMode();
  const location = useLocation();

  if (loading) return null;

  if (!isAuthenticated && !isDemoMode) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  return children;
};

/**
 * Wraps public-only routes (login/register). Redirects to /dashboard if already authenticated.
 */
export const PublicOnlyRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) return null;

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};
