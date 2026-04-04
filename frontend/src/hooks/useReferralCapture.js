import { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import axios from "axios";
import { API } from "../lib/constants";

const REFERRAL_STORAGE_KEY = "alphaai_referral_code";

/**
 * Hook to capture ?ref= from URL, validate it, store in localStorage, and clean the URL.
 * Mount once in App.js inside BrowserRouter.
 */
const useReferralCapture = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  useEffect(() => {
    const ref = searchParams.get("ref");
    if (!ref) return;

    // Already have a stored referral — don't overwrite
    if (localStorage.getItem(REFERRAL_STORAGE_KEY)) {
      // Clean URL
      searchParams.delete("ref");
      setSearchParams(searchParams, { replace: true });
      return;
    }

    (async () => {
      try {
        const { data } = await axios.get(`${API}/referrals/validate/${encodeURIComponent(ref)}`);
        if (data.valid) {
          localStorage.setItem(REFERRAL_STORAGE_KEY, data.referral_code);
          // Track click
          axios.post(`${API}/referrals/track-click`, null, { params: { code: data.referral_code } }).catch(() => {});
        }
      } catch {
        // Invalid ref — ignore silently
      }
      // Clean URL
      searchParams.delete("ref");
      setSearchParams(searchParams, { replace: true });
    })();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps
};

/**
 * Get the stored referral code (if any). Used during signup.
 */
export const getStoredReferralCode = () => {
  return localStorage.getItem(REFERRAL_STORAGE_KEY);
};

/**
 * Clear the stored referral code. Call after successful signup with referral.
 */
export const clearStoredReferralCode = () => {
  localStorage.removeItem(REFERRAL_STORAGE_KEY);
};

export default useReferralCapture;
