"use client";

import { useState, useCallback, useEffect, useRef } from "react";
import { motion, AnimatePresence, useInView } from "framer-motion";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import {
  Upload, Compass, Sparkles, Brain, Target, Map, Mic, Briefcase,
  ChevronRight, X, ArrowLeft, CheckCircle2, RefreshCw, Plus, Zap,
  Star, Rocket, BarChart2, Cpu, Network, MessageSquare, Search,
} from "lucide-react";
import {
  uploadResume, suggestRoles, analyzeSkills, generateRoadmap,
  searchJobs, getRoles,
} from "@/lib/api";
import { useAppStore } from "@/store/useAppStore";
import { trackEvent } from "@/lib/posthog";
import ConstellationHero from "@/components/ui/ConstellationHero";
import CinematicHeroBg from "@/components/ui/CinematicHeroBg";

// ─── Types ───────────────────────────────────────────────────────────────────
type Scene = "home" | "resume" | "manual" | "generating";
type ResumePhase = "drop" | "role-pick";
type ManualStep = "role" | "skills" | "timeline";

interface RoleSuggestion {
  role: string; readiness_pct: number;
  matched_count: number; matched_skills: string[];
}

// ─── Journey steps ───────────────────────────────────────────────────────────
const JOURNEY_STEPS = [
  { n: "01", Icon: Upload,    title: "Upload Resume",  desc: "PDF auto-parsed. Mistral Small 24B extracts every skill instantly.",          color: "#ef4444", glow: "rgba(239,68,68,0.35)" },
  { n: "02", Icon: Brain,     title: "AI Skill Scan",  desc: "Nemotron 253B maps your profile against 30+ career tracks.",            color: "#f97316", glow: "rgba(249,115,22,0.35)" },
  { n: "03", Icon: BarChart2, title: "Gap Analysis",   desc: "DeepSeek R1 671B ranks skill gaps with chain-of-thought market reasoning.",   color: "#ef4444", glow: "rgba(239,68,68,0.3)" },
  { n: "04", Icon: Map,       title: "Roadmap Built",  desc: "Week-by-week plan with real resources, curated by Nemotron 253B.",      color: "#f97316", glow: "rgba(249,115,22,0.3)" },
  { n: "05", Icon: Mic,       title: "Interview Prep", desc: "Qwen3 235B generates role-specific questions with detailed answer guides.",   color: "#ef4444", glow: "rgba(239,68,68,0.25)" },
  { n: "06", Icon: Briefcase, title: "Get Hired",      desc: "Live jobs from Adzuna · Remotive · Jobicy · The Muse, refreshed daily.",      color: "#f97316", glow: "rgba(249,115,22,0.25)" },
];

// ─── 4-Model showcase ─────────────────────────────────────────────────────────
const AI_MODELS = [
  { icon: <Cpu className="w-4 h-4" />, name: "Nemotron 253B", task: "Roadmap Generation", tag: "NVIDIA · Main Model", color: "text-red-400", border: "border-red-500/25", bg: "bg-red-500/8" },
  { icon: <Search className="w-4 h-4" />, name: "Mistral Small 24B", task: "Skill Extraction", tag: "Mistral · Fast NER", color: "text-orange-400", border: "border-orange-500/25", bg: "bg-orange-500/8" },
  { icon: <Network className="w-4 h-4" />, name: "DeepSeek R1 671B", task: "Market Insight & RAG", tag: "DeepSeek · Reasoning", color: "text-amber-400", border: "border-amber-500/25", bg: "bg-amber-500/8" },
  { icon: <MessageSquare className="w-4 h-4" />, name: "Qwen3 235B", task: "Interview & Quiz", tag: "Alibaba · Latest", color: "text-rose-300", border: "border-rose-500/25", bg: "bg-rose-500/8" },
];

const SKILL_SUGGESTIONS: Record<string, string[]> = {
  "Machine Learning Engineer":     ["Python", "PyTorch", "TensorFlow", "scikit-learn", "NumPy", "Pandas", "SQL", "Git", "Docker", "MLflow"],
  "Data Scientist":                ["Python", "SQL", "Pandas", "NumPy", "Statistics", "R", "Matplotlib", "Tableau", "scikit-learn"],
  "Software Engineer (Frontend)":  ["JavaScript", "TypeScript", "React", "CSS", "HTML", "Git", "Next.js", "Webpack", "Jest"],
  "Software Engineer (Backend)":   ["Python", "SQL", "REST APIs", "Git", "Docker", "PostgreSQL", "Redis", "FastAPI"],
  "Full Stack Developer":          ["JavaScript", "React", "Node.js", "SQL", "Git", "TypeScript", "Docker", "PostgreSQL"],
  "DevOps / Cloud Engineer":       ["Linux", "Docker", "Kubernetes", "Terraform", "AWS", "Bash", "CI/CD", "Helm"],
  "Data Engineer":                 ["Python", "SQL", "Spark", "Airflow", "dbt", "Kafka", "BigQuery", "Snowflake"],
  "Cybersecurity Engineer":        ["Linux", "Python", "Network Security", "SIEM", "Penetration Testing", "OWASP"],
  "UI/UX Designer":                ["Figma", "Prototyping", "User Research", "Design Systems", "Framer", "Accessibility"],
  "Product Manager":               ["Agile", "User Research", "Data Analysis", "Roadmapping", "SQL", "Figma", "OKRs"],
};

const MONTHS = [1, 2, 3, 4, 6];

const GEN_STEPS = [
  "Mistral Small 24B extracting your skills…",
  "Nemotron 253B mapping skill connections…",
  "DeepSeek R1 analyzing 2026 market data…",
  "Nemotron 253B building your roadmap…",
  "Qwen3 235B preparing interview questions…",
  "Pulling live jobs from 4 boards…",
];

