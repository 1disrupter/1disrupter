/**
 * usePrefetch — React hook that drives the smart prefetch engine.
 * Starts prefetching on mount (if conditions pass), cancels on unmount/navigation.
 */
import { useEffect, useRef, useCallback } from "react";
import { useLocation } from "react-router-dom";
import { startPrefetching, cancelPrefetching, prefetchStrategy } from "../lib/smartPrefetch";

const usePrefetch = () => {
  const location = useLocation();
  const prevPath = useRef(location.pathname);

  useEffect(() => {
    if (prevPath.current !== location.pathname) {
      cancelPrefetching();
      prevPath.current = location.pathname;
    }
    startPrefetching();
    return () => cancelPrefetching();
  }, [location.pathname]);

  const onHoverStrategy = useCallback((strategyId) => {
    if (strategyId) prefetchStrategy(strategyId);
  }, []);

  return { onHoverStrategy };
};

export default usePrefetch;
