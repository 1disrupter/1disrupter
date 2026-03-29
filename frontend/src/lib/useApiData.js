import { useState, useEffect, useCallback } from 'react';
import { API } from './constants';

/**
 * Generic fetch hook for dashboard pages.
 * Returns { data, loading, error, refetch }.
 * Skipped entirely when `skip` is true (e.g. demo mode).
 */
export function useApiData(path, { skip = false, token = null, defaultValue = null } = {}) {
  const [data, setData] = useState(defaultValue);
  const [loading, setLoading] = useState(!skip);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (skip) return;
    setLoading(true);
    setError(null);
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers.Authorization = `Bearer ${token}`;
      const res = await fetch(`${API}${path}`, { headers });
      if (!res.ok) throw new Error(`${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [path, skip, token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
