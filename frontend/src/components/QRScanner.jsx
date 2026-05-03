import QrReader from 'react-qr-scanner';
import { useState } from 'react';

export default function QRScanner({ onClose }) {
  const [error, setError] = useState(null);

  const handleResult = async (result) => {
    if (result?.text) {
      try {
        const url = result.text;
        const venueId = new URL(url).searchParams.get("venue");

        await fetch("https://api.vibe2nite.com/api/checkin", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ venueId })
        });

        alert("✅ Checked in! Tokens pending");
        onClose();

      } catch (err) {
        setError("Scan failed");
      }
    }
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col items-center justify-center">
      <button onClick={onClose} className="text-white mb-4">Close</button>
    
      <div className="w-full max-w-md">
        <QrReader
          onResult={(result, error) => {
            if (result) handleResult(result);
            if (error) setError(error?.message);
          }}
          constraints={{ facingMode: "environment" }}
        />
      </div>

      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  );
}
