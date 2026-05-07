"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useScroll, useTransform } from "framer-motion";

interface Milestone {
  position_pct: number;
  label: string;
  completed: boolean;
  active: boolean;
}

interface Props {
  milestones: Milestone[];
  overallProgress: number; // 0-100
}

export default function CarJourney({ milestones, overallProgress }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgSize, setSvgSize] = useState({ w: 300, h: 800 });

  useEffect(() => {
    const update = () => {
      if (containerRef.current) {
        setSvgSize({ w: containerRef.current.clientWidth, h: Math.max(containerRef.current.clientHeight, 600) });
      }
    };
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  const { w, h } = svgSize;
  const cx = w / 2;

  // Winding road path — S-curve from bottom to top
  const roadPath = `
    M ${cx} ${h - 20}
    C ${cx + 80} ${h * 0.75}, ${cx - 100} ${h * 0.6}, ${cx} ${h * 0.5}
    C ${cx + 120} ${h * 0.4}, ${cx - 80} ${h * 0.25}, ${cx} ${h * 0.12}
  `;

  // Car position along path based on progress
  const carProgress = overallProgress / 100;

  // Get point at given fraction along path (approximation)
  const getPointAtFraction = (t: number) => {
    const segments = [
      { from: { x: cx, y: h - 20 }, cp1: { x: cx + 80, y: h * 0.75 }, cp2: { x: cx - 100, y: h * 0.6 }, to: { x: cx, y: h * 0.5 } },
      { from: { x: cx, y: h * 0.5 }, cp1: { x: cx + 120, y: h * 0.4 }, cp2: { x: cx - 80, y: h * 0.25 }, to: { x: cx, y: h * 0.12 } },
    ];
    const segIdx = t < 0.5 ? 0 : 1;
    const segT = t < 0.5 ? t * 2 : (t - 0.5) * 2;
    const seg = segments[segIdx];
    const mt = 1 - segT;
    return {
      x: mt ** 3 * seg.from.x + 3 * mt ** 2 * segT * seg.cp1.x + 3 * mt * segT ** 2 * seg.cp2.x + segT ** 3 * seg.to.x,
      y: mt ** 3 * seg.from.y + 3 * mt ** 2 * segT * seg.cp1.y + 3 * mt * segT ** 2 * seg.cp2.y + segT ** 3 * seg.to.y,
    };
  };

  const carPos = getPointAtFraction(carProgress);

  return (
    <div ref={containerRef} className="relative w-full" style={{ minHeight: 600 }}>
      <svg width={w} height={h} className="absolute inset-0">
        <defs>
          <linearGradient id="roadGrad" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0%" stopColor="#1e1b4b" />
            <stop offset="50%" stopColor="#312e81" />
            <stop offset="100%" stopColor="#4c1d95" />
          </linearGradient>
          <linearGradient id="progressGrad" x1="0" y1="1" x2="0" y2="0">
            <stop offset="0%" stopColor="#6366f1" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="coloredBlur" />
            <feMerge><feMergeNode in="coloredBlur" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        {/* Road shadow/base */}
        <path d={roadPath} fill="none" stroke="url(#roadGrad)" strokeWidth={48} strokeLinecap="round" />
        {/* Road edges */}
        <path d={roadPath} fill="none" stroke="rgba(99,102,241,0.3)" strokeWidth={50} strokeLinecap="round" />
        {/* Road surface */}
        <path d={roadPath} fill="none" stroke="#1e1b4b" strokeWidth={44} strokeLinecap="round" />
        {/* Center dashes */}
        <path d={roadPath} fill="none" stroke="rgba(255,255,255,0.15)" strokeWidth={2} strokeDasharray="12 8" strokeLinecap="round" />
        {/* Progress overlay */}
        <motion.path
          d={roadPath}
          fill="none"
          stroke="url(#progressGrad)"
          strokeWidth={4}
          strokeLinecap="round"
          filter="url(#glow)"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: carProgress }}
          transition={{ duration: 1.5, ease: "easeInOut" }}
        />

        {/* Milestone dots */}
        {milestones.map((m, i) => {
          const pt = getPointAtFraction(m.position_pct / 100);
          return (
            <g key={i}>
              {/* Outer pulse ring */}
              {m.active && (
                <motion.circle
                  cx={pt.x} cy={pt.y} r={20}
                  fill="none" stroke="rgba(99,102,241,0.4)"
                  animate={{ r: [16, 24, 16], opacity: [0.8, 0.2, 0.8] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              )}
              {/* Milestone circle */}
              <circle
                cx={pt.x} cy={pt.y} r={m.completed ? 12 : 10}
                fill={m.completed ? "#10b981" : m.active ? "#6366f1" : "#1e1b4b"}
                stroke={m.completed ? "#6ee7b7" : "#6366f1"}
                strokeWidth={2}
                filter={m.active ? "url(#glow)" : undefined}
              />
              {/* Check or number */}
              <text x={pt.x} y={pt.y + 4} textAnchor="middle" fill="white" fontSize={9} fontWeight="bold">
                {m.completed ? "✓" : `${i + 1}`}
              </text>
            </g>
          );
        })}

        {/* Car */}
        <motion.g
          animate={{ x: carPos.x - 16, y: carPos.y - 12 }}
          transition={{ type: "spring", stiffness: 60, damping: 15 }}
        >
          {/* Car body */}
          <rect width={32} height={20} rx={6} fill="#6366f1" filter="url(#glow)" />
          <rect x={6} y={-6} width={20} height={14} rx={4} fill="#818cf8" />
          {/* Windshield */}
          <rect x={8} y={-4} width={16} height={10} rx={2} fill="rgba(6,182,212,0.6)" />
          {/* Wheels */}
          <circle cx={6} cy={20} r={5} fill="#1e1b4b" stroke="#374151" strokeWidth={1.5} />
          <circle cx={26} cy={20} r={5} fill="#1e1b4b" stroke="#374151" strokeWidth={1.5} />
          <circle cx={6} cy={20} r={2} fill="#6366f1" />
          <circle cx={26} cy={20} r={2} fill="#6366f1" />
          {/* Headlights */}
          <motion.circle cx={32} cy={10} r={3} fill="rgba(253,224,71,0.9)"
            animate={{ opacity: [1, 0.5, 1] }} transition={{ duration: 1.5, repeat: Infinity }} />
          {/* Trail */}
          <motion.ellipse cx={-8} cy={14} rx={12} ry={4} fill="rgba(99,102,241,0.2)"
            animate={{ rx: [12, 20, 12], opacity: [0.4, 0.1, 0.4] }}
            transition={{ duration: 1, repeat: Infinity }} />
        </motion.g>
      </svg>
    </div>
  );
}
