'use client';

import { useChallenges } from '@/lib/api';
import { ChallengeCard } from '@/components/gamification/ChallengeCard';

export default function ChallengesPage() {
  const { data, isLoading } = useChallenges();
  if (isLoading) return <div>Loading challenges...</div>;
  if (!data) return <div>No challenges</div>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Weekly Challenges</h1>
      <div className="grid gap-4">
        {data.challenges.map((challenge) => (
          <ChallengeCard key={challenge.id} challenge={challenge} />
        ))}
      </div>
    </div>
  );
}