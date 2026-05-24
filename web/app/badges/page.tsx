'use client';

import { useBadges, useXP } from '@/lib/api';
import { BadgeCard } from '@/components/gamification/BadgeCard';
import { XPBar } from '@/components/gamification/XPBar';

export default function BadgesPage() {
  const { data: badgesData, isLoading: badgesLoading } = useBadges();
  const { data: xpData, isLoading: xpLoading } = useXP();

  if (badgesLoading || xpLoading) return <div>Loading badges...</div>;
  if (!badgesData || !xpData) return <div>Error loading gamification data</div>;

  return (
    <div className="space-y-8">
      <div>
        <XPBar totalXp={xpData.total_xp} level={xpData.level} levelTitle={xpData.level_title} xpToNext={xpData.xp_to_next_level} />
      </div>
      <div>
        <h2 className="text-2xl font-bold mb-4">Your Badges</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
          {badgesData.badges.map((badge) => (
            <BadgeCard key={badge.id} badge={badge} />
          ))}
        </div>
      </div>
    </div>
  );
}