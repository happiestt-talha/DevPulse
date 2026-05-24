'use client';

import { useWakaTimeStats } from '@/lib/api';
import { LineChart } from '@/components/charts/LineChart';
import { HorizontalBarChart } from '@/components/charts/HorizontalBarChart';
import { StatCard } from '@/components/stats/StatCard';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDuration } from '@/lib/utils';

export default function WakaTimePage() {
  const { data: stats, isLoading } = useWakaTimeStats();

  if (isLoading) return <WakaTimeSkeleton />;
  if (!stats) return <div className="text-red">Failed to load WakaTime stats</div>;

  const allTimeHours = (stats.total_seconds / 3600).toFixed(1);
  const todayHours = (stats.today_seconds / 3600).toFixed(1);
  const weekHours = (stats.week_seconds / 3600).toFixed(1);

  // Prepare daily breakdown for line chart
  const dailyData = stats.daily_breakdown?.map(d => ({ date: d.date, hours: (d.seconds / 3600).toFixed(1) })) || [];

  // Prepare language, project, editor data for horizontal bars
  const langData = stats.languages?.map(l => ({ name: l.name, value: l.percent })) || [];
  const projectData = stats.projects?.map(p => ({ name: p.name, value: p.hours })) || [];
  const editorData = stats.editors?.map(e => ({ name: e.name, value: e.percent })) || [];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">WakaTime Analytics</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Coding Time" value={`${allTimeHours}h`} color="cyan" />
        <StatCard title="Today" value={`${todayHours}h`} color="cyan" />
        <StatCard title="This Week" value={`${weekHours}h`} color="cyan" />
        <StatCard title="Best Day" value={stats.best_day_seconds ? `${(stats.best_day_seconds / 3600).toFixed(1)}h` : '—'} color="amber" />
      </div>

      <LineChart data={dailyData} xKey="date" yKey="hours" title="Daily Coding Hours (Last 30 Days)" color="#06B6D4" />

      <div className="grid md:grid-cols-2 gap-6">
        <HorizontalBarChart data={langData} title="Time by Language (%)" barColor="#A78BFA" />
        <HorizontalBarChart data={projectData} title="Time by Project (hours)" barColor="#7C3AED" />
      </div>

      <HorizontalBarChart data={editorData} title="Time by Editor (%)" barColor="#F59E0B" />
    </div>
  );
}

function WakaTimeSkeleton() {
  return (
    <div className="space-y-6">
      <Skeleton className="h-8 w-48" />
      <div className="grid grid-cols-4 gap-4"><Skeleton className="h-24" /><Skeleton className="h-24" /><Skeleton className="h-24" /><Skeleton className="h-24" /></div>
      <Skeleton className="h-64" />
    </div>
  );
}