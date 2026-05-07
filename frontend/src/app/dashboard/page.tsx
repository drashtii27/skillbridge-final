"use client";

import { useEffect } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Map, MessageSquare, Briefcase, Award, TrendingUp, ChevronRight, Zap } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import GlassCard from "@/components/ui/GlassCard";
import SkillGapChart from "@/components/SkillGapChart";
import JobCard from "@/components/JobCard";

export default function DashboardPage() {
  const router = useRouter();
  const { gapResult, roadmap, jobs, user, resumeSkills, completedSteps } = useAppStore();

  useEffect(() => {
    if (!gapResult) router.replace("/");
  }, [gapResult, router]);

  if (!gapResult) return null;

  const totalWeeks = roadmap?.phases?.reduce((acc, p) => acc + p.weeks.length, 0) || 0;
  const progressPct = totalWeeks ? Math.round((completedSteps.length / totalWeeks) * 100) : 0;

  const nav = [
    { href: "/dashboard/roadmap", icon: <Map className="w-5 h-5" />, label: "Roadmap Journey", desc: "Car-animated learning path", color: "red" },
    { href: "/dashboard/interview", icon: <MessageSquare className="w-5 h-5" />, label: "Interview Prep", desc: "AI-generated Q&A + quiz", color: "orange" },
    { href: "/dashboard/badges", icon: <Award className="w-5 h-5" />, label: "Badges & XP", desc: "Your achievements", color: "amber" },
  ];

  return (
    <main className="min-h-screen gradient-mesh px-4 py-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black text-white">
              {user?.name ? `Welcome, ${user.name.split(" ")[0]} 👋` : "Your Dashboard"}
            </h1>
            <p className="text-gray-400 mt-1">
              Targeting: <span className="text-red-300 font-semibold">{gapResult.role}</span>
            </p>
          </div>
          <div className="flex items-center gap-3">
            {user && (
              <div className="flex items-center gap-2 glass px-4 py-2 rounded-xl">
                <Zap className="w-4 h-4 text-amber-400" />
                <span className="text-amber-300 font-bold">{user.xp} XP</span>
              </div>
            )}
            <Link href="/" className="btn-ghost text-sm">← New Analysis</Link>
          </div>
        </motion.div>

        {/* Readiness + Progress */}
        <div className="grid md:grid-cols-3 gap-6">
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }}>
            <GlassCard glow>
              <p className="text-sm text-gray-400 mb-2">Readiness Score</p>
              <div className="text-5xl font-black gradient-text">{gapResult.readiness_pct}%</div>
              <p className="text-xs text-gray-500 mt-2">Skills match for {gapResult.role}</p>
              <div className="mt-4 bg-white/5 rounded-full h-2">
                <div className="h-2 rounded-full progress-bar" style={{ width: `${gapResult.readiness_pct}%` }} />
              </div>
            </GlassCard>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}>
            <GlassCard>
              <p className="text-sm text-gray-400 mb-2">Roadmap Progress</p>
              <div className="text-5xl font-black text-white">{progressPct}<span className="text-2xl text-gray-400">%</span></div>
              <p className="text-xs text-gray-500 mt-2">{completedSteps.length}/{totalWeeks} weeks complete</p>
              <div className="mt-4 bg-white/5 rounded-full h-2">
                <div className="h-2 rounded-full bg-emerald-500" style={{ width: `${progressPct}%` }} />
              </div>
            </GlassCard>
          </motion.div>

          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
            <GlassCard>
              <p className="text-sm text-gray-400 mb-2">Skills Gap</p>
              <div className="text-5xl font-black text-white">{gapResult.gaps.length}</div>
              <p className="text-xs text-gray-500 mt-2">skills to learn for {gapResult.role}</p>
              <div className="mt-3 flex flex-wrap gap-1">
                {gapResult.gaps.slice(0, 3).map((g) => (
                  <span key={g.skill} className="skill-tag-danger text-xs px-2 py-0.5 rounded-full">{g.skill}</span>
                ))}
                {gapResult.gaps.length > 3 && <span className="text-xs text-gray-500">+{gapResult.gaps.length - 3} more</span>}
              </div>
            </GlassCard>
          </motion.div>
        </div>

        {/* Market Insight */}
        {gapResult.market_insight && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
            <GlassCard className="border-l-4 border-red-500">
              <div className="flex gap-3">
                <TrendingUp className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-red-300 mb-1">2026 Market Insight</p>
                  <p className="text-gray-300 text-sm leading-relaxed">{gapResult.market_insight}</p>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        )}

        {/* Skill Gap Chart */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <SkillGapChart gapResult={gapResult} />
        </motion.div>

        {/* Navigation cards */}
        <div className="grid md:grid-cols-3 gap-4">
          {nav.map((n, i) => (
            <motion.div
              key={n.href}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 + i * 0.1 }}
            >
              <Link href={n.href}>
                <GlassCard hover className="group">
                  <div className={`w-10 h-10 rounded-xl bg-${n.color}-500/10 border border-${n.color}-500/20 flex items-center justify-center text-${n.color}-400 mb-3`}>
                    {n.icon}
                  </div>
                  <h3 className="font-bold text-white group-hover:gradient-text transition-all">{n.label}</h3>
                  <p className="text-xs text-gray-400 mt-1 mb-3">{n.desc}</p>
                  <div className="flex items-center gap-1 text-xs text-red-400">
                    Open <ChevronRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                  </div>
                </GlassCard>
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Jobs preview */}
        {jobs.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <Briefcase className="w-5 h-5 text-red-400" /> Live Job Matches
              </h2>
              <span className="text-xs text-gray-400">{jobs.length} positions</span>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {jobs.slice(0, 6).map((job, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.55 + i * 0.05 }}>
                  <JobCard job={job} />
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </main>
  );
}
