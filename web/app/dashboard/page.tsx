'use client';

import { useOverview, useGitHubStats, useWakaTimeStats, useLeetCodeStats } from '@/lib/api';
import { motion } from 'framer-motion';
import { ScoreCard } from '@/components/stats/ScoreCard';
import { StatCardWithDelta } from '@/components/stats/StatCardWithDelta';
import { HeatmapGrid } from '@/components/stats/HeatmapGrid';
import { StreakCounter } from '@/components/stats/StreakCounter';
import { Skeleton } from '@/components/ui/skeleton';
import { GitCommit, Clock, Brain, TrendingUp, TrendingDown } from 'lucide-react';

export default function DashboardPage() {
  const { data: overview, isLoading: overviewLoading } = useOverview();
  const { data: github } = useGitHubStats();
  const { data: wakatime } = useWakaTimeStats();
  const { data: leetcode } = useLeetCodeStats();

  if (overviewLoading) return <DashboardSkeleton />;
  if (!overview) return <div className="text-red">Failed to load dashboard</div>;

  // Calculate weekly deltas (mock if needed – real backend would provide)
  // For now we'll use dummy deltas – they would come from separate endpoint.
  const commitDelta = 12; // +12%
  const codingDelta = -5;
  const problemsDelta = 8;

  return (
    <div className="space-y-6">
      {/* Hero section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ScoreCard score={overview.developer_score} level={overview.level} totalXp={overview.total_xp} />
        </div>
        <div className="space-y-4">
          <StatCardWithDelta
            title="Today's Commits"
            value={overview.today.commits}
            delta={commitDelta}
            color="green"
            icon={<GitCommit className="w-4 h-4" />}
          />
          <StatCardWithDelta
            title="Coding Minutes"
            value={`${Math.floor(overview.today.coding_minutes / 60)}h ${overview.today.coding_minutes % 60}m`}
            delta={codingDelta}
            color="cyan"
            icon={<Clock className="w-4 h-4" />}
          />
          <StatCardWithDelta
            title="Problems Solved"
            value={overview.today.problems_solved}
            delta={problemsDelta}
            color="amber"
            icon={<Brain className="w-4 h-4" />}
          />
        </div>
      </div>

      {/* Streak and heatmap row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <HeatmapGrid />
        </div>
        <div>
          <StreakCounter streak={overview.streak_current} longest={overview.streak_longest} />
        </div>
      </div>

      {/* Weekly comparison */}
      <div className="bg-surface rounded-xl border border-border p-4">
        <h3 className="text-lg font-semibold mb-3">Weekly Comparison (vs last week)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div className="text-textSecondary text-sm">Commits</div>
            <div className="font-mono text-xl">{github?.commits_30d || 0}</div>
            <div className="flex items-center text-xs mt-1 text-green"><TrendingUp className="w-3 h-3 mr-1" /> +15%</div>
          </div>
          <div>
            <div className="text-textSecondary text-sm">Coding hours</div>
            <div className="font-mono text-xl">{wakatime ? (wakatime.week_seconds / 3600).toFixed(1) : 0}h</div>
            <div className="flex items-center text-xs mt-1 text-red"><TrendingDown className="w-3 h-3 mr-1" /> -8%</div>
          </div>
          <div>
            <div className="text-textSecondary text-sm">Problems</div>
            <div className="font-mono text-xl">{leetcode?.total_solved || 0}</div>
            <div className="flex items-center text-xs mt-1 text-green"><TrendingUp className="w-3 h-3 mr-1" /> +22%</div>
          </div>
          <div>
            <div className="text-textSecondary text-sm">PRs merged</div>
            <div className="font-mono text-xl">{github?.prs_merged_30d || 0}</div>
            <div className="flex items-center text-xs mt-1 text-green"><TrendingUp className="w-3 h-3 mr-1" /> +5%</div>
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