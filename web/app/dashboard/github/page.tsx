'use client';

import { useGitHubStats } from '@/lib/api';
import { DonutChart } from '@/components/charts/DonutChart';
import { BarChart } from '@/components/charts/BarChart';
import { StatCard } from '@/components/stats/StatCard';
import { PRReviewCard } from '@/components/stats/PRReviewCard';
import { ActiveHoursHeatmap } from '@/components/stats/ActiveHoursHeatmap';
import { Skeleton } from '@/components/ui/skeleton';

export default function GitHubPage() {
  const { data: stats, isLoading } = useGitHubStats();

  if (isLoading) return <GitHubSkeleton />;
  if (!stats) return <div className="text-red">Failed to load GitHub stats</div>;

  // Prepare language data for donut
  const langData = stats.top_languages?.map(l => ({ name: l.language, value: l.percent })) || [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">GitHub Analytics</h1>

      {/* Lifetime stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Commits" value={stats.total_commits} color="purple" />
        <StatCard title="PRs Merged" value={stats.total_prs_merged} color="purple" />
        <StatCard title="Issues Closed" value={stats.total_issues_closed} color="purple" />
        <StatCard title="Stars Earned" value={stats.total_stars_earned} color="amber" />
      </div>

      {/* Last 30 days */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard title="Commits (30d)" value={stats.commits_30d} color="green" />
        <StatCard title="PRs Merged (30d)" value={stats.prs_merged_30d} color="green" />
        <StatCard title="Active Repos (30d)" value={stats.active_repos_30d} color="cyan" />
      </div>

      {/* Charts row */}
      <div className="grid md:grid-cols-2 gap-6">
        <DonutChart data={langData} title="Languages by Bytes" />
        <BarChart data={[{ name: 'Commits (30d)', value: stats.commits_30d }]} title="Commit Activity" />
      </div>

      {/* PR reviews + peak activity */}
      <div className="grid md:grid-cols-2 gap-6">
        <PRReviewCard reviewsGiven={stats.reviews_given_30d} reviewsReceived={0 /* not yet available */} />
        <ActiveHoursHeatmap mostActiveDay={stats.most_active_day} mostActiveHour={stats.most_active_hour} />
      </div>
    </div>
  );
}

function GitHubSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-4 gap-4"><Skeleton className="h-24" /><Skeleton className="h-24" /><Skeleton className="h-24" /><Skeleton className="h-24" /></div>
      <div className="grid grid-cols-2 gap-6"><Skeleton className="h-64" /><Skeleton className="h-64" /></div>
    </div>
  );
}