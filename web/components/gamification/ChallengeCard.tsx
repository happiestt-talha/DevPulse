export function ChallengeCard({ challenge }: { challenge: any }) {
  const progress = (challenge.current_value / challenge.target_value) * 100;
  return (
    <div className="bg-surface rounded-xl border border-border p-4">
      <h3 className="font-semibold">{challenge.title}</h3>
      <p className="text-sm text-textSecondary">{challenge.description}</p>
      <div className="mt-2 flex justify-between text-sm">
        <span>Progress: {challenge.current_value} / {challenge.target_value}</span>
        <span>Reward: {challenge.xp_reward} XP + {challenge.freeze_reward} streak freeze</span>
      </div>
      <div className="w-full bg-surfaceElevated rounded-full h-2 mt-2">
        <div className="bg-primary h-2 rounded-full" style={{ width: `${progress}%` }} />
      </div>
    </div>
  );
}