interface ActiveHoursHeatmapProps {
  mostActiveDay?: string;
  mostActiveHour?: number;
}

export function ActiveHoursHeatmap({ mostActiveDay, mostActiveHour }: ActiveHoursHeatmapProps) {
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-sm font-medium text-textSecondary mb-3">Peak Activity</h3>
      <div className="space-y-2">
        <div className="flex justify-between">
          <span className="text-sm">Most active day:</span>
          <span className="font-mono text-primary">{mostActiveDay || '—'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm">Most active hour:</span>
          <span className="font-mono text-primary">{mostActiveHour !== undefined ? `${mostActiveHour}:00` : '—'}</span>
        </div>
      </div>
    </div>
  );
}