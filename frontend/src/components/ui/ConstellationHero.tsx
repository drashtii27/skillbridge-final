"use client";

import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

const PATH_D =
  "M55,215 C95,215 125,110 170,110 C215,110 255,180 300,180 C345,180 385,85 430,85 C475,85 510,190 548,190";

const NODES = [
  { x: 55,  y: 215, label: "Upload",   sub: "Resume",    color: "#ef4444", delay: 1.0 },
  { x: 170, y: 110, label: "Analyze",  sub: "Skill Map", color: "#f97316", delay: 1.3 },
  { x: 300, y: 180, label: "Roadmap",  sub: "AI Plan",   color: "#ef4444", delay: 1.6 },
  { x: 430, y: 85,  label: "Practice", sub: "Interview", color: "#f97316", delay: 1.9 },
  { x: 548, y: 190, label: "Hired!",   sub: "Dream Job", color: "#ef4444", delay: 2.2 },
];

export default function ConstellationHero() {
  const pathRef = useRef<SVGPathElement>(null);
  const dotRef  = useRef<SVGCircleElement>(null);
  const glowRef = useRef<SVGCircleElement>(null);

  useEffect(() => {
    let animId: number;
    let progress = 0;

    const tick = () => {
      const path = pathRef.current;
      const dot  = dotRef.current;
      const glow = glowRef.current;
      if (path && dot && glow) {
        progress = (progress + 0.0018) % 1;
        const len = path.getTotalLength();
        const pt  = path.getPointAtLength(progress * len);
        dot.setAttribute("cx",  String(pt.x));
        dot.setAttribute("cy",  String(pt.y));
        glow.setAttribute("cx", String(pt.x));
        glow.setAttribute("cy", String(pt.y));
      }
      animId = requestAnimationFrame(tick);
    };

    const t = setTimeout(() => { animId = requestAnimationFrame(tick); }, 3600);
    return () => { clearTimeout(t); cancelAnimationFrame(animId); };
  }, []);

  return (
    <div className="relative w-full h-[280px] md:h-[320px] select-none">
      <div
        className="absolute inset-0 rounded-3xl pointer-events-none"
        style={{ background: "radial-gradient(ellipse at 50% 55%, rgba(239,68,68,0.08) 0%, transparent 70%)" }}
      />

      <svg viewBox="0 0 608 300" className="w-full h-full" aria-hidden="true">
        <defs>
          <filter id="ch-glow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="4" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <filter id="ch-node-glow" x="-120%" y="-120%" width="340%" height="340%">
            <feGaussianBlur stdDeviation="6" result="blur"/>
            <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
          <linearGradient id="ch-grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%"   stopColor="#ef4444"/>
            <stop offset="50%"  stopColor="#f97316"/>
            <stop offset="100%" stopColor="#ef4444"/>
          </linearGradient>
        </defs>

        {/* Glow shadow behind path */}
        <path
          d={PATH_D} fill="none" stroke="url(#ch-grad)"
          strokeWidth="8" strokeLinecap="round" opacity="0.10"
          filter="url(#ch-glow)"
        />

        {/* Animated draw-in path */}
        <motion.path
          ref={pathRef}
          d={PATH_D} fill="none" stroke="url(#ch-grad)"
          strokeWidth="2" strokeLinecap="round"
          strokeDasharray="700"
          initial={{ strokeDashoffset: 700, opacity: 0 }}
          animate={{ strokeDashoffset: 0, opacity: 0.65 }}
          transition={{ duration: 2.6, ease: "easeInOut", delay: 0.7 }}
          filter="url(#ch-glow)"
        />

        {/* Traveling dot */}
        <circle ref={glowRef} cx="55" cy="215" r="12" fill="#ef4444" opacity="0.20" filter="url(#ch-glow)" />
        <circle ref={dotRef}  cx="55" cy="215" r="4.5" fill="#ef4444" opacity="0.95" filter="url(#ch-glow)" />

        {/* Nodes */}
        {NODES.map((n, i) => {
          const above = i % 2 !== 0;
          const ly = above ? n.y - 28 : n.y + 34;
          const sy = above ? n.y - 16 : n.y + 46;
          return (
            <motion.g
              key={n.label}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: n.delay, type: "spring", stiffness: 220, damping: 18 }}
              style={{ transformOrigin: `${n.x}px ${n.y}px` }}
            >
              <motion.circle
                cx={n.x} cy={n.y} fill="none"
                stroke={n.color} strokeWidth="1.5"
                initial={{ r: 14, opacity: 0.7 }}
                animate={{ r: 28, opacity: 0 }}
                transition={{ duration: 2.5, repeat: Infinity, delay: n.delay + 0.3, ease: "easeOut" }}
              />
              <circle cx={n.x} cy={n.y} r="19" fill="none" stroke={n.color} strokeWidth="0.8" opacity="0.18" />
              <circle
                cx={n.x} cy={n.y} r="13"
                fill={`${n.color}18`} stroke={n.color} strokeWidth="1.5"
                filter="url(#ch-node-glow)"
              />
              <circle cx={n.x} cy={n.y} r="4.5" fill={n.color} />
              <text x={n.x} y={ly} textAnchor="middle" fill="white"
                fontSize="10" fontWeight="700" fontFamily="Inter,system-ui">
                {n.label}
              </text>
              <text x={n.x} y={sy} textAnchor="middle"
                fill="rgba(161,161,170,0.75)" fontSize="8" fontFamily="Inter,system-ui">
                {n.sub}
              </text>
            </motion.g>
          );
        })}
      </svg>
    </div>
  );
}
