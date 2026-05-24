'use client';

import { cn } from '@/lib/utils';
import { Flame, IceCream, Calendar } from 'lucide-react';

interface StreakCounterProps {
  streak: number;
  longest?: number;
  atRisk?: boolean;
  freezeCount?: number;
}

export function StreakCounter({ streak, longest, atRisk = false, freezeCount = 0 }: StreakCounterProps) {
  return (
    <div className={cn('bg-surface rounded-xl border p-4 transition-all', atRisk ? 'border-red animate-pulse' : 'border-border')}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Flame className={cn('w-6 h-6', streak > 0 ? 'text-amber' : 'text-textSecondary')} />
          <span className="font-mono text-3xl font-bold text-amber">{streak}</span>
          <span className="text-textSecondary text-sm">day streak</span>
        </div>
        {freezeCount > 0 && (
          <div className="flex items-center gap-1">
            <IceCream className="w-4 h-4 text-cyan" />
            <span className="text-xs text-cyan">{freezeCount}</span>
          </div>
        )}
      </div>
      {longest !== undefined && (
        <div className="flex items-center gap-2 mt-2 text-xs text-textSecondary">
          <Calendar className="w-3 h-3" />
          <span>Longest: {longest} days</span>
        </div>
      )}
      {atRisk && (
        <p className="text-xs text-red mt-2">Streak at risk – code today!</p>
      )}
    </div>
  );
}