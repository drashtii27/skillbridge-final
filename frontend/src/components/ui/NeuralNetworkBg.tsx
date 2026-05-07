"use client";

import { useEffect, useRef } from "react";

interface Node {
  x: number; y: number;
  vx: number; vy: number;
  r: number;
  pulse: number; pulseSpeed: number;
  opacity: number;
  color: string;
}

interface Particle {
  fromNode: number; toNode: number;
  t: number; speed: number;
  opacity: number;
}

const COLORS = [
  "239,68,68",    // red
  "249,115,22",   // orange
  "220,38,38",    // dark red
  "253,186,116",  // light orange
  "239,68,68",    // red again (weighted)
];

export default function NeuralNetworkBg() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;
    let animId: number;
    let mouseX = -9999, mouseY = -9999;
    let width = 0, height = 0;

    const resize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", (e) => { mouseX = e.clientX; mouseY = e.clientY; });

    // Create nodes
    const NODE_COUNT = 55;
    const nodes: Node[] = Array.from({ length: NODE_COUNT }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      r: Math.random() * 3 + 1.5,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: 0.02 + Math.random() * 0.025,
      opacity: 0.4 + Math.random() * 0.5,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
    }));

    // Connection threshold
    const CONNECT_DIST = 180;
    // Data particles traveling along edges
    const particles: Particle[] = [];

    const spawnParticle = () => {
      if (particles.length > 80 || Math.random() > 0.08) return;
      // pick random edge
      const a = Math.floor(Math.random() * NODE_COUNT);
      let b = Math.floor(Math.random() * NODE_COUNT);
      if (b === a) b = (a + 1) % NODE_COUNT;
      const dx = nodes[a].x - nodes[b].x, dy = nodes[a].y - nodes[b].y;
      if (Math.sqrt(dx * dx + dy * dy) < CONNECT_DIST) {
        particles.push({ fromNode: a, toNode: b, t: 0, speed: 0.004 + Math.random() * 0.006, opacity: 0.8 + Math.random() * 0.2 });
      }
    };

    const drawFrame = () => {
      ctx.clearRect(0, 0, width, height);

      // Update + draw nodes
      for (const n of nodes) {
        // Mouse repulsion
        const dx = n.x - mouseX, dy = n.y - mouseY;
        const md = Math.sqrt(dx * dx + dy * dy);
        if (md < 150 && md > 0) {
          const f = ((150 - md) / 150) * 0.5;
          n.vx += (dx / md) * f;
          n.vy += (dy / md) * f;
        }
        const spd = Math.sqrt(n.vx * n.vx + n.vy * n.vy);
        if (spd > 2) { n.vx *= 0.9; n.vy *= 0.9; }

        n.x += n.vx; n.y += n.vy;
        if (n.x < 0) n.x = width; if (n.x > width) n.x = 0;
        if (n.y < 0) n.y = height; if (n.y > height) n.y = 0;

        n.pulse += n.pulseSpeed;
        const pulseFactor = 0.7 + 0.3 * Math.sin(n.pulse);
        const glow = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r * 7 * pulseFactor);
        glow.addColorStop(0, `rgba(${n.color},${n.opacity * pulseFactor * 0.7})`);
        glow.addColorStop(1, `rgba(${n.color},0)`);
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r * 7 * pulseFactor, 0, Math.PI * 2);
        ctx.fillStyle = glow;
        ctx.fill();

        ctx.beginPath();
        ctx.arc(n.x, n.y, n.r * pulseFactor, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${n.color},${n.opacity * pulseFactor})`;
        ctx.fill();
      }

      // Draw edges
      for (let i = 0; i < NODE_COUNT; i++) {
        for (let j = i + 1; j < NODE_COUNT; j++) {
          const dx = nodes[i].x - nodes[j].x, dy = nodes[i].y - nodes[j].y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < CONNECT_DIST) {
            const alpha = (1 - d / CONNECT_DIST) * 0.15;
            const grad = ctx.createLinearGradient(nodes[i].x, nodes[i].y, nodes[j].x, nodes[j].y);
            grad.addColorStop(0, `rgba(${nodes[i].color},${alpha})`);
            grad.addColorStop(1, `rgba(${nodes[j].color},${alpha})`);
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = grad;
            ctx.lineWidth = 0.8;
            ctx.stroke();
          }
        }
      }

      // Spawn + draw particles
      spawnParticle();
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.t += p.speed;
        if (p.t >= 1) { particles.splice(i, 1); continue; }

        const from = nodes[p.fromNode], to = nodes[p.toNode];
        const dx = to.x - from.x, dy = to.y - from.y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d >= CONNECT_DIST) { particles.splice(i, 1); continue; }

        const px = from.x + dx * p.t, py = from.y + dy * p.t;
        const fadeAlpha = p.opacity * (1 - Math.abs(p.t - 0.5) * 2);

        ctx.beginPath();
        ctx.arc(px, py, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${from.color},${fadeAlpha})`;
        ctx.fill();

        // Tail
        const tailLen = 0.06;
        const tx = from.x + dx * Math.max(0, p.t - tailLen);
        const ty = from.y + dy * Math.max(0, p.t - tailLen);
        const tailGrad = ctx.createLinearGradient(tx, ty, px, py);
        tailGrad.addColorStop(0, `rgba(${from.color},0)`);
        tailGrad.addColorStop(1, `rgba(${from.color},${fadeAlpha * 0.5})`);
        ctx.beginPath();
        ctx.moveTo(tx, ty);
        ctx.lineTo(px, py);
        ctx.strokeStyle = tailGrad;
        ctx.lineWidth = 1.2;
        ctx.stroke();
      }

      animId = requestAnimationFrame(drawFrame);
    };
    drawFrame();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener("resize", resize);
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