// ─── Animated counter ────────────────────────────────────────────────────────
function AnimatedCounter({ end, suffix, label, icon }: { end: number; suffix: string; label: string; icon: string }) {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true });
  const [val, setVal] = useState(0);

  useEffect(() => {
    if (!inView) return;
    const dur = 1800, fps = 60;
    const frames = dur / (1000 / fps);
    let f = 0;
    const id = setInterval(() => {
      f++;
      setVal(Math.min(Math.round(end * (f / frames)), end));
      if (f >= frames) clearInterval(id);
    }, 1000 / fps);
    return () => clearInterval(id);
  }, [inView, end]);

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="glass rounded-xl p-6 text-center relative overflow-hidden group border border-white/5 hover:border-red-500/20 transition-colors duration-300"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-red-500/0 to-orange-500/0 group-hover:from-red-500/4 group-hover:to-orange-500/4 transition-all duration-500" />
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-4xl font-black gradient-text tabular-nums">
        {val.toLocaleString()}{suffix}
      </div>
      <div className="text-xs text-gray-400 mt-1 font-medium">{label}</div>
    </motion.div>
  );
}

// ─── Gateway card ─────────────────────────────────────────────────────────────
function GatewayCard({
  icon, title, subtitle, badge, features, onClick,
}: {
  icon: React.ReactNode; title: string; subtitle: string;
  badge?: string; features: string[]; onClick: () => void;
}) {
  return (
    <motion.button
      whileHover={{ y: -4, scale: 1.01 }}
      whileTap={{ scale: 0.99 }}
      onClick={onClick}
      className="group relative w-full glass rounded-2xl p-7 text-left overflow-hidden border border-white/8 hover:border-red-500/30 transition-all duration-300 hover:shadow-[0_0_40px_rgba(239,68,68,0.12)]"
    >
      {/* Animated border sweep on hover */}
      <div
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
        style={{
          background: "linear-gradient(135deg, rgba(239,68,68,0.06), transparent 60%, rgba(249,115,22,0.04))",
        }}
      />
      {badge && (
        <span className="absolute top-4 right-4 text-[10px] font-bold px-2.5 py-1 rounded-full bg-red-500/15 border border-red-500/30 text-red-300 uppercase tracking-wider">
          {badge}
        </span>
      )}
      <div className="w-12 h-12 rounded-xl bg-red-500/10 border border-red-500/25 flex items-center justify-center text-red-400 mb-5">
        {icon}
      </div>
      <h3 className="text-xl font-black text-white mb-1">{title}</h3>
      <p className="text-sm text-gray-400 mb-5">{subtitle}</p>
      <ul className="space-y-2">
        {features.map((f) => (
          <li key={f} className="flex items-center gap-2 text-xs text-gray-500">
            <CheckCircle2 className="w-3.5 h-3.5 text-red-500/60 flex-shrink-0" />
            {f}
          </li>
        ))}
      </ul>
      <div className="mt-6 flex items-center gap-1.5 text-sm font-semibold text-red-400 group-hover:gap-2.5 transition-all">
        Get started <ChevronRight className="w-4 h-4" />
      </div>
    </motion.button>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────
export default function LandingPage() {
  const router = useRouter();
  const { setResumeSkills, setGapResult, setRoadmap, setJobs, setTargetRole, setTargetMonths } = useAppStore();

  const [scene, setScene] = useState<Scene>("home");
  const [resumePhase, setResumePhase] = useState<ResumePhase>("drop");
  const [manualStep, setManualStep] = useState<ManualStep>("role");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [genStep, setGenStep] = useState(0);
  const [suggestions, setSuggestions] = useState<RoleSuggestion[] | null>(null);
  const [faqOpen, setFaqOpen] = useState<number | null>(null);
  const [extractedSkills, setExtractedSkills] = useState<string[]>([]);
  const [allRoles, setAllRoles] = useState<string[]>([]);
  const [showAllRoles, setShowAllRoles] = useState(false);
  const [selectedRole, setSelectedRole] = useState("");
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedMonths, setSelectedMonths] = useState(3);
  const [skillInput, setSkillInput] = useState("");
  const [roles, setRoles] = useState<string[]>([]);

  useEffect(() => {
    getRoles().then((r) => setRoles(r.data.roles || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (scene !== "generating") return;
    const id = setInterval(() => setGenStep((s) => (s + 1) % GEN_STEPS.length), 1800);
    return () => clearInterval(id);
  }, [scene]);

  const onDrop = useCallback(async (files: File[]) => {
    const file = files[0];
    if (!file) return;
    setScene("resume"); setResumePhase("drop");
    setLoading(true); setProgress(10); setSuggestions(null);
    try {
      trackEvent("resume_drop");
      const { data: up } = await uploadResume(file);
      setProgress(55);
      setExtractedSkills(up.extracted_skills);
      setResumeSkills(up.extracted_skills);
      const [sr, rr] = await Promise.all([suggestRoles(up.extracted_skills), getRoles()]);
      setProgress(95);
      setSuggestions(sr.data.suggestions);
      setAllRoles(rr.data.roles);
      setLoading(false);
      setResumePhase("role-pick");
      trackEvent("resume_uploaded", { skills_found: up.extracted_skills.length });
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      toast.error(msg || "Upload failed — check that the backend is running on port 8000.");
      setLoading(false);
      setProgress(0);
      // Stay on the resume scene so the user can retry
    }
  }, [setResumeSkills]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { "application/pdf": [".pdf"] }, maxFiles: 1, disabled: loading,
  });

  const handleRoleConfirmed = useCallback(async (role: string) => {
    setTargetRole(role); setTargetMonths(3); setScene("generating"); setProgress(0);
    try {
      const { data: gap } = await analyzeSkills(role, extractedSkills, 3);
      setGapResult(gap); setProgress(35);
      const missing = gap.gaps.map((g: { skill: string }) => g.skill).slice(0, 8);
      const { data: rm } = await generateRoadmap({ role, user_skills: extractedSkills, missing_skills: missing, readiness_pct: gap.readiness_pct, months: 3 });
      setRoadmap(rm); setProgress(75);
      const { data: jd } = await searchJobs(role);
      setJobs(jd.jobs); setProgress(100);
      trackEvent("resume_flow_complete", { role, skills: extractedSkills.length });
      setTimeout(() => router.push("/dashboard"), 600);
    } catch {
      toast.error("Something went wrong. Check if the backend is running.");
      setScene("resume"); setResumePhase("role-pick");
    }
  }, [extractedSkills, router, setTargetRole, setTargetMonths, setGapResult, setRoadmap, setJobs]);

  const handleManualContinue = useCallback(async () => {
    if (!selectedRole) return;
    setTargetRole(selectedRole); setTargetMonths(selectedMonths);
    setResumeSkills(selectedSkills); setScene("generating"); setProgress(0);
    try {
      const { data: gap } = await analyzeSkills(selectedRole, selectedSkills, selectedMonths);
      setGapResult(gap); setProgress(35);
      const missing = gap.gaps.map((g: { skill: string }) => g.skill).slice(0, 8);
      const { data: rm } = await generateRoadmap({ role: selectedRole, user_skills: selectedSkills, missing_skills: missing, readiness_pct: gap.readiness_pct, months: selectedMonths });
      setRoadmap(rm); setProgress(75);
      const { data: jd } = await searchJobs(selectedRole);
      setJobs(jd.jobs); setProgress(100);
      trackEvent("manual_flow_complete", { role: selectedRole });
      setTimeout(() => router.push("/dashboard"), 600);
    } catch {
      toast.error("Something went wrong. Check if the backend is running.");
      setScene("manual");
    }
  }, [selectedRole, selectedSkills, selectedMonths, router, setTargetRole, setTargetMonths, setResumeSkills, setGapResult, setRoadmap, setJobs]);

  const addSkill = (s: string) => {
    const t = s.trim();
    if (t && !selectedSkills.includes(t)) setSelectedSkills((p) => [...p, t]);
    setSkillInput("");
  };

  const fade = {
    initial: { opacity: 0, y: 24, scale: 0.98 },
    animate: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] } },
    exit:    { opacity: 0, y: -14, scale: 0.97, transition: { duration: 0.28 } },
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] overflow-x-hidden">

      {/* ══ Cinematic animated background (always visible on home) ══ */}
      {scene === "home" && <CinematicHeroBg />}

      <AnimatePresence mode="wait">

        {/* ══════════════ HOME ══════════════ */}
        {scene === "home" && (
          <motion.div key="home" variants={fade} initial="initial" animate="animate" exit="exit">

            {/* Navbar */}
            <nav className="fixed top-0 left-0 right-0 z-40 px-6 py-4">
              <div className="max-w-7xl mx-auto flex items-center justify-between glass-dark rounded-2xl px-6 py-3 border border-white/6">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-xl bg-red-500/15 border border-red-500/40 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-red-400" />
                  </div>
                  <span className="font-black text-white text-lg tracking-tight">
                    SkillBridge<span className="gradient-text">AI</span>
                  </span>
                </div>
                <div className="hidden md:flex items-center gap-6 text-sm text-gray-400">
                  <a href="/analytics" className="hover:text-white transition-colors flex items-center gap-1.5">
                    <BarChart2 className="w-3.5 h-3.5" /> Analytics
                  </a>
                  <a href="/dashboard/badges" className="hover:text-white transition-colors">Badges</a>
                  <a href="/login" className="hover:text-white transition-colors">Login</a>
                  <a href="/register" className="btn-primary text-xs px-4 py-2 rounded-lg">Get Started</a>
                </div>
              </div>
            </nav>

            {/* Hero */}
            <section className="relative min-h-screen flex flex-col items-center justify-center px-4 pt-28 pb-16 overflow-hidden">

              {/* Subtle ambient blobs behind the neural network */}
              <div className="absolute top-1/3 left-1/4 w-[600px] h-[600px] rounded-full opacity-4 blur-[160px] pointer-events-none"
                style={{ background: "radial-gradient(circle, rgba(239,68,68,0.15), transparent)" }} />
              <div className="absolute bottom-1/3 right-1/4 w-[400px] h-[400px] rounded-full opacity-4 blur-[120px] pointer-events-none"
                style={{ background: "radial-gradient(circle, rgba(249,115,22,0.12), transparent)" }} />

              <div className="relative z-10 max-w-5xl w-full mx-auto text-center">

                {/* Headline */}
                <motion.h1
                  initial={{ opacity: 0, y: 32 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15, duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
                  className="text-6xl sm:text-7xl md:text-[86px] font-black leading-[0.9] mb-6 tracking-tight"
                >
                  <span className="gradient-text-white block">Your Career,</span>
                  <span className="gradient-text block">AI-Mapped.</span>
                </motion.h1>

                <motion.p
                  initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.28, duration: 0.6 }}
                  className="text-lg md:text-xl text-gray-400 max-w-2xl mx-auto mb-3 leading-relaxed"
                >
                  Upload your resume and get a personalized skill gap analysis, week-by-week roadmap,
                  interview prep, and live jobs — powered by 4 industry-leading AI models.
                </motion.p>

                <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.42 }}
                  className="text-sm text-gray-600 mb-10">
                  Roadmap in under 60 seconds · 30+ career tracks · No account required to start
                </motion.p>

                {/* Constellation path */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.92 }} animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.38, duration: 0.8, ease: "easeOut" }}
                  className="mb-12"
                >
                  <ConstellationHero />
                </motion.div>

                {/* Gateway Cards */}
                <motion.div
                  initial={{ opacity: 0, y: 28 }} animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5, duration: 0.55 }}
                  className="grid md:grid-cols-2 gap-5 max-w-3xl mx-auto"
                >
                  <GatewayCard
                    icon={<Upload className="w-6 h-6" />}
                    title="Upload Resume"
                    subtitle="Let AI decode your path"
                    badge="Recommended"
                    features={["PDF parsed by Mistral Small 24B in seconds", "Nemotron 253B builds roadmap", "Roles ranked by readiness score"]}
                    onClick={() => setScene("resume")}
                  />
                  <GatewayCard
                    icon={<Compass className="w-6 h-6" />}
                    title="Build Manually"
                    subtitle="Choose your own destination"
                    features={["Pick from 30+ career tracks", "Add current skills interactively", "Set your timeline"]}
                    onClick={() => { setScene("manual"); setManualStep("role"); }}
                  />
                </motion.div>
              </div>
            </section>

            {/* 4-Model Architecture Section */}
            <section className="py-16 px-4 relative z-10 bg-[#0a0a0a]">
              <div className="max-w-5xl mx-auto">
                <motion.div
                  initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }} className="text-center mb-10"
                >
                  <p className="text-xs text-red-400 font-semibold uppercase tracking-widest mb-3">4-Model Architecture</p>
                  <h2 className="text-3xl md:text-4xl font-black text-white mb-3">
                    Right model, <span className="gradient-text">right task</span>
                  </h2>
                  <p className="text-gray-400 text-sm max-w-xl mx-auto">
                    Each AI model is chosen for what it does best — no one-size-fits-all approach.
                  </p>
                </motion.div>
                <div className="grid md:grid-cols-4 gap-4">
                  {AI_MODELS.map((m, i) => (
                    <motion.div key={m.name}
                      initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }} transition={{ delay: i * 0.07 }}
                      className={`glass rounded-xl p-5 border ${m.border} ${m.bg} text-center`}
                    >
                      <div className={`w-9 h-9 rounded-lg flex items-center justify-center mx-auto mb-3 bg-white/5 ${m.color}`}>
                        {m.icon}
                      </div>
                      <p className={`text-xs font-bold ${m.color} mb-0.5`}>{m.task}</p>
                      <p className="text-sm font-semibold text-white mb-1">{m.name}</p>
                      <p className="text-[11px] text-gray-500">{m.tag}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* Stats */}
            <section className="py-12 px-4">
              <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4">
                <AnimatedCounter end={10000} suffix="+" label="Careers Launched"       icon="🚀" />
                <AnimatedCounter end={30}    suffix="+"  label="Career Tracks"          icon="🗺️" />
                <AnimatedCounter end={4}     suffix=""   label="Specialized AI Models"  icon="🤖" />
                <AnimatedCounter end={60}    suffix="s"  label="Roadmap Generated"      icon="⚡" />
              </div>
            </section>

            {/* Journey Steps */}
            <section className="py-20 px-4 relative z-10 bg-[#0a0a0a] overflow-hidden">
              <div className="absolute inset-0 pointer-events-none"
                style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(239,68,68,0.05) 0%, transparent 60%)" }} />
              <div className="max-w-6xl mx-auto">
                <motion.div initial={{ opacity: 0, y: 24 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-14">
                  <p className="text-xs text-red-400 font-semibold uppercase tracking-widest mb-3">The Journey</p>
                  <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
                    How the <span className="gradient-text">path</span> unfolds
                  </h2>
                  <p className="text-gray-400 text-base max-w-xl mx-auto">
                    Six milestones, powered by four AI models, one continuous journey from where you are to where you want to be.
                  </p>
                </motion.div>

                <div className="hidden md:flex items-center justify-between mb-0 relative px-8">
                  <div className="absolute left-8 right-8 top-1/2 -translate-y-1/2 milestone-line rounded-full" />
                  {JOURNEY_STEPS.map((step, i) => (
                    <motion.div key={step.n}
                      initial={{ opacity: 0, scale: 0 }} whileInView={{ opacity: 1, scale: 1 }}
                      viewport={{ once: true }} transition={{ delay: i * 0.09, type: "spring", stiffness: 200 }}
                      className="relative z-10 w-10 h-10 rounded-full flex items-center justify-center text-xs font-black border-2"
                      style={{ background: `${step.color}15`, borderColor: step.color, color: step.color, boxShadow: `0 0 18px ${step.glow}` }}
                    >{step.n}</motion.div>
                  ))}
                </div>

                <div className="grid md:grid-cols-3 lg:grid-cols-6 gap-4 mt-6">
                  {JOURNEY_STEPS.map((step, i) => (
                    <motion.div key={step.n}
                      initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }} transition={{ delay: i * 0.07 }}
                      whileHover={{ y: -6 }}
                      className="glass rounded-xl p-5 text-center border border-white/5 hover:border-red-500/20 transition-all duration-300 cursor-default group"
                      onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.boxShadow = `0 0 28px ${step.glow}`; }}
                      onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.boxShadow = ""; }}
                    >
                      <div className="w-10 h-10 rounded-xl mx-auto mb-3 flex items-center justify-center"
                        style={{ background: `${step.color}12`, border: `1px solid ${step.color}35` }}>
                        <step.Icon className="w-5 h-5" style={{ color: step.color }} />
                      </div>
                      <p className="font-bold text-white text-sm mb-1.5">{step.title}</p>
                      <p className="text-xs text-gray-500 leading-relaxed">{step.desc}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* CTA Footer */}
            <section className="py-24 px-4 relative overflow-hidden">
              <div className="absolute inset-0 pointer-events-none"
                style={{ background: "radial-gradient(ellipse at 50% 100%, rgba(239,68,68,0.08) 0%, transparent 60%)" }} />
              <motion.div
                initial={{ opacity: 0, y: 28 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                className="max-w-3xl mx-auto text-center"
              >
                <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
                  Your next role starts<br />
                  <span className="gradient-text">with one smart step.</span>
                </h2>
                <p className="text-gray-400 text-lg mb-10">
                  Build momentum, not confusion. See the shortest path from where you are to where you want to be.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button onClick={() => setScene("resume")} className="btn-cta flex items-center justify-center gap-2">
                    <Upload className="w-5 h-5" /> Begin Your Journey
                  </button>
                  <button onClick={() => { setScene("manual"); setManualStep("role"); }} className="btn-ghost flex items-center justify-center gap-2">
                    <Compass className="w-5 h-5" /> Build Manually
                  </button>
                </div>
              </motion.div>
            </section>

            {/* ── Why It Helps ── */}
            <section className="py-20 px-4 border-t border-white/5 relative z-10 bg-[#0a0a0a]">
              <div className="max-w-5xl mx-auto">
                <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-14">
                  <p className="text-xs text-red-400 font-semibold uppercase tracking-widest mb-3">Why It Matters</p>
                  <h2 className="text-3xl md:text-4xl font-black text-white mb-4">The career gap is real. <span className="gradient-text">AI closes it.</span></h2>
                  <p className="text-gray-500 max-w-xl mx-auto">Most people spend months guessing what skills they need. SkillBridge AI gives you a precision map in 60 seconds.</p>
                </motion.div>
                {/* Stats row */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
                  {[
                    { val: "60s", label: "Roadmap generated", color: "text-red-400" },
                    { val: "30+", label: "Career tracks covered", color: "text-orange-400" },
                    { val: "293", label: "Skills in taxonomy", color: "text-amber-400" },
                    { val: "4", label: "Specialized AI models", color: "text-emerald-400" },
                  ].map(({ val, label, color }) => (
                    <motion.div key={label} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                      className="glass-dark rounded-2xl p-6 text-center border border-white/5">
                      <div className={`text-4xl font-black mb-2 ${color}`}>{val}</div>
                      <div className="text-xs text-gray-500">{label}</div>
                    </motion.div>
                  ))}
                </div>
                {/* Benefit cards */}
                <div className="grid md:grid-cols-3 gap-6">
                  {[
                    { icon: "🎯", title: "Precision Skill Gap", body: "Upload your resume and instantly see exactly which skills are holding you back from your dream role — not a generic list, but a diff against 35 real role benchmarks." },
                    { icon: "🗺️", title: "Week-by-Week Roadmap", body: "NVIDIA Nemotron 253B (LoRA fine-tuned) builds a 12-week action plan with real courses, projects, and resources — not vague advice." },
                    { icon: "💼", title: "Live Job Market Data", body: "4 live job APIs (Remotive, Jobicy, The Muse, Adzuna) surface real openings that match your skill level right now, not cached listings." },
                  ].map(({ icon, title, body }) => (
                    <motion.div key={title} initial={{ opacity: 0, y: 16 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                      className="glass-dark rounded-2xl p-7 border border-white/5 hover:border-red-500/20 transition-colors">
                      <div className="text-3xl mb-4">{icon}</div>
                      <h3 className="text-white font-bold text-lg mb-2">{title}</h3>
                      <p className="text-gray-500 text-sm leading-relaxed">{body}</p>
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            {/* ── FAQ ── */}
            <section className="py-20 px-4 border-t border-white/5 relative z-10 bg-[#0a0a0a]">
              <div className="max-w-2xl mx-auto">
                <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-center mb-12">
                  <p className="text-xs text-red-400 font-semibold uppercase tracking-widest mb-3">FAQ</p>
                  <h2 className="text-3xl md:text-4xl font-black text-white">Frequently asked questions</h2>
                </motion.div>
                <div className="space-y-3">
                  {[
                    { q: "Do I need a resume to use SkillBridge AI?", a: "No. You can choose \"Build Manually\" to select your role and type in your skills directly. Resume upload is optional — it just makes skill extraction instant and automatic." },
                    { q: "Which AI models power this?", a: "4 specialized models: NVIDIA Nemotron 253B for roadmap generation (LoRA fine-tuned), Mistral Small 24B for skill extraction, DeepSeek R1 671B for market insights, and Qwen3 235B for interview & quiz questions." },
                    { q: "How accurate is the skill gap analysis?", a: "Skill gaps are compared against 293 curated skills across 35 role benchmarks built from real job postings. GLiNER NER + Mistral 24B extract skills from your resume with high precision." },
                    { q: "Is my resume data stored?", a: "Your resume PDF is only processed in-memory and never stored. The extracted skills and generated roadmap are saved to your account if you register, but the raw PDF is discarded immediately." },
                    { q: "How long does it take to get a roadmap?", a: "Typically under 60 seconds end-to-end: ~5s for skill extraction, ~40s for roadmap generation via Nemotron 253B, ~10s for job fetching and RAG context injection." },
                    { q: "Is it free?", a: "Yes — fully free. All AI models run on OpenRouter's free tier. No credit card required. The app is open to use without even creating an account." },
                  ].map(({ q, a }, i) => (
                    <motion.div key={i} initial={{ opacity: 0, y: 10 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
                      className="glass-dark rounded-2xl border border-white/5 overflow-hidden">
                      <button onClick={() => setFaqOpen(faqOpen === i ? null : i)}
                        className="w-full flex items-center justify-between px-6 py-5 text-left text-white font-medium hover:bg-white/3 transition-colors">
                        <span>{q}</span>
                        <span className={`text-red-400 text-xl transition-transform duration-300 ${faqOpen === i ? "rotate-45" : ""}`}>+</span>
                      </button>
                      {faqOpen === i && (
                        <div className="px-6 pb-5 text-gray-400 text-sm leading-relaxed border-t border-white/5 pt-4">{a}</div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </div>
            </section>

            <footer className="py-8 px-4 border-t border-white/5 relative z-10 bg-[#0a0a0a]">
              <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-gray-600">
                <span className="flex items-center gap-2">
                  <Sparkles className="w-3 h-3 text-red-500" />
                  SkillBridge AI — 4 Models: Nemotron 253B · Mistral 24B · DeepSeek R1 · Qwen3 235B
                </span>
                <div className="flex gap-6">
                  <a href="/analytics" className="hover:text-gray-400 transition-colors">Model Analytics</a>
                  <a href="/dashboard" className="hover:text-gray-400 transition-colors">Dashboard</a>
                </div>
              </div>
            </footer>
          </motion.div>
        )}

        {/* ══════════════ RESUME SCENE ══════════════ */}
        {scene === "resume" && (
          <motion.div key="resume" variants={fade} initial="initial" animate="animate" exit="exit"
            className="fixed inset-0 z-50 bg-[#0a0a0a] overflow-y-auto">
            <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">

              <div className="fixed top-0 left-0 right-0 z-10 px-6 py-4 flex items-center justify-between glass-dark border-b border-white/5">
                <div className="flex items-center gap-2 text-sm">
                  <Sparkles className="w-4 h-4 text-red-400" />
                  <span className="font-bold text-white">SkillBridge<span className="gradient-text">AI</span></span>
                </div>
                <div className="flex items-center gap-3">
                  <div className="hidden sm:flex items-center gap-1.5">
                    {["Upload Resume", "Choose Role"].map((s, i) => (
                      <div key={s} className="flex items-center gap-1.5">
                        <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${
                          (resumePhase === "drop" && i === 0) || (resumePhase === "role-pick" && i === 1)
                            ? "bg-red-500 text-white shadow-[0_0_12px_rgba(239,68,68,0.6)]"
                            : resumePhase === "role-pick" && i === 0 ? "bg-emerald-500 text-white"
                            : "bg-white/5 text-gray-500"
                        }`}>
                          {resumePhase === "role-pick" && i === 0 ? <CheckCircle2 className="w-3.5 h-3.5" /> : i + 1}
                        </div>
                        <span className={`text-xs ${(resumePhase === "drop" && i === 0) || (resumePhase === "role-pick" && i === 1) ? "text-white" : "text-gray-600"}`}>{s}</span>
                        {i === 0 && <div className="w-8 h-px bg-white/10" />}
                      </div>
                    ))}
                  </div>
                  <button onClick={() => setScene("home")} className="p-2 rounded-xl hover:bg-white/5 text-gray-500 hover:text-white transition-colors">
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="mt-20 w-full max-w-2xl">

                {resumePhase === "drop" && (
                  <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
                    <div className="text-center mb-8">
                      <h1 className="text-3xl md:text-4xl font-black text-white mb-3">
                        Drop your <span className="gradient-text">resume</span>
                      </h1>
                      <p className="text-gray-400 text-sm">Mistral Small 24B extracts your skills · Nemotron 253B builds your roadmap</p>
                    </div>

                    <div {...getRootProps()}
                      className={`relative rounded-2xl border-2 border-dashed p-16 text-center transition-all duration-300 cursor-pointer overflow-hidden
                        ${isDragActive
                          ? "border-red-400 bg-red-500/8 shadow-[0_0_60px_rgba(239,68,68,0.2)]"
                          : "border-white/10 hover:border-red-500/35 hover:bg-red-500/4 hover:shadow-[0_0_40px_rgba(239,68,68,0.1)]"
                        }`}
                    >
                      <input {...getInputProps()} />
                      {loading ? (
                        <div className="space-y-5">
                          <div className="relative w-20 h-20 mx-auto">
                            <div className="w-20 h-20 rounded-full border-2 border-red-500/20 animate-spin border-t-red-500" />
                            <div className="w-20 h-20 rounded-full border-2 border-orange-500/10 animate-spin border-t-orange-400 absolute inset-0" style={{ animationDuration: "1.5s", animationDirection: "reverse" }} />
                            <Brain className="absolute inset-0 m-auto w-8 h-8 text-red-400 animate-pulse" />
                          </div>
                          <div>
                            <p className="text-white font-semibold text-lg mb-1">
                              {progress < 55 ? "Mistral Small 24B parsing your resume…" : "Scoring role matches…"}
                            </p>
                            <p className="text-gray-500 text-sm">AI is reading every line</p>
                          </div>
                          <div className="max-w-xs mx-auto">
                            <div className="w-full bg-white/5 rounded-full h-1.5">
                              <div className="h-1.5 rounded-full progress-bar transition-all duration-700" style={{ width: `${progress}%` }} />
                            </div>
                            <p className="text-xs text-gray-600 mt-2">{progress}%</p>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <motion.div animate={{ y: [0, -8, 0] }} transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut" }}
                            className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-red-500/8 border border-red-500/25 flex items-center justify-center">
                            <Upload className="w-8 h-8 text-red-400" />
                          </motion.div>
                          <p className="text-xl font-bold text-white mb-2">
                            {isDragActive ? "Release to unleash AI" : "Drag & drop your resume here"}
                          </p>
                          <p className="text-gray-500 text-sm mb-6">or click to browse — PDF only · Max 10 MB</p>
                          <div className="flex items-center justify-center gap-6 text-xs text-gray-600">
                            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Skills extracted</span>
                            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Roles matched</span>
                            <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" /> Roadmap built</span>
                          </div>
                        </div>
                      )}
                    </div>

                    <p className="text-center mt-5 text-sm text-gray-600">
                      No resume?{" "}
                      <button onClick={() => { setScene("manual"); setManualStep("role"); }}
                        className="text-red-400 hover:text-red-300 font-medium transition-colors">
                        Build manually →
                      </button>
                    </p>
                  </motion.div>
                )}

                {resumePhase === "role-pick" && (
                  <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
                    <div className="text-center mb-8">
                      <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold mb-4">
                        <Zap className="w-3.5 h-3.5" />
                        {extractedSkills.length} skills detected · Mistral Small 24B extraction
                      </div>
                      <h1 className="text-3xl font-black text-white mb-2">
                        Your <span className="gradient-text">best-fit</span> roles
                      </h1>
                      <p className="text-gray-400 text-sm">Ranked by readiness score. Click to generate your roadmap with Nemotron 253B.</p>
                    </div>

                    <div className="space-y-3 mb-4">
                      {suggestions?.map((s, i) => (
                        <motion.button key={s.role}
                          initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.07 }}
                          onClick={() => handleRoleConfirmed(s.role)}
                          className="w-full group glass rounded-xl px-5 py-4 flex items-center gap-4 hover:border-red-500/35 border border-white/8 transition-all duration-300 hover:shadow-[0_0_28px_rgba(239,68,68,0.12)]"
                        >
                          <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-black shrink-0 ${
                            i === 0 ? "bg-red-500/25 border border-red-500/50 text-red-300" : "bg-white/5 border border-white/10 text-gray-500"
                          }`}>
                            {i === 0 ? <Star className="w-4 h-4" /> : i + 1}
                          </div>
                          <div className="flex-1 text-left min-w-0">
                            <div className="flex items-center gap-2 mb-0.5 flex-wrap">
                              <span className="text-white font-bold text-sm">{s.role}</span>
                              {i === 0 && <span className="text-[10px] px-2 py-0.5 rounded-full bg-red-500/15 border border-red-500/30 text-red-300 font-semibold">BEST MATCH</span>}
                            </div>
                            <p className="text-gray-500 text-xs truncate">
                              {s.matched_skills.length > 0 ? `Already have: ${s.matched_skills.slice(0, 3).join(", ")}${s.matched_skills.length > 3 ? "…" : ""}` : "Build from scratch"}
                            </p>
                          </div>
                          <div className="shrink-0 text-right mr-2">
                            <p className={`text-xl font-black leading-none ${s.readiness_pct >= 50 ? "text-emerald-400" : s.readiness_pct >= 25 ? "text-amber-400" : "text-gray-500"}`}>
                              {s.readiness_pct.toFixed(0)}%
                            </p>
                            <p className="text-[10px] text-gray-600 mt-0.5">ready</p>
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-red-400 group-hover:translate-x-0.5 transition-all shrink-0" />
                        </motion.button>
                      ))}
                    </div>

                    <button onClick={() => setShowAllRoles(v => !v)}
                      className="w-full flex items-center justify-center gap-2 text-xs text-gray-600 hover:text-gray-300 transition-colors py-2">
                      <RefreshCw className="w-3 h-3" />
                      {showAllRoles ? "Show fewer" : "My role isn't listed — show all 30+ roles"}
                    </button>
                    <AnimatePresence>
                      {showAllRoles && (
                        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
                          className="grid grid-cols-2 gap-2 mt-2 overflow-hidden">
                          {allRoles.map((r) => (
                            <button key={r} onClick={() => handleRoleConfirmed(r)}
                              className="glass rounded-lg px-3 py-2 text-xs text-gray-300 hover:text-white hover:border-red-500/35 border border-white/5 transition-all text-left">
                              {r}
                            </button>
                          ))}
                        </motion.div>
                      )}
                    </AnimatePresence>
                    <button onClick={() => setResumePhase("drop")}
                      className="mt-4 flex items-center gap-1.5 text-sm text-gray-600 hover:text-gray-300 transition-colors mx-auto">
                      <Upload className="w-3.5 h-3.5" /> Upload a different resume
                    </button>
                  </motion.div>
                )}
              </div>
            </div>
          </motion.div>
        )}

        {/* ══════════════ MANUAL SCENE ══════════════ */}
        {scene === "manual" && (
          <motion.div key="manual" variants={fade} initial="initial" animate="animate" exit="exit"
            className="fixed inset-0 z-50 bg-[#0a0a0a] overflow-y-auto">
            <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12">

              <div className="fixed top-0 left-0 right-0 z-10 px-6 py-4 flex items-center justify-between glass-dark border-b border-white/5">
                <span className="font-bold text-white text-sm">Build Your <span className="gradient-text">Path</span></span>
                <div className="flex items-center gap-4">
                  <div className="hidden sm:flex items-center gap-1">
                    {["Role", "Skills", "Timeline"].map((s, i) => {
                      const idx = manualStep === "role" ? 0 : manualStep === "skills" ? 1 : 2;
                      return (
                        <div key={s} className="flex items-center gap-1">
                          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                            i === idx ? "bg-red-500 text-white shadow-[0_0_12px_rgba(239,68,68,0.5)]"
                            : i < idx ? "bg-emerald-500/80 text-white" : "bg-white/5 text-gray-600"
                          }`}>
                            {i < idx ? <CheckCircle2 className="w-3.5 h-3.5" /> : i + 1}
                          </div>
                          <span className={`text-xs ${i === idx ? "text-white" : "text-gray-600"}`}>{s}</span>
                          {i < 2 && <div className="w-6 h-px bg-white/10 mx-1" />}
                        </div>
                      );
                    })}
                  </div>
                  <button onClick={() => setScene("home")} className="p-2 rounded-xl hover:bg-white/5 text-gray-500 hover:text-white transition-colors">
                    <X className="w-5 h-5" />
                  </button>
                </div>
              </div>

              <div className="mt-20 w-full max-w-2xl">
                <AnimatePresence mode="wait">

                  {manualStep === "role" && (
                    <motion.div key="step-role" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} transition={{ duration: 0.3 }}>
                      <div className="text-center mb-8">
                        <p className="text-4xl mb-3">🎯</p>
                        <h2 className="text-3xl font-black text-white mb-2">What&apos;s your <span className="gradient-text">destination?</span></h2>
                        <p className="text-gray-400 text-sm">Choose from 30+ career tracks</p>
                      </div>
                      <div className="grid grid-cols-2 gap-2.5 mb-8 max-h-80 overflow-y-auto pr-1">
                        {roles.map((r) => (
                          <motion.button key={r} whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
                            onClick={() => setSelectedRole(r)}
                            className={`text-left p-4 rounded-xl border transition-all duration-200 ${
                              selectedRole === r
                                ? "bg-red-500/15 border-red-500/55 text-white shadow-[0_0_20px_rgba(239,68,68,0.15)]"
                                : "glass border-white/5 text-gray-300 hover:border-red-500/20 hover:bg-red-500/4"
                            }`}>
                            <p className="font-semibold text-sm leading-snug">{r}</p>
                          </motion.button>
                        ))}
                      </div>
                      <button disabled={!selectedRole} onClick={() => setManualStep("skills")}
                        className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-30 disabled:pointer-events-none py-4 rounded-xl">
                        Continue to Skills <ChevronRight className="w-4 h-4" />
                      </button>
                    </motion.div>
                  )}

                  {manualStep === "skills" && (
                    <motion.div key="step-skills" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} transition={{ duration: 0.3 }}>
                      <div className="text-center mb-6">
                        <p className="text-4xl mb-3">🧰</p>
                        <h2 className="text-3xl font-black text-white mb-2">Your current <span className="gradient-text">toolkit</span></h2>
                        <p className="text-gray-400 text-sm">Tap to add skills you already have</p>
                      </div>
                      {(SKILL_SUGGESTIONS[selectedRole] || []).length > 0 && (
                        <div className="mb-6">
                          <p className="text-xs text-gray-500 uppercase tracking-wider mb-3">Quick add for {selectedRole}</p>
                          <div className="flex flex-wrap gap-2">
                            {(SKILL_SUGGESTIONS[selectedRole] || []).map((s) => (
                              <button key={s} onClick={() => addSkill(s)}
                                className={`skill-chip ${selectedSkills.includes(s) ? "skill-chip-active" : ""}`}>
                                {selectedSkills.includes(s) ? <span className="flex items-center gap-1"><CheckCircle2 className="w-3 h-3" />{s}</span> : `+ ${s}`}
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                      <div className="flex gap-2 mb-4">
                        <input value={skillInput} onChange={(e) => setSkillInput(e.target.value)}
                          onKeyDown={(e) => { if (e.key === "Enter") addSkill(skillInput); }}
                          placeholder="Add a custom skill and press Enter"
                          className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-red-500/40 transition-colors"
                        />
                        <button onClick={() => addSkill(skillInput)} className="px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/25 text-red-400 hover:bg-red-500/20 transition-colors">
                          <Plus className="w-4 h-4" />
                        </button>
                      </div>
                      {selectedSkills.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-6 p-4 glass rounded-xl min-h-14">
                          {selectedSkills.map((s) => (
                            <span key={s} className="skill-tag flex items-center gap-1.5">
                              {s}
                              <button onClick={() => setSelectedSkills((p) => p.filter((x) => x !== s))}
                                className="ml-0.5 hover:text-red-400 transition-colors"><X className="w-3 h-3" /></button>
                            </span>
                          ))}
                        </div>
                      )}
                      <div className="flex gap-3">
                        <button onClick={() => setManualStep("role")} className="px-6 py-4 rounded-xl glass border border-white/10 text-gray-400 hover:text-white transition-colors flex items-center gap-2 text-sm">
                          <ArrowLeft className="w-4 h-4" /> Back
                        </button>
                        <button onClick={() => setManualStep("timeline")}
                          className="flex-1 btn-primary flex items-center justify-center gap-2 py-4 rounded-xl">
                          Continue <ChevronRight className="w-4 h-4" />
                        </button>
                      </div>
                    </motion.div>
                  )}

                  {manualStep === "timeline" && (
                    <motion.div key="step-timeline" initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }} transition={{ duration: 0.3 }}>
                      <div className="text-center mb-8">
                        <p className="text-4xl mb-3">⏱️</p>
                        <h2 className="text-3xl font-black text-white mb-2">When do you want to <span className="gradient-text">arrive?</span></h2>
                        <p className="text-gray-400 text-sm">Set your runway — Nemotron 253B calibrates the intensity</p>
                      </div>
                      <div className="grid grid-cols-5 gap-3 mb-8">
                        {MONTHS.map((m) => (
                          <motion.button key={m} whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                            onClick={() => setSelectedMonths(m)}
                            className={`p-5 rounded-xl border text-center transition-all duration-200 ${
                              selectedMonths === m
                                ? "bg-red-500/18 border-red-500/60 text-white shadow-[0_0_22px_rgba(239,68,68,0.25)]"
                                : "glass border-white/8 text-gray-400 hover:border-red-500/25"
                            }`}>
                            <div className="text-3xl font-black text-white">{m}</div>
                            <div className="text-xs text-gray-500 mt-1">{m === 1 ? "month" : "months"}</div>
                          </motion.button>
                        ))}
                      </div>
                      <div className="glass rounded-xl p-5 mb-6 border border-red-500/12">
                        <p className="text-xs text-gray-500 uppercase tracking-wider mb-3 font-semibold">Your journey summary</p>
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <p className="text-white font-bold text-sm truncate">{selectedRole || "—"}</p>
                            <p className="text-gray-600 text-xs mt-0.5">Target role</p>
                          </div>
                          <div>
                            <p className="text-white font-bold text-sm">{selectedSkills.length}</p>
                            <p className="text-gray-600 text-xs mt-0.5">Current skills</p>
                          </div>
                          <div>
                            <p className="text-white font-bold text-sm">{selectedMonths} mo.</p>
                            <p className="text-gray-600 text-xs mt-0.5">Timeline</p>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-3">
                        <button onClick={() => setManualStep("skills")} className="px-6 py-4 rounded-xl glass border border-white/10 text-gray-400 hover:text-white transition-colors flex items-center gap-2 text-sm">
                          <ArrowLeft className="w-4 h-4" /> Back
                        </button>
                        <button onClick={handleManualContinue}
                          className="flex-1 btn-cta flex items-center justify-center gap-2 py-4 rounded-xl text-base">
                          <Rocket className="w-5 h-5" /> Generate My Roadmap
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>
        )}

        {/* ══════════════ GENERATING SCENE ══════════════ */}
        {scene === "generating" && (
          <motion.div key="generating" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
            className="fixed inset-0 z-50 flex flex-col items-center justify-center"
            style={{ background: "radial-gradient(ellipse at 50% 40%, rgba(239,68,68,0.10) 0%, #0a0a0a 60%)" }}
          >
            <CinematicHeroBg />
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              {[300, 230, 160, 95].map((size, i) => (
                <motion.div key={size}
                  className="absolute rounded-full border border-red-500/10"
                  style={{ width: size, height: size }}
                  animate={{ scale: [1, 1.07, 1], opacity: [0.25, 0.55, 0.25] }}
                  transition={{ duration: 3.2 + i * 0.6, repeat: Infinity, delay: i * 0.35 }}
                />
              ))}
            </div>

            <div className="relative z-10 mb-10">
              <div className="relative w-28 h-28">
                {[
                  { size: "w-28 h-28", color: "border-red-500/40",    dur: "2s" },
                  { size: "w-20 h-20", color: "border-orange-500/30", dur: "1.5s" },
                  { size: "w-12 h-12", color: "border-red-400/50",    dur: "1s" },
                ].map(({ size, color, dur }, i) => (
                  <div key={i}
                    className={`absolute inset-0 m-auto ${size} rounded-full border-2 ${color} border-t-transparent animate-spin`}
                    style={{ animationDuration: dur, animationDirection: i % 2 === 1 ? "reverse" : "normal" }}
                  />
                ))}
                <div className="absolute inset-0 m-auto w-8 h-8 rounded-full bg-red-500/60 blur-sm animate-pulse" />
                <div className="absolute inset-0 m-auto w-5 h-5 rounded-full bg-white/80" />
              </div>
            </div>

            <motion.div className="text-center z-10 px-4">
              <h2 className="text-3xl font-black text-white mb-3">
                Building your <span className="gradient-text">roadmap</span>
              </h2>
              <AnimatePresence mode="wait">
                <motion.p key={genStep}
                  initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                  transition={{ duration: 0.35 }}
                  className="text-gray-400 text-lg mb-6"
                >
                  {GEN_STEPS[genStep]}
                </motion.p>
              </AnimatePresence>
              <div className="max-w-xs mx-auto">
                <div className="w-full bg-white/5 rounded-full h-1">
                  <motion.div className="h-1 rounded-full progress-bar" animate={{ width: `${progress}%` }} transition={{ duration: 0.8 }} />
                </div>
                <p className="text-xs text-gray-600 mt-2">{progress}%</p>
              </div>
              <div className="mt-8 flex items-center justify-center gap-6 text-xs text-gray-600">
                {AI_MODELS.map((m) => (
                  <div key={m.name} className="flex flex-col items-center gap-1">
                    <div className={`w-6 h-6 rounded-lg flex items-center justify-center bg-white/5 ${m.color}`}>{m.icon}</div>
                    <span className="hidden sm:block">{m.name.split(" ")[0]}</span>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}

      </AnimatePresence>
    </div>
  );
}
