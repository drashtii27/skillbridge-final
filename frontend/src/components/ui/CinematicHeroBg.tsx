"use client";
import { useEffect, useRef } from "react";

const KEYWORDS = [
  "Python", "React", "LLM", "RAG", "CUDA", "Docker", "FastAPI",
  "PyTorch", "SQL", "K8s", "TypeScript", "Neural", "Vector",
  "LoRA", "NLP", "API", "CI/CD", "AWS", "Transformer", "GPU",
  "Embedding", "MLOps", "DeepSeek", "Nemotron", "Qwen3",
];

export default function CinematicHeroBg() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animFrame: number;
    let t = 0;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);

    // Aurora blobs — 3 large slowly-drifting radial gradient orbs
    const orbs = [
      { px: 0.15, py: 0.22, r: 0.55, rgb: [239, 68, 68]  as [number,number,number], sp: 0.00028, phase: 0 },
      { px: 0.82, py: 0.62, r: 0.48, rgb: [249, 115, 22] as [number,number,number], sp: 0.00020, phase: 2.1 },
      { px: 0.50, py: 0.88, r: 0.42, rgb: [220, 38, 38]  as [number,number,number], sp: 0.00022, phase: 4.5 },
    ];

    // Star field — 200 distant twinkling points
    const stars = Array.from({ length: 200 }, () => ({
      x: Math.random(),
      y: Math.random(),
      r: 0.25 + Math.random() * 1.1,
      base: 0.08 + Math.random() * 0.42,
      tw: Math.random() * Math.PI * 2,
    }));

    // Scanning light beams — 2 horizontal sweeps
    const beams = [
      { y: 0.28, vy: 0.000075, opacity: 0.055 },
      { y: 0.71, vy: 0.000055, opacity: 0.038 },
    ];

    // Floating tech keywords
    const kwds = KEYWORDS.map((text, i) => ({
      text,
      x: 0.04 + Math.random() * 0.92,
      y: Math.random(),
      vy: -(0.000038 + Math.random() * 0.000085),
      opacity: 0.038 + Math.random() * 0.052,
      size: 10 + Math.floor(Math.random() * 7),
      phase: i * 0.37,
    }));

    const draw = () => {
      const W = canvas.width;
      const H = canvas.height;
      t += 1;

      // Base fill — deep near-black
      ctx.fillStyle = "#030308";
      ctx.fillRect(0, 0, W, H);

      // Aurora blobs
      orbs.forEach((orb) => {
        const cx = (Math.sin(t * orb.sp + orb.phase) * 0.18 + orb.px) * W;
        const cy = (Math.cos(t * orb.sp * 0.73 + orb.phase + 1) * 0.14 + orb.py) * H;
        const radius = orb.r * Math.min(W, H);
        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, radius);
        const [r, g, b] = orb.rgb;
        grad.addColorStop(0,    `rgba(${r},${g},${b},0.10)`);
        grad.addColorStop(0.45, `rgba(${r},${g},${b},0.038)`);
        grad.addColorStop(1,    `rgba(${r},${g},${b},0)`);
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, W, H);
      });

      // Star field
      stars.forEach((s) => {
        const tw = Math.sin(t * 0.025 + s.tw);
        ctx.beginPath();
        ctx.arc(s.x * W, s.y * H, s.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255,255,255,${s.base * (0.6 + tw * 0.4)})`;
        ctx.fill();
      });

      // Light beams
      beams.forEach((beam) => {
        beam.y += beam.vy;
        if (beam.y > 1.06) beam.y = -0.06;
        const y = beam.y * H;
        const grad = ctx.createLinearGradient(0, 0, W, 0);
        grad.addColorStop(0,   "rgba(255,255,255,0)");
        grad.addColorStop(0.2, `rgba(255,130,70,${beam.opacity})`);
        grad.addColorStop(0.8, `rgba(255,130,70,${beam.opacity})`);
        grad.addColorStop(1,   "rgba(255,255,255,0)");
        ctx.fillStyle = grad;
        ctx.fillRect(0, y - 1, W, 2);
      });

      // Central vortex glow — pulses slowly
      const pulse = 0.062 + Math.sin(t * 0.011) * 0.022;
      const vg = ctx.createRadialGradient(W * 0.5, H * 0.42, 0, W * 0.5, H * 0.42, Math.min(W, H) * 0.30);
      vg.addColorStop(0,   `rgba(239,68,68,${pulse})`);
      vg.addColorStop(0.5, `rgba(249,115,22,${pulse * 0.28})`);
      vg.addColorStop(1,   "rgba(239,68,68,0)");
      ctx.fillStyle = vg;
      ctx.fillRect(0, 0, W, H);

      // Floating keywords
      kwds.forEach((kw) => {
        kw.y += kw.vy;
        if (kw.y < -0.06) kw.y = 1.06;
        const alpha = kw.opacity * (0.65 + Math.sin(t * 0.018 + kw.phase) * 0.35);
        ctx.font = `${kw.size}px "JetBrains Mono", "Fira Mono", monospace`;
        ctx.fillStyle = `rgba(249,115,22,${alpha})`;
        ctx.fillText(kw.text, kw.x * W, kw.y * H);
      });

      animFrame = requestAnimationFrame(draw);
    };

    draw();

    return () => {
      cancelAnimationFrame(animFrame);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
    />
  );
}
