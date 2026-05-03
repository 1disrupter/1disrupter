import { useEffect } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";

export default function QRScanner({ onClose }) {
  useEffect(() => {
    const scanner = new Html5QrcodeScanner(
      "reader",
      { fps: 10, qrbox: 250 },
      false
    );

    scanner.render(
      (decodedText) => {
        handleResult({ text: decodedText });
        scanner.clear();
        onClose();
      },
      (error) => {}
    );

    return () => scanner.clear().catch(() => {});
  }, []);

  const handleResult = async (result) => {
    try {
      const url = result.text;
      const venueId = new URL(url).searchParams.get("venue");

      await fetch("https://api.vibe2nite.com/api/checkin", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ venueId })
      });

      alert("✅ Checked in! Tokens pending");
      onClose();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col items-center justify-center">
      <button onClick={onClose} className="text-white mb-4">
        Close
      </button>

      <div id="reader" className="w-full max-w-md bg-white" />
    </div>
  );
}

     
