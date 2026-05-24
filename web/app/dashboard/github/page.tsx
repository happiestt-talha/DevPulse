'use client';

import { useGitHubStats } from '@/lib/api';
import { DonutChart } from '@/components/charts/DonutChart';
import { BarChart } from '@/components/charts/BarChart';
import { StatCard } from '@/components/stats/StatCard';

export default function GitHubPage() {
  const { data: stats, isLoading } = useGitHubStats();
  if (isLoading) return <div>Loading GitHub stats...</div>;
  if (!stats) return <div>No data</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">GitHub Analytics</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Commits" value={stats.total_commits} />
        <StatCard title="PRs Merged" value={stats.total_prs_merged} />
        <StatCard title="Issues Closed" value={stats.total_issues_closed} />
        <StatCard title="Stars Earned" value={stats.total_stars_earned} />
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <DonutChart data={stats.top_languages.map((l) => ({ name: l.language, percent: l.percent }))} title="Languages" />
        <BarChart data={[{ name: 'Commits (30d)', value: stats.commits_30d }]} title="Recent Activity" />
      </div>
    </div>
  );
}