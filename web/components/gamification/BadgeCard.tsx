import { cn } from '@/lib/utils';
import { Lock } from 'lucide-react';

export function BadgeCard({ badge }: { badge: any }) {
  return (
    <div className={cn('relative bg-surfaceElevated rounded-xl p-4 text-center transition-all hover:scale-105', !badge.earned && 'opacity-40 grayscale')}>
      <div className="w-16 h-16 mx-auto rounded-full bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center mb-2">
        {!badge.earned && <Lock className="w-6 h-6 text-textSecondary" />}
      </div>
      <h4 className="font-semibold text-sm">{badge.name}</h4>
      <p className="text-xs text-textSecondary">{badge.xp_reward} XP</p>
      {!badge.earned && (
        <div className="mt-2 w-full bg-surface rounded-full h-1">
          <div className="bg-primary h-1 rounded-full" style={{ width: `${badge.progress}%` }} />
        </div>
      )}
    </div>
  );
}