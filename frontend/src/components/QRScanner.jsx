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
    <div className="fixed inset-0 bg-black z-50 flex flex-col items-center justify-center">
      <button onClick={onClose} className="text-white mb-4">
        Close
      </button>

      <div id="reader" className="w-full max-w-md bg-white" />
    </div>
  );
}
     
