"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import { Youtube, BookOpen, Code2, ExternalLink, Check, ChevronDown, ChevronUp, Trophy, Users, MessageCircle, Download } from "lucide-react";
import toast from "react-hot-toast";
import { useAppStore } from "@/store/useAppStore";
import { updateProgress } from "@/lib/api";
import { trackEvent } from "@/lib/posthog";
import CarJourney from "@/components/roadmap/CarJourney";
import GlassCard from "@/components/ui/GlassCard";
import confetti from "canvas-confetti";
import type { Week, Resource } from "@/types";

const RESOURCE_ICONS: Record<string, React.ReactNode> = {
  youtube:  <Youtube  className="w-4 h-4 text-red-400" />,
  course:   <BookOpen className="w-4 h-4 text-orange-400" />,
  docs:     <Code2    className="w-4 h-4 text-gray-400" />,
  practice: <Code2    className="w-4 h-4 text-amber-400" />,
};

export default function RoadmapPage() {
  const router = useRouter();
  const { roadmap, completedSteps, setCompletedSteps, user } = useAppStore();
  const [expandedWeek, setExpandedWeek] = useState<string | null>(null);

  useEffect(() => {
    if (!roadmap) router.replace("/");
  }, [roadmap, router]);

  if (!roadmap) return null;

  const allWeeks    = roadmap.phases.flatMap((p) => p.weeks);
  const totalWeeks  = allWeeks.length;
  // Use actual completedSteps length for real progress (not car_position_pct from JSON)
  const overallProgress = totalWeeks
    ? Math.round((completedSteps.length / totalWeeks) * 100)
    : 0;

  const milestones = allWeeks.map((w, i) => ({
    position_pct: Math.round(((i + 1) / totalWeeks) * 90) + 5,
    label: w.skills_focus[0] || `Week ${w.week}`,
    completed: completedSteps.includes(`w${w.month}_${w.week}`),
    active: completedSteps.length === i,
  }));

  const handleMarkDone = async (week: Week) => {
    const stepId = `w${week.month}_${week.week}`;
    if (completedSteps.includes(stepId)) return;

    const newSteps = [...completedSteps, stepId];
    setCompletedSteps(newSteps);
    trackEvent("milestone_completed", { step: stepId, role: roadmap.role });

    if (roadmap.roadmap_id && user) {
      updateProgress(roadmap.roadmap_id, stepId).catch(() => {});
    }

    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 },
      colors: ["#ef4444", "#f97316", "#fca5a5", "#ffffff"],
    });

    const newPct = Math.round((newSteps.length / totalWeeks) * 100);
    if (newPct === 100) {
      toast.success("You completed the entire roadmap!", { duration: 5000 });
    } else {
      toast.success(`Week ${week.week} done! ${newPct}% complete`);
    }
  };

  const handleResourceClick = (r: Resource) => {
    trackEvent("resource_clicked", { type: r.type, title: r.title, url: r.url });
    window.open(r.url, "_blank", "noopener,noreferrer");
  };

  const exportToOpenNote = () => {
    const md = roadmap.export.opennote_markdown;
    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${roadmap.role.replace(/\s+/g, "-")}-roadmap.md`;
    a.click();
    URL.revokeObjectURL(url);
    trackEvent("roadmap_exported");
    toast.success("Roadmap exported as Markdown — import into Obsidian or Notion!");
  };

  return (
    <main className="min-h-screen gradient-mesh">
      {/* Sticky header */}
      <div className="sticky top-0 z-50 glass-dark px-4 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="font-black text-lg text-white">{roadmap.role} Roadmap</h1>
            <p className="text-xs text-gray-400">{roadmap.months} months · {totalWeeks} weeks</p>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-3 glass rounded-lg px-4 py-2">
              <div className="text-xs text-gray-400">Progress</div>
              <div className="w-32 bg-white/5 rounded-full h-1.5">
                <div
                  className="h-1.5 rounded-full progress-bar transition-all duration-1000"
                  style={{ width: `${overallProgress}%` }}
                />
              </div>
              <div className="text-xs font-bold text-white">{overallProgress}%</div>
            </div>
            <button onClick={exportToOpenNote} className="flex items-center gap-2 btn-ghost text-sm py-2 px-4">
              <Download className="w-4 h-4" /> Export
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[280px_1fr] gap-8">
          {/* Car Journey sidebar */}
          <div className="hidden lg:block sticky top-24 self-start">
            <GlassCard className="p-4">
              <h3 className="text-sm font-bold text-white mb-3">Your Journey</h3>
              <CarJourney milestones={milestones} overallProgress={overallProgress} />
              <div className="mt-4 space-y-1.5 text-xs text-gray-500">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block" /> Completed
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /> In Progress
                </div>
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-zinc-700 inline-block" /> Upcoming
                </div>
              </div>
            </GlassCard>
          </div>

          {/* Phases */}
          <div className="space-y-8">
            {roadmap.phases.map((phase) => (
              <motion.div
                key={phase.month}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                {/* Phase header */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-red-500/15 border border-red-500/25 flex items-center justify-center font-black text-red-400">
                    {phase.month}
                  </div>
                  <div>
                    <h2 className="font-bold text-white text-lg">{phase.title}</h2>
                    <p className="text-xs text-gray-400">Month {phase.month} · {phase.weeks.length} weeks</p>
                  </div>
                </div>

                <div className="space-y-4 ml-14 border-l border-white/5 pl-4">
                  {phase.weeks.map((week) => {
                    const stepId = `w${week.month}_${week.week}`;
                    const isDone = completedSteps.includes(stepId);
                    const isOpen = expandedWeek === stepId;

                    return (
                      <motion.div
                        key={stepId}
                        layout
                        className={`glass rounded-xl overflow-hidden transition-all duration-300 ${
                          isDone ? "border border-emerald-500/20" : "border border-white/5"
                        }`}
                      >
                        <button
                          className="w-full flex items-center justify-between p-4 text-left"
                          onClick={() => setExpandedWeek(isOpen ? null : stepId)}
                        >
                          <div className="flex items-center gap-3">
                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold
                              ${isDone
                                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/25"
                                : "bg-red-500/10 text-red-400 border border-red-500/20"
                              }`}>
                              {isDone ? <Check className="w-4 h-4" /> : `W${week.week}`}
                            </div>
                            <div>
                              <p className="font-semibold text-white text-sm">
                                Week {week.week}: {week.skills_focus.join(", ")}
                              </p>
                              <p className="text-xs text-gray-500 mt-0.5">{week.daily_plan}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 flex-shrink-0">
                            {isDone && <span className="text-xs text-emerald-400 font-medium">Done</span>}
                            {isOpen
                              ? <ChevronUp className="w-4 h-4 text-gray-400" />
                              : <ChevronDown className="w-4 h-4 text-gray-400" />}
                          </div>
                        </button>

                        <AnimatePresence>
                          {isOpen && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.3 }}
                              className="border-t border-white/5"
                            >
                              <div className="p-4 space-y-4">
                                {/* Resources */}
                                <div>
                                  <p className="text-xs text-gray-500 uppercase tracking-wider mb-2">Resources</p>
                                  <div className="grid sm:grid-cols-2 gap-2">
                                    {week.resources.map((r, ri) => (
                                      <button
                                        key={ri}
                                        onClick={() => handleResourceClick(r)}
                                        className="flex items-start gap-2 p-3 rounded-lg bg-white/3 border border-white/5 hover:border-red-500/25 hover:bg-red-500/5 transition-all text-left group"
                                      >
                                        <span className="mt-0.5 flex-shrink-0">
                                          {RESOURCE_ICONS[r.type] || <BookOpen className="w-4 h-4 text-gray-400" />}
                                        </span>
                                        <div className="min-w-0">
                                          <p className="text-xs font-medium text-white truncate group-hover:text-red-300 transition-colors">{r.title}</p>
                                          <p className="text-xs text-gray-500">{r.platform || r.channel || r.type}</p>
                                        </div>
                                        {r.free && <span className="text-xs text-emerald-400 ml-auto flex-shrink-0">Free</span>}
                                      </button>
                                    ))}
                                  </div>
                                </div>

                                {/* Project */}
                                {week.project && (
                                  <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-3">
                                    <p className="text-xs text-red-300 font-semibold mb-1">Mini Project</p>
                                    <p className="text-sm font-medium text-white">{week.project.title}</p>
                                    <p className="text-xs text-gray-400 mt-1">{week.project.description}</p>
                                    <div className="flex flex-wrap gap-1 mt-2">
                                      {week.project.tech_stack.map((t) => (
                                        <span key={t} className="skill-tag text-xs">{t}</span>
                                      ))}
                                    </div>
                                    <p className="text-xs text-gray-500 mt-2">{week.project.time_estimate}</p>
                                  </div>
                                )}

                                {/* Checkpoint */}
                                <div className="bg-orange-500/5 border border-orange-500/20 rounded-lg p-3">
                                  <p className="text-xs text-orange-300 font-semibold mb-1">Checkpoint</p>
                                  <p className="text-sm text-gray-300">{week.checkpoint}</p>
                                </div>

                                {/* Mark done */}
                                <button
                                  onClick={() => handleMarkDone(week)}
                                  disabled={isDone}
                                  className={`w-full py-2.5 rounded-lg font-semibold text-sm transition-all flex items-center justify-center gap-2
                                    ${isDone
                                      ? "bg-emerald-500/10 border border-emerald-500/25 text-emerald-400"
                                      : "btn-primary"
                                    }`}
                                >
                                  {isDone
                                    ? <><Check className="w-4 h-4" /> Completed!</>
                                    : <><Trophy className="w-4 h-4" /> Mark Week {week.week} as Done</>
                                  }
                                </button>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </motion.div>
                    );
                  })}
                </div>
              </motion.div>
            ))}

            {/* Portfolio Projects */}
            {roadmap.portfolio_projects.length > 0 && (
              <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
                <h2 className="text-xl font-bold text-white mb-4">Portfolio Projects</h2>
                <div className="grid md:grid-cols-2 gap-4">
                  {roadmap.portfolio_projects.map((p, i) => (
                    <GlassCard key={i} hover>
                      <div className="text-xs text-red-400 font-medium mb-1">{p.difficulty || "Intermediate"} · {p.time_estimate}</div>
                      <h3 className="font-bold text-white mb-2">{p.title}</h3>
                      <p className="text-sm text-gray-400 mb-3">{p.description}</p>
                      <div className="flex flex-wrap gap-1 mb-3">
                        {(p.tech_stack || []).map((t) => <span key={t} className="skill-tag text-xs">{t}</span>)}
                      </div>
                      {p.recruiter_appeal && (
                        <p className="text-xs text-emerald-400">{p.recruiter_appeal}</p>
                      )}
                    </GlassCard>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Communities */}
            <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
              <h2 className="text-xl font-bold text-white mb-4">Communities & Collaboration</h2>
              <div className="grid md:grid-cols-2 gap-4">
                <GlassCard>
                  <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                    <MessageCircle className="w-4 h-4 text-red-400" /> Discord Servers
                  </h3>
                  <div className="space-y-2">
                    {roadmap.networking.discord_servers.map((d) => (
                      <a key={d.name} href={d.url} target="_blank" rel="noopener noreferrer"
                        onClick={() => trackEvent("community_clicked", { name: d.name, type: "discord" })}
                        className="flex items-center justify-between p-2 rounded-lg hover:bg-red-500/5 transition-colors group">
                        <div>
                          <p className="text-sm font-medium text-white group-hover:text-red-300 transition-colors">{d.name}</p>
                          {d.members && <p className="text-xs text-gray-500">{d.members} members</p>}
                        </div>
                        <ExternalLink className="w-3 h-3 text-gray-500 group-hover:text-red-400 transition-colors" />
                      </a>
                    ))}
                  </div>
                </GlassCard>

                <GlassCard>
                  <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                    <Users className="w-4 h-4 text-orange-400" /> Code Together
                  </h3>
                  <div className="space-y-2">
                    {roadmap.networking.collab_platforms.map((p) => (
                      <a key={p.name} href={p.url} target="_blank" rel="noopener noreferrer"
                        className="flex items-start gap-2 p-2 rounded-lg hover:bg-white/5 transition-colors group">
                        <div>
                          <p className="text-sm font-medium text-white group-hover:text-orange-300 transition-colors">{p.name}</p>
                          <p className="text-xs text-gray-500">{p.desc}</p>
                        </div>
                        <ExternalLink className="w-3 h-3 text-gray-500 group-hover:text-orange-400 transition-colors mt-0.5 flex-shrink-0 ml-auto" />
                      </a>
                    ))}
                  </div>
                </GlassCard>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </main>
  );
}
