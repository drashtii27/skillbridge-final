"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { Trophy, Zap } from "lucide-react";
import { useAppStore } from "@/store/useAppStore";
import GlassCard from "@/components/ui/GlassCard";

const ALL_BADGES = [
  { id: "resume_uploaded", title: "Resume Pioneer", icon: "📄", xp: 50, desc: "Uploaded your first resume" },
  { id: "roadmap_generated", title: "Roadmap Starter", icon: "🗺️", xp: 100, desc: "Generated your first roadmap" },
  { id: "quiz_ace", title: "Quiz Ace", icon: "🧠", xp: 150, desc: "Scored 80%+ on a quiz" },
  { id: "week_1_done", title: "Week 1 Warrior", icon: "⚔️", xp: 200, desc: "Completed Week 1 of roadmap" },
  { id: "job_applied", title: "Job Hunter", icon: "💼", xp: 75, desc: "Applied to your first job" },
  { id: "interview_ready", title: "Interview Ready", icon: "🎤", xp: 100, desc: "Practiced 10+ interview questions" },
  { id: "streak_3", title: "3-Day Streak", icon: "🔥", xp: 120, desc: "Active 3 days in a row" },
  { id: "community_joiner", title: "Community Star", icon: "⭐", xp: 50, desc: "Joined a learning community" },
];

export default function BadgesPage() {
  const router = useRouter();
  const { user, completedSteps } = useAppStore();
  const earnedBadges = user?.badges || [];

  const totalXP = user?.xp || completedSteps.length * 10;
  const level = Math.floor(totalXP / 200) + 1;
  const levelProgress = ((totalXP % 200) / 200) * 100;

  return (
    <main className="min-h-screen gradient-mesh px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-black text-white flex items-center gap-3">
              <Trophy className="w-8 h-8 text-amber-400" /> Achievements
            </h1>
            <p className="text-gray-400 text-sm mt-1">{earnedBadges.length}/{ALL_BADGES.length} badges earned</p>
          </div>
          <button onClick={() => router.back()} className="btn-ghost text-sm py-2 px-4">← Back</button>
        </motion.div>

        {/* XP / Level card */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="mb-8">
          <GlassCard glow>
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-sm text-gray-400">Your Level</p>
                <div className="text-5xl font-black gradient-text">{level}</div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-400">Total XP</p>
                <div className="flex items-center gap-2 text-3xl font-black text-amber-400">
                  <Zap className="w-6 h-6" />{totalXP}
                </div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs text-gray-500 mb-1">
                <span>Level {level}</span>
                <span>{Math.round(levelProgress)}% to Level {level + 1}</span>
              </div>
              <div className="bg-white/5 rounded-full h-2">
                <div className="h-2 rounded-full progress-bar transition-all duration-1000" style={{ width: `${levelProgress}%` }} />
              </div>
            </div>
          </GlassCard>
        </motion.div>

        {/* Badges grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {ALL_BADGES.map((badge, i) => {
            const earned = earnedBadges.includes(badge.id);
            return (
              <motion.div
                key={badge.id}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.15 + i * 0.05 }}
              >
                <div className={`glass rounded-2xl p-5 text-center transition-all duration-300 relative overflow-hidden
                  ${earned ? "border border-amber-500/30 neon-border" : "border border-white/5 opacity-50 grayscale"}`}
                  style={earned ? { boxShadow: "0 0 30px rgba(245,158,11,0.15)" } : undefined}
                >
                  {earned && (
                    <div className="absolute top-2 right-2">
                      <span className="text-xs text-amber-400 font-bold">✓</span>
                    </div>
                  )}
                  <div className="text-4xl mb-2">{badge.icon}</div>
                  <h3 className={`font-bold text-sm mb-1 ${earned ? "text-white" : "text-gray-500"}`}>{badge.title}</h3>
                  <p className="text-xs text-gray-500 mb-2">{badge.desc}</p>
                  <div className={`text-xs font-bold flex items-center justify-center gap-1 ${earned ? "text-amber-400" : "text-gray-600"}`}>
                    <Zap className="w-3 h-3" /> +{badge.xp} XP
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Progress stats */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.6 }} className="mt-8">
          <GlassCard>
            <h2 className="font-bold text-white mb-4">📊 Your Stats</h2>
            <div className="grid grid-cols-3 gap-4">
              {[
                { label: "Badges Earned", value: earnedBadges.length, max: ALL_BADGES.length },
                { label: "Steps Completed", value: completedSteps.length, max: null },
                { label: "Current Level", value: `L${level}`, max: null },
              ].map((s) => (
                <div key={s.label} className="text-center">
                  <div className="text-2xl font-black gradient-text">{s.value}{s.max ? `/${s.max}` : ""}</div>
                  <div className="text-xs text-gray-400 mt-1">{s.label}</div>
                </div>
              ))}
            </div>
          </GlassCard>
        </motion.div>
      </div>
    </main>
  );
}
