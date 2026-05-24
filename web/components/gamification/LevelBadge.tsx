import { cn } from '@/lib/utils';
import { Award } from 'lucide-react';

interface LevelBadgeProps {
  level: number;
  totalXp: number;
  className?: string;
}

const levelTitles: Record<number, string> = {
  1: 'Intern',
  2: 'Junior Dev',
  3: 'Mid Dev',
  4: 'Senior Dev',
  5: 'Staff Engineer',
  6: 'Principal',
  7: 'Legend',
};

export function LevelBadge({ level, totalXp, className }: LevelBadgeProps) {
  const title = levelTitles[level] || 'Developer';
  return (
    <div className={cn('flex items-center gap-2 bg-primary/10 rounded-full px-3 py-1 border border-primary/30', className)}>
      <Award className="w-4 h-4 text-primary" />
      <span className="text-xs font-medium text-primary">{title}</span>
      <span className="text-xs text-textSecondary">{totalXp} XP</span>
    </div>
  );
}