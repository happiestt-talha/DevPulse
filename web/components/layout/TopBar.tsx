'use client';

import { useAuthStore } from '@/lib/store';
import { signOut } from '@/lib/auth';
import { LevelBadge } from '@/components/gamification/LevelBadge';
import { StreakCounter } from '@/components/stats/StreakCounter';
import { LogOut, User } from 'lucide-react';
import Image from 'next/image';

export function TopBar() {
  const user = useAuthStore((state) => state.user);
  const streakCurrent = user?.streak_current || 0;

  return (
    <header className="h-16 border-b border-border bg-surface/50 backdrop-blur-sm px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        {user && <LevelBadge level={user.level} totalXp={user.total_xp} />}
        {user && <StreakCounter streak={streakCurrent} />}
      </div>
      <div className="flex items-center gap-4">
        {user?.avatar_url && (
          <Image src={user.avatar_url} alt="avatar" width={32} height={32} className="rounded-full" />
        )}
        <span className="text-sm text-textSecondary">{user?.github_username}</span>
        <button onClick={signOut} className="p-2 hover:bg-surfaceElevated rounded-lg transition">
          <LogOut className="w-5 h-5 text-textSecondary" />
        </button>
      </div>
    </header>
  );
}