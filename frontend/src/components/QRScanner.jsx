import { useEffect, useState, useCallback } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";

export default function QRScanner({ onClose }) {
  const [scanned, setScanned] = useState(false);

  const handleResult = useCallback(
    async (decodedText) => {
      try {
        let venueId;

        try {
          const url = new URL(decodedText);
          venueId = url.searchParams.get("venue");
        } catch {
          venueId = decodedText;
        }

        if (!venueId) {
          alert("❌ Invalid QR code");
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
          alert(
            `✅ Checked in!\nGroup size: ${result.group_size}\nReward: ${result.reward.tier} (${result.reward.tokens} tokens)`
          );
        } else {
          alert("❌ Check-in failed");
        }

        onClose();
      } catch (err) {
        console.error(err);
        alert("❌ Error checking in");
      }
    },
    [onClose]
  );

  useEffect(() => {
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
  }, [scanned, handleResult]);

return (
  <div className="fixed inset-0 bg-black/90 z-50 flex flex-col items-center justify-center p-4">
    
    <button 
      onClick={onClose} 
      className="text-white mb-4 text-sm uppercase tracking-wider border border-white/20 px-4 py-2 rounded-lg"
    >
      Close
    </button>

    <div className="w-full max-w-md rounded-xl overflow-hidden border border-white/10 bg-black p-2">
      <div id="reader" className="w-full" />
    </div>

  </div>
);
}
     
