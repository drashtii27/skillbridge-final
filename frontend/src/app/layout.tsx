import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";
import AnimatedCursor from "@/components/ui/AnimatedCursor";
import ParticleBackground from "@/components/ui/ParticleBackground";
import PostHogProvider from "@/components/ui/PostHogProvider";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const jetbrains = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jetbrains" });

export const metadata: Metadata = {
  title: "SkillBridge AI — Your AI Career Co-Pilot",
  description: "Upload your resume, discover skill gaps, and get a personalized career roadmap powered by NVIDIA Nemotron.",
  openGraph: {
    title: "SkillBridge AI",
    description: "AI-powered career roadmap & skill gap analysis",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <body className="antialiased">
        <PostHogProvider>
          <ParticleBackground />
          <AnimatedCursor />
          <div className="relative z-10">{children}</div>
          <Toaster
            position="top-right"
            toastOptions={{
              style: {
                background: "rgba(15, 15, 30, 0.95)",
                border: "1px solid rgba(99, 102, 241, 0.3)",
                color: "#f9fafb",
                backdropFilter: "blur(20px)",
              },
            }}
          />
        </PostHogProvider>
      </body>
    </html>
  );
}
