import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardWithDeltaProps {
  title: string;
  value: string | number;
  delta?: number; // percentage change vs last week
  color?: 'purple' | 'cyan' | 'amber' | 'green' | 'red';
  icon?: React.ReactNode;
}

const colorClasses = {
  purple: 'text-primary',
  cyan: 'text-cyan',
  amber: 'text-amber',
  green: 'text-green',
  red: 'text-red',
};

export function StatCardWithDelta({ title, value, delta, color = 'purple', icon }: StatCardWithDeltaProps) {
  const isPositive = delta && delta > 0;
  return (
    <div className="bg-surface rounded-xl border border-border p-4 hover:border-primary/50 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-textSecondary text-sm">{title}</span>
        {icon && <div className="text-textSecondary">{icon}</div>}
      </div>
      <div className={cn('font-mono text-3xl font-bold mt-2', colorClasses[color])}>{value}</div>
      {delta !== undefined && (
        <div className="flex items-center gap-1 mt-2 text-xs">
          {isPositive ? (
            <TrendingUp className="w-3 h-3 text-green" />
          ) : (
            <TrendingDown className="w-3 h-3 text-red" />
          )}
          <span className={isPositive ? 'text-green' : 'text-red'}>{Math.abs(delta)}%</span>
          <span className="text-textSecondary">vs last week</span>
        </div>
      )}
    </div>
  );
}