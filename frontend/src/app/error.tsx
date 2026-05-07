"use client";

import { useEffect } from "react";

export default function Error({
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
    <div className="min-h-screen flex flex-col items-center justify-center bg-[#080d1a] text-white px-4">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-6">⚠️</div>
        <h2 className="text-2xl font-bold mb-3 text-red-400">Something went wrong</h2>
        <p className="text-slate-400 mb-8 text-sm">{error.message || "An unexpected error occurred."}</p>
        <button
          onClick={reset}
          className="px-6 py-3 bg-red-600 hover:bg-red-500 text-white rounded-lg font-medium transition-colors"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
