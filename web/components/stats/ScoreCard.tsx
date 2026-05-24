'use client';

import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export function ScoreCard({ score, level, totalXp }: { score: number; level: number; totalXp: number }) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    let start = 0;
    const duration = 1500;
    const step = Math.ceil(score / (duration / 16));
    const timer = setInterval(() => {
      start += step;
      if (start >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(start);
      }
    }, 16);
    return () => clearInterval(timer);
  }, [score]);

  return (
    <div className="bg-surface rounded-xl border border-border p-6 relative overflow-hidden">
      <div className="absolute top-2 right-2 bg-primary/20 text-primary px-3 py-1 rounded-full text-sm">
        Level {level}
      </div>
      <div className="text-center">
        <motion.div
          className="font-mono text-7xl font-bold text-primary"
          initial={{ scale: 0.8 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          {displayScore}
        </motion.div>
        <p className="text-textSecondary mt-2">Developer Score</p>
        <div className="mt-4 w-full bg-surfaceElevated rounded-full h-2">
          <div
            className="bg-primary h-2 rounded-full"
            style={{ width: `${(totalXp % 500) / 5}%` }}
          />
        </div>
      </div>
    </div>
  );
}
