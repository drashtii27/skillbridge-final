"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import {
  Brain, ChevronRight, RotateCcw, Trophy, Clock, CheckCircle,
  XCircle, BookOpen, ExternalLink, AlertTriangle, Star,
} from "lucide-react";
import toast from "react-hot-toast";
import { useAppStore } from "@/store/useAppStore";
import { getInterviewQuestions, getQuizQuestions, submitQuiz } from "@/lib/api";
import { trackEvent } from "@/lib/posthog";
import GlassCard from "@/components/ui/GlassCard";
import type { InterviewQuestion, QuizQuestion } from "@/types";

type Mode = "select" | "flashcards" | "quiz" | "result";

// ─── Resource map ────────────────────────────────────────────────────────────
const SKILL_RESOURCES: Record<string, { label: string; url: string }[]> = {
  Python: [
    { label: "Python Official Docs", url: "https://docs.python.org/3/tutorial/" },
    { label: "CS50P – Harvard Python (free)", url: "https://cs50.harvard.edu/python/" },
    { label: "freeCodeCamp Python Tutorial", url: "https://www.youtube.com/watch?v=rfscVS0vtbw" },
  ],
  SQL: [
    { label: "SQLBolt – Interactive SQL", url: "https://sqlbolt.com/" },
    { label: "DataLemur SQL Practice", url: "https://datalemur.com/" },
    { label: "Mode Analytics SQL Tutorial", url: "https://mode.com/sql-tutorial/" },
  ],
  Spark: [
    { label: "Apache Spark Official Docs", url: "https://spark.apache.org/docs/latest/" },
    { label: "Databricks Spark Learning", url: "https://www.databricks.com/learn/training" },
    { label: "freeCodeCamp Spark Course", url: "https://www.youtube.com/watch?v=_C8kWso4ne4" },
  ],
  Kafka: [
    { label: "Confluent Kafka Tutorials", url: "https://developer.confluent.io/learn-kafka/" },
    { label: "Kafka Official Docs", url: "https://kafka.apache.org/documentation/" },
  ],
  Docker: [
    { label: "Docker Official Get Started", url: "https://docs.docker.com/get-started/" },
    { label: "TechWorld with Nana – Docker", url: "https://www.youtube.com/watch?v=3c-iBn73dDE" },
  ],
  "Machine Learning": [
    { label: "fast.ai Practical Deep Learning", url: "https://fast.ai/" },
    { label: "Google ML Crash Course", url: "https://developers.google.com/machine-learning/crash-course" },
  ],
  "System Design": [
    { label: "System Design Primer (GitHub)", url: "https://github.com/donnemartin/system-design-primer" },
    { label: "Grokking System Design (Educative)", url: "https://www.educative.io/courses/grokking-the-system-design-interview" },
  ],
  Algorithms: [
    { label: "NeetCode 150 (free)", url: "https://neetcode.io/" },
    { label: "LeetCode Blind 75", url: "https://leetcode.com/discuss/general-discussion/460599/blind-75-leetcode-questions" },
  ],
  "Data Engineering": [
    { label: "Fundamentals of Data Engineering (book)", url: "https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/" },
    { label: "DataTalks.Club DE Zoomcamp", url: "https://github.com/DataTalksClub/data-engineering-zoomcamp" },
  ],
  React: [
    { label: "React Official Tutorial", url: "https://react.dev/learn" },
    { label: "Full Stack Open (Helsinki)", url: "https://fullstackopen.com/" },
  ],
  default: [
    { label: "FreeCodeCamp YouTube", url: "https://www.youtube.com/@freecodecamp" },
    { label: "The Odin Project", url: "https://www.theodinproject.com/" },
  ],
};

function getResources(skillTag: string) {
  const key = Object.keys(SKILL_RESOURCES).find(
    (k) => skillTag.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(skillTag.toLowerCase())
  );
  return SKILL_RESOURCES[key ?? "default"];
}

const PASS_THRESHOLD = 80;

