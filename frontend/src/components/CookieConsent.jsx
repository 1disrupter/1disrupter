import { useState, useEffect } from "react";
import { X } from "lucide-react";

const STORAGE_KEY = "alphaai_cookie_consent";

const CookieConsent = () => {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const consent = localStorage.getItem(STORAGE_KEY);
    if (!consent) setVisible(true);
  }, []);

  const handleAccept = () => {
    localStorage.setItem(STORAGE_KEY, "accepted");
    setVisible(false);
  };

  const handleReject = () => {
    localStorage.setItem(STORAGE_KEY, "rejected");
    setVisible(false);
  };

  if (!visible) return null;

  return (
    <div
      className="fixed bottom-0 left-0 right-0 z-[60] px-4 py-3 bg-[#0B0B0F] border-t border-zinc-800"
      data-testid="cookie-consent-banner"
    >
      <div className="max-w-4xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="text-zinc-400 text-xs font-mono text-center sm:text-left">
          We use cookies for analytics and improving your experience.
        </p>
        <div className="flex items-center gap-2 shrink-0">
          <button
            onClick={handleAccept}
            className="px-4 py-1.5 bg-[#7B61FF] hover:bg-[#7B61FF]/90 text-white text-xs font-medium rounded-full transition-colors"
            data-testid="cookie-accept-btn"
          >
            Accept
          </button>
          <button
            onClick={handleReject}
            className="px-4 py-1.5 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-medium rounded-full transition-colors"
            data-testid="cookie-reject-btn"
          >
            Reject
          </button>
        </div>
      </div>
    </div>
  );
};

export default CookieConsent;
