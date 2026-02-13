"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const FOOD_EMOJIS = [
  "\uD83C\uDF4E", "\uD83C\uDF4C", "\uD83C\uDF52", "\uD83C\uDF53", "\uD83C\uDF50",
  "\uD83C\uDF4A", "\uD83C\uDF4B", "\uD83C\uDF49", "\uD83C\uDF47", "\uD83C\uDF51",
  "\uD83E\uDD51", "\uD83E\uDD6D", "\uD83C\uDF46", "\uD83E\uDD55", "\uD83C\uDF3D",
  "\uD83C\uDF36\uFE0F", "\uD83E\uDD66", "\uD83E\uDDC0", "\uD83C\uDF57", "\uD83C\uDF56",
  "\uD83C\uDF54", "\uD83C\uDF55", "\uD83C\uDF2E", "\uD83C\uDF2F", "\uD83E\uDD5A",
  "\uD83C\uDF73", "\uD83E\uDD53", "\uD83E\uDD69", "\uD83C\uDF5E", "\uD83E\uDD50",
];

interface EmojiParticle {
  id: number;
  emoji: string;
  left: number;
  delay: number;
  duration: number;
  size: number;
}

function FallingEmojisInner() {
  const [particles, setParticles] = useState<EmojiParticle[]>([]);

  useEffect(() => {
    setParticles(
      Array.from({ length: 30 }, (_, i) => ({
        id: i,
        emoji: FOOD_EMOJIS[Math.floor(Math.random() * FOOD_EMOJIS.length)],
        left: Math.random() * 100,
        delay: Math.random() * 8,
        duration: 6 + Math.random() * 8,
        size: 18 + Math.random() * 16,
      }))
    );
  }, []);

  if (particles.length === 0) return null;

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map((p) => (
        <span
          key={p.id}
          className="absolute animate-fall"
          style={{
            left: `${p.left}%`,
            fontSize: `${p.size}px`,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
            opacity: 0.12,
          }}
        >
          {p.emoji}
        </span>
      ))}
    </div>
  );
}

const FallingEmojis = dynamic(() => Promise.resolve(FallingEmojisInner), {
  ssr: false,
});

export default FallingEmojis;
