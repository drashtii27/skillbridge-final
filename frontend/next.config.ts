import type { NextConfig } from "next";

const BACKEND = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  output: "standalone",
  images: { remotePatterns: [{ protocol: "https", hostname: "**" }, { protocol: "http", hostname: "localhost" }] },
  async rewrites() {
    return [
      // Proxy every /api/* and /static/* call to the FastAPI backend.
      // The browser only ever talks to localhost:3000 — no cross-origin at all.
      {
        source: "/api/:path*",
        destination: `${BACKEND}/api/:path*`,
      },
      {
        source: "/static/:path*",
        destination: `${BACKEND}/static/:path*`,
      },
    ];
  },
};

export default nextConfig;
