import { cn } from '@/lib/utils';

interface StatCardProps {
  title: string;
  value: string | number;
  color?: 'purple' | 'cyan' | 'amber' | 'green' | 'red' | 'default';
  icon?: React.ReactNode;
}

const colorClasses = {
  purple: 'text-primary',
  cyan: 'text-cyan',
  amber: 'text-amber',
  green: 'text-green',
  red: 'text-red',
  default: 'text-textPrimary',
};

export function StatCard({ title, value, color = 'default', icon }: StatCardProps) {
  return (
    <div className="bg-surface rounded-xl border border-border p-4 hover:border-primary/50 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-textSecondary text-sm">{title}</span>
        {icon && <div className="text-textSecondary">{icon}</div>}
      </div>
      <div className={cn('font-mono text-2xl font-bold mt-2', colorClasses[color])}>
        {value}
      </div>
    </div>
  );
}