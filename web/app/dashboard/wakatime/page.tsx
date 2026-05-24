'use client';

import { useWakaTimeStats } from '@/lib/api';
import { DonutChart } from '@/components/charts/DonutChart';
import { BarChart } from '@/components/charts/BarChart';
import { StatCard } from '@/components/stats/StatCard';

function formatTime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  return `${h}h ${m}m`;
}

export default function WakaTimePage() {
  const { data: stats, isLoading } = useWakaTimeStats();
  if (isLoading) return <div>Loading WakaTime stats...</div>;
  if (!stats) return <div>No data</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">WakaTime Analytics</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Coding Time" value={formatTime(stats.total_seconds)} />
        <StatCard title="Today" value={formatTime(stats.today_seconds)} />
        <StatCard title="This Week" value={formatTime(stats.week_seconds)} />
        <StatCard
          title="Best Day"
          value={stats.best_day_date ? `${formatTime(stats.best_day_seconds)} (${stats.best_day_date})` : 'N/A'}
        />
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <DonutChart data={stats.languages} title="Languages" />
        <DonutChart data={stats.editors} title="Editors" />
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <BarChart
          data={stats.projects.map((p) => ({ name: p.name, value: p.hours }))}
          title="Projects (hours)"
        />
        <BarChart
          data={stats.daily_breakdown.slice(-14).map((d) => ({
            name: d.date.slice(5),
            value: Math.round(d.seconds / 3600),
          }))}
          title="Daily Activity (hours, last 14 days)"
        />
      </div>
    </div>
  );
}
