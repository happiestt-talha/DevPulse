'use client';

import { useLeetCodeStats } from '@/lib/api';
import { DonutChart } from '@/components/charts/DonutChart';
import { BarChart } from '@/components/charts/BarChart';
import { StatCard } from '@/components/stats/StatCard';

export default function LeetCodePage() {
  const { data: stats, isLoading } = useLeetCodeStats();
  if (isLoading) return <div>Loading LeetCode stats...</div>;
  if (!stats) return <div>No data</div>;

  const difficultyData = [
    { name: 'Easy', percent: stats.easy_solved },
    { name: 'Medium', percent: stats.medium_solved },
    { name: 'Hard', percent: stats.hard_solved },
  ];

  const recentByLang: Record<string, number> = {};
  stats.recent_submissions.forEach((s) => {
    recentByLang[s.lang] = (recentByLang[s.lang] || 0) + 1;
  });
  const langBarData = Object.entries(recentByLang).map(([name, value]) => ({ name, value }));

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">LeetCode Analytics</h1>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard title="Total Solved" value={stats.total_solved} />
        <StatCard title="Acceptance Rate" value={`${stats.acceptance_rate.toFixed(1)}%`} />
        <StatCard title="Ranking" value={stats.ranking.toLocaleString()} />
        <StatCard title="Contest Rating" value={Math.round(stats.contest_rating)} />
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <DonutChart data={difficultyData} title="Problems by Difficulty" />
        <BarChart data={langBarData} title="Recent Submissions by Language" />
      </div>
      <div className="grid md:grid-cols-3 gap-4">
        <StatCard title="Easy Solved" value={stats.easy_solved} />
        <StatCard title="Medium Solved" value={stats.medium_solved} />
        <StatCard title="Hard Solved" value={stats.hard_solved} />
      </div>

      {stats.recent_submissions.length > 0 && (
        <div className="bg-surface rounded-xl border border-border p-4">
          <h3 className="text-lg font-semibold mb-3">Recent Submissions</h3>
          <div className="space-y-2">
            {stats.recent_submissions.slice(0, 10).map((sub, i) => (
              <div
                key={i}
                className="flex items-center justify-between bg-surfaceElevated rounded-lg px-4 py-2"
              >
                <div className="flex items-center gap-3">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      sub.status === 'Accepted' ? 'bg-green' : 'bg-red'
                    }`}
                  />
                  <span className="text-sm text-textPrimary">{sub.title}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-textSecondary">{sub.lang}</span>
                  <span className="text-xs text-textSecondary">
                    {new Date(sub.timestamp * 1000).toLocaleDateString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
