"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Plus, X, ChevronRight } from "lucide-react";
import { getRoles } from "@/lib/api";

const SKILL_SUGGESTIONS: Record<string, string[]> = {
  "Machine Learning Engineer": ["Python", "PyTorch", "scikit-learn", "NumPy", "Pandas", "SQL", "Docker", "Git"],
  "Data Scientist": ["Python", "SQL", "Pandas", "NumPy", "Matplotlib", "Statistics", "R"],
  "Software Engineer (Frontend)": ["JavaScript", "TypeScript", "React", "CSS", "HTML", "Git"],
  "Software Engineer (Backend)": ["Python", "SQL", "REST APIs", "Git", "Docker"],
  "Full Stack Developer": ["JavaScript", "React", "Node.js", "SQL", "Git"],
  "DevOps / Cloud Engineer": ["Linux", "Docker", "Kubernetes", "Terraform", "AWS", "Bash"],
  "Data Engineer": ["Python", "SQL", "Spark", "Airflow", "dbt"],
  "Cybersecurity Engineer": ["Linux", "Python", "Networking", "Penetration Testing"],
  "UI/UX Designer": ["Figma", "Prototyping", "User Research", "Design Systems"],
  "Product Manager": ["Agile", "User Research", "Data Analysis", "Roadmapping"],
};

interface Props {
  onContinue: (role: string, skills: string[], months: number) => void;
  loading: boolean;
}

export default function RoleSelector({ onContinue, loading }: Props) {
  const [roles, setRoles] = useState<string[]>([]);
  const [selectedRole, setSelectedRole] = useState("");
  const [skills, setSkills] = useState<string[]>([]);
  const [skillInput, setSkillInput] = useState("");
  const [months, setMonths] = useState(3);
  const [step, setStep] = useState<"role" | "skills" | "timeline">("role");

  useEffect(() => {
    getRoles().then((r) => setRoles(r.data.roles || [])).catch(() => {});
  }, []);

  const addSkill = (s: string) => {
    const trimmed = s.trim();
    if (trimmed && !skills.includes(trimmed)) setSkills((prev) => [...prev, trimmed]);
    setSkillInput("");
  };

  const suggestions = SKILL_SUGGESTIONS[selectedRole] || [];

  return (
    <div className="glass rounded-2xl p-8 text-left">
      {step === "role" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h2 className="text-2xl font-bold text-white mb-2">What&apos;s your target role?</h2>
          <p className="text-gray-400 text-sm mb-6">We&apos;ll build your roadmap around this</p>
          <div className="grid grid-cols-2 gap-2 max-h-64 overflow-y-auto pr-1">
            {roles.map((r) => (
              <button
                key={r}
                onClick={() => setSelectedRole(r)}
                className={`text-left p-3 rounded-xl text-sm transition-all duration-200 border
                  ${selectedRole === r
                    ? "bg-red-500/20 border-red-500/50 text-white"
                    : "glass border-white/5 text-gray-300 hover:border-white/20"}`}
              >
                {r}
              </button>
            ))}
          </div>
          <button
            disabled={!selectedRole}
            onClick={() => setStep("skills")}
            className="mt-6 w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-40"
          >
            Continue <ChevronRight className="w-4 h-4" />
          </button>
        </motion.div>
      )}

      {step === "skills" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h2 className="text-2xl font-bold text-white mb-2">Your current skills</h2>
          <p className="text-gray-400 text-sm mb-4">Add what you already know</p>

          {suggestions.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Quick add for {selectedRole}:</p>
              <div className="flex flex-wrap gap-2">
                {suggestions.filter((s) => !skills.includes(s)).map((s) => (
                  <button key={s} onClick={() => addSkill(s)} className="skill-tag hover:bg-red-500/30 transition-colors">
                    + {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-2 mb-3">
            <input
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") addSkill(skillInput); }}
              placeholder="Type a skill and press Enter"
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-red-500/50"
            />
            <button onClick={() => addSkill(skillInput)} className="px-4 py-2.5 rounded-xl bg-red-500/20 border border-red-500/30 text-red-300 hover:bg-red-500/30 transition-colors">
              <Plus className="w-4 h-4" />
            </button>
          </div>

          <div className="flex flex-wrap gap-2 min-h-12 mb-4">
            {skills.map((s) => (
              <span key={s} className="skill-tag flex items-center gap-1">
                {s}
                <button onClick={() => setSkills((prev) => prev.filter((x) => x !== s))}><X className="w-3 h-3" /></button>
              </span>
            ))}
          </div>

          <button
            onClick={() => setStep("timeline")}
            className="w-full btn-primary flex items-center justify-center gap-2"
          >
            Continue <ChevronRight className="w-4 h-4" />
          </button>
        </motion.div>
      )}

      {step === "timeline" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <h2 className="text-2xl font-bold text-white mb-2">Your timeline</h2>
          <p className="text-gray-400 text-sm mb-6">How many months to reach your goal?</p>
          <div className="grid grid-cols-3 gap-3 mb-8">
            {[1, 2, 3, 4, 6].map((m) => (
              <button
                key={m}
                onClick={() => setMonths(m)}
                className={`p-4 rounded-xl border text-center transition-all duration-200
                  ${months === m ? "bg-red-500/20 border-red-500/50 text-white" : "glass border-white/5 text-gray-300 hover:border-white/20"}`}
              >
                <div className="text-2xl font-bold">{m}</div>
                <div className="text-xs text-gray-400">{m === 1 ? "month" : "months"}</div>
              </button>
            ))}
          </div>
          <button
            disabled={loading}
            onClick={() => onContinue(selectedRole, skills, months)}
            className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> Generating...</>
            ) : (
              <><ChevronRight className="w-4 h-4" /> Generate My Roadmap</>
            )}
          </button>
        </motion.div>
      )}
    </div>
  );
}
