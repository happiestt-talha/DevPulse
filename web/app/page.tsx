'use client';

import { signInWithGitHub } from '@/lib/auth';
import { motion } from 'framer-motion';
import { Code2, Flame, Trophy, Zap } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-surface flex flex-col items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center max-w-3xl"
      >
        <h1 className="text-7xl font-bold font-mono mb-4 bg-gradient-to-r from-primary to-primaryLight bg-clip-text text-transparent">
          DevPulse
        </h1>
        <p className="text-xl text-textSecondary mb-8">Your code. Your stats. Your story.</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-12">
          <Feature icon={<Code2 className="w-8 h-8 text-primary" />} title="GitHub" desc="Commits, PRs, contributions" />
          <Feature icon={<Zap className="w-8 h-8 text-cyan" />} title="WakaTime" desc="Coding time, languages, projects" />
          <Feature icon={<Trophy className="w-8 h-8 text-amber" />} title="LeetCode" desc="Problems solved, ranking, streaks" />
        </div>

        <button
          onClick={signInWithGitHub}
          className="bg-primary hover:bg-primary/90 text-white font-semibold py-3 px-8 rounded-lg transition-all transform hover:scale-105 shadow-lg"
        >
          Connect GitHub → Start your journey
        </button>
      </motion.div>
    </div>
  );
}

function Feature({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="bg-surface/50 backdrop-blur-sm p-6 rounded-2xl border border-border">
      <div className="flex justify-center mb-3">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-textSecondary text-sm">{desc}</p>
    </div>
  );
}