import { useEffect, useState, useCallback } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";

 export default function QRScanner({ onClose, onCheckInSuccess }){
  const [scanned, setScanned] = useState(false);

  // UX STATES
  const [status, setStatus] = useState("scanning"); 
  // scanning | loading | success | error

  const [message, setMessage] = useState("");

  const handleResult = useCallback(
    async (decodedText) => {
      try {
        // 📳 vibration feedback
        if (navigator.vibrate) {
          navigator.vibrate(100);
        }

        setStatus("loading");

        let venueId;

        try {
          const url = new URL(decodedText);
          venueId = url.searchParams.get("venue");
        } catch {
          venueId = decodedText;
        }

        if (!venueId) {
          setStatus("error");
          setMessage("Invalid QR code");
          return;
        }

        const deviceId =
          localStorage.getItem("deviceId") || crypto.randomUUID();

        localStorage.setItem("deviceId", deviceId);

        const res = await fetch("https://api.vibe2nite.com/api/checkin", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            venueId,
            deviceId,
          }),
        });

        const result = await res.json();

        if (result.success) {
  setStatus("success");
  setMessage(
    `Checked in · ${result.reward.tokens} tokens earned`
  );

  // 🔥 THIS IS THE CONNECTION
  if (onCheckInSuccess) {
    onCheckInSuccess(result);
  }

} else {
          setStatus("error");
          setMessage("Check-in failed");
        }

        // ⏱ smoother close timing
        setTimeout(() => {
          onClose();
        }, 2500);

      } catch (err) {
        console.error(err);
        setStatus("error");
        setMessage("Error checking in");
      }
    },
    [onClose]
  );

  useEffect(() => {
    // 🛑 only run scanner when actively scanning
    if (status !== "scanning") return;

    const scanner = new Html5QrcodeScanner(
      "reader",
      { fps: 10, qrbox: 250 },
      false
    );

    scanner.render(
      (decodedText) => {
        if (!scanned) {
          setScanned(true);
          handleResult(decodedText);
          scanner.clear();
        }
      },
      () => {}
    );

    return () => scanner.clear().catch(() => {});
  }, [scanned, handleResult, status]);

  return (
    <div className="fixed inset-0 bg-black/90 z-50 flex flex-col items-center justify-center p-4">

      {/* CLOSE BUTTON */}
      <button 
        onClick={onClose} 
        className="text-white mb-4 text-sm uppercase tracking-wider border border-white/20 px-4 py-2 rounded-lg"
      >
        Close
      </button>

      {/* TITLE */}
      <h2 className="text-white mb-3 text-xs uppercase tracking-widest opacity-70">
        Scan Venue QR
      </h2>

      {/* SCANNING */}
      {status === "scanning" && (
        <div className="w-full max-w-md rounded-xl overflow-hidden border border-white/10 bg-black p-2">
          <div id="reader" className="w-full" />
        </div>
      )}

      {/* LOADING */}
      {status === "loading" && (
        <div className="text-white text-center">
          <p className="text-sm opacity-70 animate-pulse">
            Checking you in...
          </p>
        </div>
      )}

      {/* SUCCESS */}
      {status === "success" && (
        <div className="text-center text-green-400 animate-pulse">
          <p className="text-lg">✅ Success</p>
          <p className="text-sm mt-2">{message}</p>
        </div>
      )}

      {/* ERROR */}
      {status === "error" && (
        <div className="text-center text-red-400">
          <p className="text-lg">❌ Error</p>
          <p className="text-sm mt-2">{message}</p>

          <button
            onClick={() => {
              setStatus("scanning");
              setScanned(false);
            }}
            className="mt-4 text-white border border-white/20 px-3 py-1 rounded"
          >
            Try Again
          </button>
        </div>
      )}

    </div>
  );
}
     
