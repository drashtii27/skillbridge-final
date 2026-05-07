"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { LayoutDashboard, Map, MessageSquare, Award, Briefcase, LogOut, Zap, ArrowLeft } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import { clsx } from "clsx";

const NAV = [
  { href: "/dashboard", icon: <LayoutDashboard className="w-4 h-4" />, label: "Overview", exact: true },
  { href: "/dashboard/roadmap", icon: <Map className="w-4 h-4" />, label: "Roadmap" },
  { href: "/dashboard/interview", icon: <MessageSquare className="w-4 h-4" />, label: "Interview" },
  { href: "/dashboard/badges", icon: <Award className="w-4 h-4" />, label: "Badges & XP" },
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { gapResult, user, setUser, setAccessToken, setGapResult, setRoadmap } = useAppStore();

  useEffect(() => {
    if (!gapResult) router.replace("/");
  }, [gapResult, router]);

  const logout = () => {
    setUser(null);
    setAccessToken(null);
    setGapResult(null);
    setRoadmap(null);
    router.replace("/");
  };

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-56 glass border-r border-white/5 fixed inset-y-0 left-0 z-40 p-4">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 px-2 mb-8 group">
          <div className="w-8 h-8 rounded-lg bg-red-500/20 border border-red-500/30 flex items-center justify-center">
            <span className="text-red-400 font-black text-sm">SB</span>
          </div>
          <span className="font-black text-white group-hover:gradient-text transition-all">SkillBridge</span>
        </Link>

        {/* User XP pill */}
        {user && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-amber-500/5 border border-amber-500/15 mb-6">
            <Zap className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-bold text-amber-300">{user.xp} XP</span>
            <span className="text-xs text-gray-500 ml-auto">Lv.{Math.floor(user.xp / 200) + 1}</span>
          </div>
        )}

        {/* Nav links */}
        <nav className="flex-1 space-y-1">
          {NAV.map((item) => {
            const active = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                  active
                    ? "bg-red-500/15 text-white border border-red-500/20"
                    : "text-gray-400 hover:text-white hover:bg-white/5"
                )}
              >
                <span className={active ? "text-red-400" : ""}>{item.icon}</span>
                {item.label}
                {active && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-red-400"
                  />
                )}
              </Link>
            );
          })}
        </nav>

        {/* Bottom actions */}
        <div className="space-y-1 pt-4 border-t border-white/5">
          <Link href="/" className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-all">
            <ArrowLeft className="w-4 h-4" /> New Analysis
          </Link>
          {user && (
            <button onClick={logout} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-gray-400 hover:text-red-400 hover:bg-red-500/5 transition-all">
              <LogOut className="w-4 h-4" /> Sign Out
            </button>
          )}
        </div>
      </aside>

      {/* Mobile top bar */}
      <div className="md:hidden fixed top-0 inset-x-0 z-40 glass border-b border-white/5 px-4 h-14 flex items-center justify-between">
        <Link href="/" className="font-black text-white">SkillBridge</Link>
        <div className="flex gap-1">
          {NAV.map((item) => {
            const active = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            return (
              <Link key={item.href} href={item.href}
                className={clsx("p-2 rounded-lg transition-colors", active ? "text-red-400 bg-red-500/10" : "text-gray-400")}>
                {item.icon}
              </Link>
            );
          })}
        </div>
      </div>

      {/* Main content */}
      <main className="flex-1 md:ml-56 pt-14 md:pt-0">
        {children}
      </main>
    </div>
  );
}
