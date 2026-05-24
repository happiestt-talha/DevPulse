export function RankingBadge({ ranking, percentile }: { ranking: number; percentile: number }) {
  return (
    <div className="bg-surface rounded-xl border border-border p-4 text-center">
      <div className="text-3xl font-mono font-bold text-primary">#{ranking}</div>
      <div className="text-xs text-textSecondary">Global Ranking</div>
      <div className="mt-2 text-sm">
        Top <span className="font-mono text-amber">{percentile}%</span>
      </div>
    </div>
  );
}