"use client";

import { useEffect, useRef } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

export default function AnimatedCursor() {
  const cursorX = useMotionValue(-100);
  const cursorY = useMotionValue(-100);
  const trailX = useMotionValue(-100);
  const trailY = useMotionValue(-100);

  const springX = useSpring(trailX, { stiffness: 80, damping: 15 });
  const springY = useSpring(trailY, { stiffness: 80, damping: 15 });

  const isHoveringRef = useRef(false);
  const dotRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const move = (e: MouseEvent) => {
      cursorX.set(e.clientX - 8);
      cursorY.set(e.clientY - 8);
      trailX.set(e.clientX - 16);
      trailY.set(e.clientY - 16);
    };

    const over = (e: MouseEvent) => {
      const t = e.target as HTMLElement;
      isHoveringRef.current = !!(t.closest("a,button,[role=button],input,textarea,select,[data-hover]"));
      if (dotRef.current) {
        dotRef.current.style.transform = isHoveringRef.current ? "scale(2.5)" : "scale(1)";
      }
    };

    window.addEventListener("mousemove", move);
    window.addEventListener("mouseover", over);
    return () => { window.removeEventListener("mousemove", move); window.removeEventListener("mouseover", over); };
  }, [cursorX, cursorY, trailX, trailY]);

  return (
    <>
      {/* Dot cursor */}
      <motion.div
        ref={dotRef}
        className="fixed top-0 left-0 w-4 h-4 rounded-full bg-red-400 pointer-events-none z-[9999] mix-blend-difference"
        style={{ x: cursorX, y: cursorY }}
        transition={{ type: "tween", duration: 0 }}
      />
      {/* Glow ring */}
      <motion.div
        className="fixed top-0 left-0 w-8 h-8 rounded-full pointer-events-none z-[9998]"
        style={{
          x: springX,
          y: springY,
          background: "radial-gradient(circle, rgba(239,68,68,0.3) 0%, transparent 70%)",
          border: "1px solid rgba(239,68,68,0.5)",
        }}
      />
    </>
  );
}
