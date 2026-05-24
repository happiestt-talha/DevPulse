interface PRReviewCardProps {
  reviewsGiven: number;
  reviewsReceived: number;
}

export function PRReviewCard({ reviewsGiven, reviewsReceived }: PRReviewCardProps) {
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="text-sm font-medium text-textSecondary mb-2">PR Review Activity</h3>
      <div className="flex justify-between items-center">
        <div>
          <div className="font-mono text-2xl font-bold text-primary">{reviewsGiven}</div>
          <div className="text-xs text-textSecondary">Reviews given</div>
        </div>
        <div>
          <div className="font-mono text-2xl font-bold text-cyan">{reviewsReceived}</div>
          <div className="text-xs text-textSecondary">Reviews received</div>
        </div>
      </div>
    </div>
  );
}