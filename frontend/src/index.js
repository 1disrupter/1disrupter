
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import "./index.css";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
);

// PWA: register the service worker in production only. CRA dev server
// regenerates assets on every save, so caching them in dev causes stale
// builds and would mask real issues.
if (process.env.NODE_ENV === "production" && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => {
      // Registration failures are non-fatal — app still works, just no
      // offline shell or installable PWA on this visit.
    });
  });
}