export default function InterviewPage() {
  const router = useRouter();
  const { roadmap, gapResult, setInterviewQuestions, interviewQuestions } = useAppStore();
  const [mode, setMode] = useState<Mode>("select");
  const [loading, setLoading] = useState(false);
  const [cardIdx, setCardIdx] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [quizQuestions, setQuizQuestions] = useState<QuizQuestion[]>([]);
  const [quizIdx, setQuizIdx] = useState(0);
  const [quizAnswers, setQuizAnswers] = useState<{ question_id: number; chosen_index: number; correct_index: number; skill_tag: string }[]>([]);
  const [quizResult, setQuizResult] = useState<{ score_pct: number; xp_earned: number; badges_unlocked: string[] } | null>(null);
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [timeLeft, setTimeLeft] = useState(30);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const role = gapResult?.role || roadmap?.role || "";
  const skills = gapResult?.gaps.map((g) => g.skill).slice(0, 8) || [];

  useEffect(() => {
    if (!role) router.replace("/");
  }, [role, router]);

  // Load flashcards
  useEffect(() => {
    if (mode === "flashcards" && interviewQuestions.length === 0) {
      setLoading(true);
      getInterviewQuestions(role, skills, 10)
        .then((r) => { setInterviewQuestions(r.data.questions); })
        .catch(() => toast.error("Failed to load questions"))
        .finally(() => setLoading(false));
    }
  }, [mode]);

  // Quiz timer
  useEffect(() => {
    if (mode !== "quiz" || selectedAnswer !== null || quizQuestions.length === 0) return;
    setTimeLeft(30);
    if (timerRef.current) clearInterval(timerRef.current);
    timerRef.current = setInterval(() => {
      setTimeLeft((t) => {
        if (t <= 1) {
          handleAnswer(-1);
          if (timerRef.current) clearInterval(timerRef.current);
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [mode, quizIdx, quizQuestions.length]);

  const startQuiz = async () => {
    setLoading(true);
    try {
      const skillStr = skills.slice(0, 6).join(",");
      const r = await getQuizQuestions(role, skillStr, 15);
      const qs: QuizQuestion[] = r.data.questions || [];
      if (qs.length === 0) throw new Error("empty");
      setQuizQuestions(qs);
      setQuizAnswers([]);
      setQuizIdx(0);
      setSelectedAnswer(null);
      setMode("quiz");
    } catch {
      toast.error("Using offline question bank — starting quiz…");
      // Fetch again — backend has fallback now
      try {
        const r2 = await getQuizQuestions(role, skills.slice(0, 4).join(","), 15);
        const qs2: QuizQuestion[] = r2.data.questions || [];
        setQuizQuestions(qs2);
        setQuizAnswers([]);
        setQuizIdx(0);
        setSelectedAnswer(null);
        setMode("quiz");
      } catch {
        toast.error("Could not load quiz. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = (idx: number) => {
    if (selectedAnswer !== null) return;
    if (timerRef.current) clearInterval(timerRef.current);
    setSelectedAnswer(idx);
    const q = quizQuestions[quizIdx];
    setQuizAnswers((prev) => [
      ...prev,
      { question_id: quizIdx, chosen_index: idx, correct_index: q.correct_index, skill_tag: q.skill_tag || "General" },
    ]);
    trackEvent("quiz_answer", { correct: idx === q.correct_index });
  };

  const nextQuestion = () => {
    if (quizIdx + 1 >= quizQuestions.length) {
      finishQuiz();
    } else {
      setQuizIdx((i) => i + 1);
      setSelectedAnswer(null);
    }
  };

  const finishQuiz = async () => {
    try {
      const r = await submitQuiz(quizAnswers, role);
      setQuizResult(r.data);
    } catch {
      const correct = quizAnswers.filter((a) => a.chosen_index === a.correct_index).length;
      setQuizResult({
        score_pct: Math.round((correct / quizAnswers.length) * 100),
        xp_earned: correct * 10,
        badges_unlocked: [],
      });
    }
    setMode("result");
  };

  // ─── Weak skill analysis ─────────────────────────────────────────────────
  const weakSkills = (() => {
    if (!quizResult || quizAnswers.length === 0) return [];
    const map: Record<string, { correct: number; total: number }> = {};
    quizAnswers.forEach((a) => {
      const tag = a.skill_tag;
      if (!map[tag]) map[tag] = { correct: 0, total: 0 };
      map[tag].total++;
      if (a.chosen_index === a.correct_index) map[tag].correct++;
    });
    return Object.entries(map)
      .filter(([, v]) => v.correct / v.total < 0.6)
      .sort((a, b) => (a[1].correct / a[1].total) - (b[1].correct / b[1].total))
      .map(([skill, v]) => ({ skill, pct: Math.round((v.correct / v.total) * 100), total: v.total }));
  })();

  const passed = (quizResult?.score_pct ?? 0) >= PASS_THRESHOLD;
  const difficultyColor = (d: string) =>
    d === "Easy" ? "text-emerald-400" : d === "Medium" ? "text-amber-400" : "text-red-400";

  if (!role) return null;

  return (
    <main className="min-h-screen gradient-mesh px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-black text-white">Interview Prep</h1>
            <p className="text-gray-400 text-sm mt-1">{role} · {skills.length} skills to cover</p>
          </div>
          <button onClick={() => router.back()} className="btn-ghost text-sm py-2 px-4">← Back</button>
        </motion.div>

        <AnimatePresence mode="wait">

          {/* ── Mode selector ── */}
          {mode === "select" && (
            <motion.div key="select" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {loading ? (
                <div className="flex flex-col items-center gap-4 py-20">
                  <div className="w-12 h-12 border-2 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
                  <p className="text-gray-400">Generating 15 questions with Qwen3 235B…</p>
                </div>
              ) : (
                <div className="grid gap-4">
                  <GlassCard hover onClick={() => setMode("flashcards")} className="group cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                        <Brain className="w-6 h-6 text-red-400" />
                      </div>
                      <div>
                        <h2 className="font-bold text-white group-hover:gradient-text transition-all">Flashcard Mode</h2>
                        <p className="text-sm text-gray-400">10 AI-generated Q&As. Flip to reveal answers.</p>
                      </div>
                      <ChevronRight className="ml-auto text-gray-500 group-hover:text-red-400 transition-colors group-hover:translate-x-1 duration-200" />
                    </div>
                  </GlassCard>

                  <GlassCard hover onClick={startQuiz} className="group cursor-pointer">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
                        <Clock className="w-6 h-6 text-amber-400" />
                      </div>
                      <div>
                        <h2 className="font-bold text-white group-hover:gradient-text transition-all">Timed Quiz</h2>
                        <p className="text-sm text-gray-400">15 MCQs · 30 seconds each · Pass threshold: 80% · Earn XP</p>
                      </div>
                      <ChevronRight className="ml-auto text-gray-500 group-hover:text-amber-400 transition-colors group-hover:translate-x-1 duration-200" />
                    </div>
                  </GlassCard>

                  {/* Pass threshold notice */}
                  <div className="glass rounded-xl p-4 border border-amber-500/15 flex items-start gap-3">
                    <Star className="w-4 h-4 text-amber-400 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-gray-400">
                      Score <span className="text-amber-400 font-bold">≥ 80%</span> to pass. Failed skills get personalised study resources with direct course links.
                    </p>
                  </div>
                </div>
              )}
            </motion.div>
          )}

          {/* ── Flashcards ── */}
          {mode === "flashcards" && (
            <motion.div key="flashcards" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {loading ? (
                <div className="flex flex-col items-center gap-4 py-20">
                  <div className="w-12 h-12 border-2 border-red-500/30 border-t-red-500 rounded-full animate-spin" />
                  <p className="text-gray-400">Generating interview questions with Qwen3 235B…</p>
                </div>
              ) : interviewQuestions.length > 0 ? (
                <div>
                  <div className="flex items-center justify-between mb-6">
                    <p className="text-sm text-gray-400">{cardIdx + 1} / {interviewQuestions.length}</p>
                    <div className="flex gap-2">
                      {interviewQuestions.map((_, i) => (
                        <div key={i} className={`w-2 h-2 rounded-full transition-colors ${i === cardIdx ? "bg-red-400" : i < cardIdx ? "bg-emerald-400" : "bg-white/10"}`} />
                      ))}
                    </div>
                    <span className={`text-xs font-medium ${difficultyColor(interviewQuestions[cardIdx]?.difficulty)}`}>
                      {interviewQuestions[cardIdx]?.difficulty}
                    </span>
                  </div>
                  <div className="relative h-64 cursor-pointer" onClick={() => setFlipped((f) => !f)} style={{ perspective: 1200 }}>
                    <motion.div className="w-full h-full" style={{ transformStyle: "preserve-3d" }}
                      animate={{ rotateY: flipped ? 180 : 0 }} transition={{ duration: 0.5, type: "spring", damping: 15 }}>
                      <div className="absolute inset-0 glass rounded-2xl p-6 flex flex-col justify-between" style={{ backfaceVisibility: "hidden" }}>
                        <span className="text-xs text-red-300 font-medium">{interviewQuestions[cardIdx]?.category}</span>
                        <p className="text-xl font-bold text-white text-center leading-relaxed">{interviewQuestions[cardIdx]?.question}</p>
                        <p className="text-xs text-gray-500 text-center">Click to reveal answer →</p>
                      </div>
                      <div className="absolute inset-0 glass rounded-2xl p-6 flex flex-col justify-between bg-red-950/20 border border-red-500/20" style={{ backfaceVisibility: "hidden", transform: "rotateY(180deg)" }}>
                        <span className="text-xs text-red-300 font-medium">Answer Outline</span>
                        <ul className="space-y-2 flex-1 flex flex-col justify-center">
                          {(interviewQuestions[cardIdx]?.answer_outline || []).map((a, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-200">
                              <span className="text-red-400 font-bold mt-0.5">•</span> {a}
                            </li>
                          ))}
                        </ul>
                        <div className="flex flex-wrap gap-1">
                          {(interviewQuestions[cardIdx]?.skills_tested || []).map((s) => (
                            <span key={s} className="skill-tag text-xs">{s}</span>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  </div>
                  <div className="flex gap-3 mt-6">
                    <button onClick={() => { setCardIdx((i) => Math.max(0, i - 1)); setFlipped(false); }} disabled={cardIdx === 0} className="btn-ghost flex-1 py-2.5 disabled:opacity-30">← Previous</button>
                    {cardIdx + 1 < interviewQuestions.length ? (
                      <button onClick={() => { setCardIdx((i) => i + 1); setFlipped(false); }} className="btn-primary flex-1 py-2.5">Next →</button>
                    ) : (
                      <button onClick={() => setMode("select")} className="btn-primary flex-1 py-2.5 flex items-center justify-center gap-2">
                        <RotateCcw className="w-4 h-4" /> Done
                      </button>
                    )}
                  </div>
                </div>
              ) : (
                <div className="text-center py-20 text-gray-500">No questions loaded. <button onClick={() => setMode("select")} className="text-red-400 underline">Go back</button></div>
              )}
            </motion.div>
          )}

          {/* ── Quiz ── */}
          {mode === "quiz" && (
            <motion.div key="quiz" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {quizQuestions.length === 0 ? (
                <div className="flex flex-col items-center gap-4 py-20">
                  <div className="w-12 h-12 border-2 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
                  <p className="text-gray-400">Loading questions…</p>
                </div>
              ) : (
                <>
                  {/* Progress + timer */}
                  <div className="flex items-center justify-between mb-4">
                    <p className="text-sm text-gray-400">Question {quizIdx + 1} / {quizQuestions.length}</p>
                    <div className={`flex items-center gap-2 px-3 py-1 rounded-full glass ${timeLeft <= 10 ? "border border-red-500/40" : "border border-white/10"}`}>
                      <Clock className={`w-4 h-4 ${timeLeft <= 10 ? "text-red-400" : "text-gray-400"}`} />
                      <span className={`text-sm font-bold ${timeLeft <= 10 ? "text-red-400" : "text-white"}`}>{timeLeft}s</span>
                    </div>
                  </div>

                  {/* Timer bar */}
                  <div className="w-full bg-white/5 rounded-full h-1 mb-2">
                    <div className="h-1 rounded-full bg-amber-500 transition-all duration-1000" style={{ width: `${(timeLeft / 30) * 100}%` }} />
                  </div>

                  {/* Question progress dots */}
                  <div className="flex gap-1 mb-6 flex-wrap">
                    {quizQuestions.map((_, i) => {
                      const answered = quizAnswers[i];
                      const correct = answered?.chosen_index === answered?.correct_index;
                      return (
                        <div key={i} className={`w-2 h-2 rounded-full transition-colors ${
                          i === quizIdx ? "bg-amber-400" :
                          answered ? (correct ? "bg-emerald-400" : "bg-red-400") : "bg-white/10"
                        }`} />
                      );
                    })}
                  </div>

                  <GlassCard className="mb-4">
                    <p className="text-xs text-amber-300 font-medium mb-2">{quizQuestions[quizIdx]?.skill_tag} · {quizQuestions[quizIdx]?.difficulty}</p>
                    <p className="text-lg font-semibold text-white leading-snug">{quizQuestions[quizIdx]?.question}</p>
                  </GlassCard>

                  <div className="grid gap-3">
                    {quizQuestions[quizIdx]?.options.map((opt, i) => {
                      const isCorrect = quizQuestions[quizIdx].correct_index === i;
                      const isSelected = selectedAnswer === i;
                      const revealed = selectedAnswer !== null;
                      return (
                        <motion.button key={i} whileHover={!revealed ? { scale: 1.01 } : {}}
                          onClick={() => handleAnswer(i)} disabled={revealed}
                          className={`w-full p-4 rounded-xl text-left text-sm font-medium transition-all flex items-center gap-3
                            ${!revealed ? "glass border border-white/10 hover:border-amber-500/40 text-white"
                              : isCorrect ? "bg-emerald-500/15 border border-emerald-500/40 text-emerald-300"
                              : isSelected ? "bg-red-500/15 border border-red-500/40 text-red-300"
                              : "glass border border-white/5 text-gray-500"}`}>
                          <span className="w-6 h-6 rounded-full border flex items-center justify-center text-xs flex-shrink-0 border-current">
                            {String.fromCharCode(65 + i)}
                          </span>
                          {opt}
                          {revealed && isCorrect && <CheckCircle className="ml-auto w-4 h-4 text-emerald-400 flex-shrink-0" />}
                          {revealed && isSelected && !isCorrect && <XCircle className="ml-auto w-4 h-4 text-red-400 flex-shrink-0" />}
                        </motion.button>
                      );
                    })}
                  </div>

                  {selectedAnswer !== null && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="mt-4">
                      {quizQuestions[quizIdx].explanation && (
                        <p className="text-sm text-gray-400 mb-3 glass rounded-xl p-3 border border-white/5">
                          💡 {quizQuestions[quizIdx].explanation}
                        </p>
                      )}
                      <button onClick={nextQuestion} className="w-full btn-primary py-3 flex items-center justify-center gap-2">
                        {quizIdx + 1 >= quizQuestions.length ? <><Trophy className="w-4 h-4" /> Finish Quiz</> : "Next Question →"}
                      </button>
                    </motion.div>
                  )}
                </>
              )}
            </motion.div>
          )}

          {/* ── Result ── */}
          {mode === "result" && quizResult && (
            <motion.div key="result" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>

              {/* Score card */}
              <GlassCard glow className={`text-center py-10 mb-6 border-2 ${passed ? "border-emerald-500/30" : "border-red-500/30"}`}>
                <div className={`text-7xl font-black mb-3 ${passed ? "text-emerald-400" : "text-red-400"}`}>
                  {quizResult.score_pct}%
                </div>
                <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-sm font-bold mb-4 ${passed ? "bg-emerald-500/15 text-emerald-300" : "bg-red-500/15 text-red-300"}`}>
                  {passed ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                  {passed ? "PASSED — Great job!" : `FAILED — Threshold is ${PASS_THRESHOLD}%`}
                </div>
                <p className="text-gray-400 text-sm mb-4">
                  {quizAnswers.filter(a => a.chosen_index === a.correct_index).length} / {quizAnswers.length} correct
                </p>
                <div className="flex items-center justify-center gap-2 text-amber-400">
                  <Trophy className="w-4 h-4" />
                  <span className="font-bold text-sm">+{quizResult.xp_earned} XP earned</span>
                </div>
              </GlassCard>

              {/* Skill breakdown */}
              <GlassCard className="mb-6">
                <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-amber-400" /> Score by Skill
                </h3>
                <div className="space-y-3">
                  {(() => {
                    const map: Record<string, { correct: number; total: number }> = {};
                    quizAnswers.forEach((a) => {
                      const tag = a.skill_tag;
                      if (!map[tag]) map[tag] = { correct: 0, total: 0 };
                      map[tag].total++;
                      if (a.chosen_index === a.correct_index) map[tag].correct++;
                    });
                    return Object.entries(map).sort((a, b) => b[1].correct / b[1].total - a[1].correct / a[1].total);
                  })().map(([skill, v]) => {
                    const pct = Math.round((v.correct / v.total) * 100);
                    const ok = pct >= 60;
                    return (
                      <div key={skill}>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm text-gray-300">{skill}</span>
                          <span className={`text-sm font-bold ${ok ? "text-emerald-400" : "text-red-400"}`}>{pct}% ({v.correct}/{v.total})</span>
                        </div>
                        <div className="w-full bg-white/5 rounded-full h-1.5">
                          <div className={`h-1.5 rounded-full transition-all ${ok ? "bg-emerald-500" : "bg-red-500"}`} style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </GlassCard>

              {/* Weak skills + resources */}
              {weakSkills.length > 0 && (
                <div className="mb-6">
                  <div className={`rounded-xl p-4 border mb-4 ${passed ? "border-amber-500/20 bg-amber-500/5" : "border-red-500/20 bg-red-500/5"}`}>
                    <p className={`text-sm font-semibold flex items-center gap-2 ${passed ? "text-amber-300" : "text-red-300"}`}>
                      <AlertTriangle className="w-4 h-4" />
                      {passed ? "Areas to strengthen before interviews:" : "Practice these skills to pass — you need ≥80%:"}
                    </p>
                  </div>

                  {weakSkills.map(({ skill, pct }) => (
                    <GlassCard key={skill} className="mb-3 border border-red-500/15">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <XCircle className="w-4 h-4 text-red-400" />
                          <span className="font-semibold text-white">{skill}</span>
                        </div>
                        <span className="text-red-400 font-bold text-sm">{pct}% correct</span>
                      </div>
                      <p className="text-xs text-gray-500 mb-3">Recommended study resources:</p>
                      <div className="space-y-2">
                        {getResources(skill).map((r) => (
                          <a key={r.url} href={r.url} target="_blank" rel="noopener noreferrer"
                            className="flex items-center gap-2 text-sm text-amber-400 hover:text-amber-300 transition-colors group">
                            <ExternalLink className="w-3.5 h-3.5 flex-shrink-0 group-hover:translate-x-0.5 transition-transform" />
                            {r.label}
                          </a>
                        ))}
                      </div>
                    </GlassCard>
                  ))}
                </div>
              )}

              {/* Actions */}
              <div className="flex gap-3">
                <button onClick={() => { setMode("select"); setQuizQuestions([]); setQuizAnswers([]); setQuizResult(null); }}
                  className="btn-primary flex-1 py-3 flex items-center justify-center gap-2">
                  <RotateCcw className="w-4 h-4" /> Retake Quiz
                </button>
                <button onClick={() => router.back()} className="btn-ghost flex-1 py-3">
                  Back to Dashboard
                </button>
              </div>

              {!passed && (
                <p className="text-center text-xs text-gray-500 mt-4">
                  Study the resources above, then retake to unlock the <span className="text-amber-400">Quiz Ace</span> badge (+150 XP).
                </p>
              )}
            </motion.div>
          )}

        </AnimatePresence>
      </div>
    </main>
  );
}
