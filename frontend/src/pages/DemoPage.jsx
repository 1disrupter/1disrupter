import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

/**
 * /demo route — activates demo mode via sessionStorage, then loads dashboard.
 * The DemoModeContext reads sessionStorage on init.
 */
export default function DemoPage() {
  const navigate = useNavigate();

  useEffect(() => {
    sessionStorage.setItem("alphaai_demo_mode", "true");
    // Full reload so DemoModeContext re-initializes with demo mode active
    window.location.href = "/dashboard?demo=true";
  }, [navigate]);

  return null;
}
