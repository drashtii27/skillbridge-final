import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        primary: "#6366f1",
        secondary: "#8b5cf6",
        accent: "#06b6d4",
        success: "#10b981",
        warning: "#f59e0b",
        danger: "#ef4444",
        "bg-dark": "#030712",
        "bg-card": "rgba(255,255,255,0.03)",
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-jetbrains)", "monospace"],
      },
      animation: {
        "float": "float 6s ease-in-out infinite",
        "pulse-glow": "pulse-glow 2s ease-in-out infinite",
        "gradient-shift": "gradient-shift 8s ease infinite",
        "spin-slow": "spin 8s linear infinite",
        "bounce-slow": "bounce 3s ease-in-out infinite",
        "fade-up": "fade-up 0.5s ease-out forwards",
        "car-drive": "car-drive 2s ease-in-out",
        "badge-pop": "badge-pop 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55) forwards",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-20px)" },
        },
        "pulse-glow": {
          "0%, 100%": { boxShadow: "0 0 5px rgba(99,102,241,0.4)" },
          "50%": { boxShadow: "0 0 25px rgba(99,102,241,0.9), 0 0 50px rgba(99,102,241,0.3)" },
        },
        "gradient-shift": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "badge-pop": {
          "0%": { transform: "scale(0) rotate(-10deg)", opacity: "0" },
          "100%": { transform: "scale(1) rotate(0deg)", opacity: "1" },
        },
      },
      backdropBlur: { xs: "2px" },
      backgroundSize: { "300%": "300%" },
    },
  },
  plugins: [],
};

export default config;
