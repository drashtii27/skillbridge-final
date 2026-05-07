"use client";

import { motion } from "framer-motion";
import { clsx } from "clsx";

interface Props {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
  glow?: boolean;
  onClick?: () => void;
}

export default function GlassCard({ children, className, hover = false, glow = false, onClick }: Props) {
  return (
    <motion.div
      onClick={onClick}
      whileHover={hover ? { y: -4, scale: 1.01 } : undefined}
      transition={{ type: "spring", stiffness: 300, damping: 20 }}
      className={clsx(
        "glass rounded-2xl p-6",
        glow && "neon-border",
        hover && "cursor-pointer",
        className
      )}
      style={glow ? { boxShadow: "0 0 30px rgba(99,102,241,0.12), inset 0 0 30px rgba(99,102,241,0.03)" } : undefined}
    >
      {children}
    </motion.div>
  );
}
