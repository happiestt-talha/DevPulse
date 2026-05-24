interface ProblemRingsProps {
  easy: number;
  medium: number;
  hard: number;
}

export function ProblemRings({ easy, medium, hard }: ProblemRingsProps) {
  const total = easy + medium + hard;
  const easyPct = (easy / total) * 100;
  const mediumPct = (medium / total) * 100;
  const hardPct = (hard / total) * 100;

  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-sm font-medium text-textSecondary mb-4">Problems Solved</h3>
      <div className="flex justify-center gap-6">
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-green flex items-center justify-center font-mono text-xl font-bold">
            {easy}
          </div>
          <div className="text-xs text-textSecondary mt-1">Easy</div>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-amber flex items-center justify-center font-mono text-xl font-bold">
            {medium}
          </div>
          <div className="text-xs text-textSecondary mt-1">Medium</div>
        </div>
        <div className="text-center">
          <div className="w-16 h-16 rounded-full border-4 border-red flex items-center justify-center font-mono text-xl font-bold">
            {hard}
          </div>
          <div className="text-xs text-textSecondary mt-1">Hard</div>
        </div>
      </div>
    </div>
  );
}