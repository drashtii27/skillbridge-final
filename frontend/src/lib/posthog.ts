"use client";

import posthog from "posthog-js";

let initialized = false;

export function initPostHog() {
  if (initialized || typeof window === "undefined") return;
  const key = process.env.NEXT_PUBLIC_POSTHOG_KEY;
  const host = process.env.NEXT_PUBLIC_POSTHOG_HOST || "https://us.i.posthog.com";
  if (!key) return;
  posthog.init(key, { api_host: host, person_profiles: "identified_only", capture_pageview: false });
  initialized = true;
}

export function trackEvent(event: string, props?: Record<string, unknown>) {
  if (typeof window === "undefined" || !initialized) return;
  posthog.capture(event, props);
}

export function identifyUser(userId: string, email: string, name: string) {
  if (typeof window === "undefined" || !initialized) return;
  posthog.identify(userId, { email, name });
}

export { posthog };
