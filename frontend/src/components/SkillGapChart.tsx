"use client";

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar } from "recharts";
import GlassCard from "./ui/GlassCard";
import type { SkillGapResult } from "@/types";

export default function SkillGapChart({ gapResult }: { gapResult: SkillGapResult }) {
  const barData = gapResult.category_chart.categories.map((cat, i) => ({
    name: cat,
    Have: gapResult.category_chart.have[i],
    Need: gapResult.category_chart.need[i],
  }));

  const radarData = gapResult.category_chart.categories.map((cat, i) => {
    const have = gapResult.category_chart.have[i];
    const need = gapResult.category_chart.need[i];
    const total = have + need || 1;
    return { subject: cat, A: Math.round((have / total) * 100) };
  });

  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: { name: string; value: number; fill: string }[]; label?: string }) => {
    if (!active || !payload?.length) return null;
    return (
      <div className="glass rounded-xl p-3 text-sm border border-white/10">
        <p className="font-semibold text-white mb-1">{label}</p>
        {payload.map((p) => (
          <p key={p.name} style={{ color: p.fill }}>{p.name}: {p.value}</p>
        ))}
      </div>
    );
  };

  return (
    <GlassCard>
      <h2 className="text-lg font-bold text-white mb-6">Skills Breakdown</h2>
      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <p className="text-xs text-gray-400 mb-3 uppercase tracking-wider">Skills by Category</p>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={barData} barGap={4}>
              <XAxis dataKey="name" tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="Have" fill="#ef4444" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Need" fill="rgba(239,68,68,0.6)" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-4 mt-2">
            <span className="flex items-center gap-1 text-xs text-gray-400"><span className="w-3 h-3 rounded-sm bg-red-500 inline-block" /> Have</span>
            <span className="flex items-center gap-1 text-xs text-gray-400"><span className="w-3 h-3 rounded-sm bg-red-500/60 inline-block" /> Need</span>
          </div>
        </div>

        <div>
          <p className="text-xs text-gray-400 mb-3 uppercase tracking-wider">Readiness Radar</p>
          <ResponsiveContainer width="100%" height={200}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="rgba(255,255,255,0.1)" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "#9ca3af", fontSize: 11 }} />
              <Radar name="Readiness" dataKey="A" stroke="#ef4444" fill="#ef4444" fillOpacity={0.2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Skills tags */}
      <div className="mt-6 grid md:grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">✅ You Have</p>
          <div className="flex flex-wrap gap-2">
            {gapResult.matched.slice(0, 8).map((s) => (
              <span key={s.skill} className="skill-tag-success text-xs px-2 py-1 rounded-full">{s.skill}</span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs text-gray-400 mb-2 uppercase tracking-wider">🎯 To Learn</p>
          <div className="flex flex-wrap gap-2">
            {gapResult.gaps.slice(0, 8).map((s) => (
              <span key={s.skill} className="skill-tag-danger text-xs px-2 py-1 rounded-full">{s.skill}</span>
            ))}
          </div>
        </div>
      </div>
    </GlassCard>
  );
}
