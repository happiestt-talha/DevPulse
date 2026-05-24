'use client';

import { useOverview } from '@/lib/api';
import { motion } from 'framer-motion';
import { ScoreCard } from '@/components/stats/ScoreCard';
import { StatCard } from '@/components/stats/StatCard';
import { HeatmapGrid } from '@/components/stats/HeatmapGrid';
import { StreakCounter } from '@/components/stats/StreakCounter';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardPage() {
  const { data: overview, isLoading, error } = useOverview();

  if (isLoading) {
    return <DashboardSkeleton />;
  }
  if (error || !overview) {
    return <div className="text-red">Failed to load dashboard</div>;
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ScoreCard score={overview.developer_score} level={overview.level} totalXp={overview.total_xp} />
        </div>
        <div className="space-y-4">
          <StatCard
            title="Today's Commits"
            value={overview.today.commits}
            icon="git-commit"
            color="green"
          />
          <StatCard
            title="Today's Coding"
            value={`${Math.floor(overview.today.coding_minutes / 60)}h ${overview.today.coding_minutes % 60}m`}
            icon="clock"
            color="cyan"
          />
          <StatCard
            title="Problems Solved Today"
            value={overview.today.problems_solved}
            icon="brain"
            color="amber"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HeatmapGrid />
        <div className="bg-surface rounded-xl border border-border p-4">
          <h3 className="text-lg font-semibold mb-2">Weekly Goals</h3>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm">
                <span>Coding hours: {overview.weekly_goal_hours}h</span>
                <span>0 / {overview.weekly_goal_hours}</span>
              </div>
              <progress className="w-full h-2 rounded-full" value={0} max={overview.weekly_goal_hours} />
            </div>
            <div>
              <div className="flex justify-between text-sm">
                <span>Problems: {overview.weekly_goal_problems}</span>
                <span>0 / {overview.weekly_goal_problems}</span>
              </div>
              <progress className="w-full h-2 rounded-full" value={0} max={overview.weekly_goal_problems} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2"><Skeleton className="h-48 w-full" /></div>
        <div className="space-y-4"><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /><Skeleton className="h-24 w-full" /></div>
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    </div>
  );
}