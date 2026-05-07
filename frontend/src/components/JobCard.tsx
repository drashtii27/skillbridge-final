"use client";

import { ExternalLink, MapPin, DollarSign, Building2 } from "lucide-react";
import { trackJobClick } from "@/lib/api";
import { trackEvent } from "@/lib/posthog";
import type { Job } from "@/types";

export default function JobCard({ job }: { job: Job }) {
  const handleClick = () => {
    trackJobClick(job.url, job.title).catch(() => {});
    trackEvent("job_clicked", { title: job.title, company: job.company });
    window.open(job.url, "_blank", "noopener,noreferrer");
  };

  const salary = job.salary_min && job.salary_max
    ? `$${Math.round(job.salary_min / 1000)}k – $${Math.round(job.salary_max / 1000)}k`
    : null;

  const initials = job.company.slice(0, 2).toUpperCase();
  const colors = ["bg-red-500", "bg-orange-500", "bg-rose-500", "bg-emerald-500", "bg-amber-500"];
  const color = colors[job.company.charCodeAt(0) % colors.length];

  return (
    <div className="glass rounded-2xl p-5 card-hover group">
      <div className="flex items-start gap-3 mb-3">
        <div className={`w-10 h-10 ${color} rounded-xl flex items-center justify-center text-white text-sm font-bold flex-shrink-0`}>
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white text-sm leading-tight truncate">{job.title}</h3>
          <div className="flex items-center gap-1 text-xs text-gray-400 mt-0.5">
            <Building2 className="w-3 h-3" />{job.company}
          </div>
        </div>
      </div>
      <div className="flex items-center gap-3 text-xs text-gray-400 mb-3">
        {job.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{job.location}</span>}
        {salary && <span className="flex items-center gap-1 text-emerald-400"><DollarSign className="w-3 h-3" />{salary}</span>}
      </div>
      {job.description_snippet && (
        <p className="text-xs text-gray-500 mb-4 line-clamp-2 leading-relaxed">{job.description_snippet}</p>
      )}
      <button
        onClick={handleClick}
        className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-300 text-xs font-medium hover:bg-red-500/20 transition-colors group-hover:border-red-500/40"
      >
        Apply Now <ExternalLink className="w-3 h-3" />
      </button>
    </div>
  );
}
