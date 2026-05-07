"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html>
      <body style={{ margin: 0, background: "#080d1a", color: "#fff", fontFamily: "sans-serif" }}>
        <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "2rem", textAlign: "center" }}>
          <div style={{ fontSize: "4rem", marginBottom: "1.5rem" }}>⚠️</div>
          <h2 style={{ color: "#f87171", marginBottom: "0.75rem" }}>Application Error</h2>
          <p style={{ color: "#94a3b8", marginBottom: "2rem", fontSize: "0.875rem" }}>
            {error.message || "A critical error occurred. Please try refreshing."}
          </p>
          <button
            onClick={reset}
            style={{ padding: "0.75rem 1.5rem", background: "#dc2626", color: "#fff", border: "none", borderRadius: "0.5rem", cursor: "pointer", fontWeight: 600 }}
          >
            Reload
          </button>
        </div>
      </body>
    </html>
  );
}
