"use client";

import { motion } from "framer-motion";

const WORDS = [
  { text: "Python",       x: "6%",  y: "12%", size: 12, dx: 18,  dy: -10, dr: 3  },
  { text: "React",        x: "82%", y: "8%",  size: 11, dx: -14, dy: 8,   dr: -2 },
  { text: "SQL",          x: "18%", y: "72%", size: 14, dx: 10,  dy: -16, dr: 4  },
  { text: "Machine Learning", x: "70%", y: "75%", size: 10, dx: -12, dy: 10, dr: -3 },
  { text: "Docker",       x: "88%", y: "40%", size: 11, dx: -8,  dy: 12,  dr: 2  },
  { text: "TypeScript",   x: "3%",  y: "45%", size: 12, dx: 16,  dy: 8,   dr: -4 },
  { text: "AWS",          x: "45%", y: "5%",  size: 13, dx: -10, dy: 14,  dr: 3  },
  { text: "TensorFlow",   x: "60%", y: "90%", size: 10, dx: 8,   dy: -12, dr: -2 },
  { text: "Kubernetes",   x: "25%", y: "90%", size: 10, dx: 12,  dy: -8,  dr: 5  },
  { text: "Node.js",      x: "92%", y: "65%", size: 11, dx: -16, dy: -10, dr: -3 },
  { text: "GraphQL",      x: "38%", y: "95%", size: 10, dx: 6,   dy: -14, dr: 2  },
  { text: "PyTorch",      x: "78%", y: "22%", size: 11, dx: -10, dy: 10,  dr: -4 },
  { text: "Figma",        x: "12%", y: "28%", size: 12, dx: 14,  dy: 12,  dr: 3  },
  { text: "FastAPI",      x: "52%", y: "88%", size: 11, dx: -8,  dy: -10, dr: -2 },
  { text: "Next.js",      x: "92%", y: "88%", size: 12, dx: -12, dy: 8,   dr: 4  },
];

export default function FloatingKeywords() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden="true">
      {WORDS.map((w) => (
        <motion.span
          key={w.text}
          className="absolute font-mono font-semibold whitespace-nowrap"
          style={{
            left: w.x,
            top: w.y,
            fontSize: w.size,
            color: "rgba(167,139,250,0.12)",
            userSelect: "none",
            "--dx": `${w.dx}px`,
            "--dy": `${w.dy}px`,
            "--dr": `${w.dr}deg`,
          } as React.CSSProperties}
          animate={{
            x: [0, w.dx, 0],
            y: [0, w.dy, 0],
            rotate: [0, w.dr, 0],
            opacity: [0.07, 0.16, 0.07],
          }}
          transition={{
            duration: 8 + Math.abs(w.dx) * 0.3,
            repeat: Infinity,
            ease: "easeInOut",
            delay: Math.abs(w.dy) * 0.1,
          }}
        >
          {w.text}
        </motion.span>
      ))}
    </div>
  );
}
