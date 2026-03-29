/**
 * PullToRefresh — mobile pull-to-refresh wrapper.
 * Shows a spinner when user pulls down on touch devices.
 */
import { useState, useRef, useCallback } from "react";
import { RefreshCw } from "lucide-react";

const THRESHOLD = 80;

const PullToRefresh = ({ onRefresh, children, disabled = false }) => {
  const [pulling, setPulling] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [pullDistance, setPullDistance] = useState(0);
  const startY = useRef(0);
  const containerRef = useRef(null);

  const canPull = () => {
    if (disabled || refreshing) return false;
    return window.scrollY <= 0;
  };

  const handleTouchStart = useCallback((e) => {
    if (!canPull()) return;
    startY.current = e.touches[0].clientY;
  }, [disabled, refreshing]);

  const handleTouchMove = useCallback((e) => {
    if (!canPull() || startY.current === 0) return;
    const diff = e.touches[0].clientY - startY.current;
    if (diff > 0) {
      setPulling(true);
      setPullDistance(Math.min(diff * 0.5, THRESHOLD * 1.5));
    }
  }, [disabled, refreshing]);

  const handleTouchEnd = useCallback(async () => {
    if (!pulling) { startY.current = 0; return; }
    if (pullDistance >= THRESHOLD && onRefresh) {
      setRefreshing(true);
      setPullDistance(THRESHOLD * 0.6);
      try {
        await onRefresh();
      } finally {
        setRefreshing(false);
      }
    }
    setPulling(false);
    setPullDistance(0);
    startY.current = 0;
  }, [pulling, pullDistance, onRefresh]);

  return (
    <div
      ref={containerRef}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
      data-testid="pull-to-refresh"
    >
      {(pulling || refreshing) && (
        <div
          className="flex items-center justify-center transition-all overflow-hidden"
          style={{ height: pullDistance }}
          data-testid="pull-indicator"
        >
          <RefreshCw
            className={`w-5 h-5 text-[#7B61FF] transition-transform ${
              refreshing ? "animate-spin" : ""
            }`}
            style={{
              transform: !refreshing ? `rotate(${(pullDistance / THRESHOLD) * 360}deg)` : undefined,
              opacity: Math.min(pullDistance / THRESHOLD, 1),
            }}
          />
        </div>
      )}
      {children}
    </div>
  );
};

export default PullToRefresh;
