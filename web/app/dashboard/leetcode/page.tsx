'use client';

import { useLeetCodeStats } from '@/lib/api';
import { ProblemRings } from '@/components/stats/ProblemRings';
import { RankingBadge } from '@/components/stats/RankingBadge';
import { RecentSubmissionsTable } from '@/components/stats/RecentSubmissionsTable';
import { StatCard } from '@/components/stats/StatCard';
import { Skeleton } from '@/components/ui/skeleton';

export default function LeetCodePage() {
  const { data: stats, isLoading } = useLeetCodeStats();

  if (isLoading) return <LeetCodeSkeleton />;
  if (!stats) return <div className="text-red">Failed to load LeetCode stats</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">LeetCode Analytics</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Solved" value={stats.total_solved} color="green" />
        <StatCard title="Acceptance Rate" value={`${(stats.acceptance_rate ?? 0).toFixed(1)}%`} color="amber" />
        <StatCard title="Total Submissions" value={stats.total_submissions ?? 0} color="purple" />
        <StatCard title="Contest Rating" value={(stats.contest_rating ?? 0).toFixed(0)} color="cyan" />
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <ProblemRings easy={stats.easy_solved ?? 0} medium={stats.medium_solved ?? 0} hard={stats.hard_solved ?? 0} />
        <RankingBadge ranking={stats.ranking ?? 0} percentile={stats.ranking_percentile ?? 0} />
      </div>

      <RecentSubmissionsTable submissions={stats.recent_submissions ?? []} />
    </div>
  );
}

function LeetCodeSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-4 gap-4"><Skeleton className="h-24" /><Skeleton className="h-24" /><Skeleton className="h-24" /><Skeleton className="h-24" /></div>
      <div className="grid md:grid-cols-2 gap-6"><Skeleton className="h-48" /><Skeleton className="h-48" /></div>
      <Skeleton className="h-64" />
    </div>
  );
}