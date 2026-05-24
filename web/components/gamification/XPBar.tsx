export function XPBar({ totalXp, level, levelTitle, xpToNext }: { totalXp: number; level: number; levelTitle: string; xpToNext: number }) {
  const nextLevelThreshold = [0, 500, 1500, 3500, 7000, 13000, 20000][level] || 20000;
  const prevThreshold = [0, 500, 1500, 3500, 7000, 13000, 20000][level - 1] || 0;
  const progress = ((totalXp - prevThreshold) / (nextLevelThreshold - prevThreshold)) * 100;
  return (
    <div className="bg-surface rounded-xl p-4 border border-border">
      <div className="flex justify-between mb-2">
        <span className="text-sm">Level {level}: {levelTitle}</span>
        <span className="text-sm">{xpToNext} XP to next level</span>
      </div>
      <div className="w-full bg-surfaceElevated rounded-full h-2">
        <div className="bg-primary h-2 rounded-full" style={{ width: `${Math.min(100, progress)}%` }} />
      </div>
    </div>
  );
}