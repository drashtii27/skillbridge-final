"use client";

import { useEffect, useRef } from "react";

export default function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;
    let animId: number;
    let mouseX = -9999, mouseY = -9999;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();

    const onResize = () => resize();
    const onMouse = (e: MouseEvent) => { mouseX = e.clientX; mouseY = e.clientY; };
    window.addEventListener("resize", onResize);
    window.addEventListener("mousemove", onMouse);

    const COLORS = ["239,68,68", "249,115,22", "220,38,38", "253,186,116", "239,68,68"];

    interface Particle {
      x: number; y: number; vx: number; vy: number;
      size: number; opacity: number; color: string; phase: number;
    }
    interface Star { x: number; y: number; vx: number; vy: number; life: number; maxLife: number; }

    const particles: Particle[] = Array.from({ length: 110 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.35,
      vy: (Math.random() - 0.5) * 0.35,
      size: Math.random() * 1.8 + 0.4,
      opacity: Math.random() * 0.55 + 0.08,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      phase: Math.random() * Math.PI * 2,
    }));

    const stars: Star[] = [];

    const spawnStar = () => {
      if (Math.random() > 0.007) return;
      stars.push({
        x: Math.random() * canvas.width,
        y: Math.random() * 0.4 * canvas.height,
        vx: (Math.random() - 0.4) * 5,
        vy: Math.random() * 3.5 + 1.5,
        life: 0,
        maxLife: 50 + Math.random() * 40,
      });
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      spawnStar();

      for (let i = stars.length - 1; i >= 0; i--) {
        const s = stars[i];
        s.x += s.vx; s.y += s.vy; s.life++;
        if (s.life > s.maxLife) { stars.splice(i, 1); continue; }
        const t = s.life / s.maxLife;
        const alpha = t < 0.4 ? t / 0.4 : (1 - t) / 0.6;
        const len = 14;
        ctx.beginPath();
        ctx.strokeStyle = `rgba(239,68,68,${alpha * 0.6})`;
        ctx.lineWidth = 1.2;
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(s.x - s.vx * len, s.y - s.vy * len);
        ctx.stroke();
      }

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const d2 = dx * dx + dy * dy;
          if (d2 < 10000) {
            const d = Math.sqrt(d2);
            ctx.beginPath();
            ctx.strokeStyle = `rgba(239,68,68,${(1 - d / 100) * 0.07})`;
            ctx.lineWidth = 0.5;
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.stroke();
          }
        }
      }

      particles.forEach((p) => {
        const dx = p.x - mouseX, dy = p.y - mouseY;
        const md = Math.sqrt(dx * dx + dy * dy);
        if (md < 120) {
          const f = ((120 - md) / 120) * 0.6;
          p.vx += (dx / md) * f;
          p.vy += (dy / md) * f;
        }

        const spd = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
        if (spd > 1.8) { p.vx *= 0.92; p.vy *= 0.92; }
        if (spd < 0.05) { p.vx += (Math.random() - 0.5) * 0.08; p.vy += (Math.random() - 0.5) * 0.08; }

        p.x += p.vx; p.y += p.vy;
        if (p.x < 0) p.x = canvas.width;
        if (p.x > canvas.width) p.x = 0;
        if (p.y < 0) p.y = canvas.height;
        if (p.y > canvas.height) p.y = 0;

        p.phase += 0.018;
        const pulse = Math.sin(p.phase) * 0.25 + 0.75;

        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 4);
        g.addColorStop(0, `rgba(${p.color},${p.opacity * pulse * 0.8})`);
        g.addColorStop(1, `rgba(${p.color},0)`);
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * 4, 0, Math.PI * 2);
        ctx.fillStyle = g;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${p.color},${p.opacity * pulse})`;
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("mousemove", onMouse);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0 pointer-events-none"
      aria-hidden="true"
    />
  );
}
