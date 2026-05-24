'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Github, Clock, Brain, Award, Calendar, Settings } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Overview', href: '/dashboard', icon: LayoutDashboard },
  { name: 'GitHub', href: '/dashboard/github', icon: Github },
  { name: 'WakaTime', href: '/dashboard/wakatime', icon: Clock },
  { name: 'LeetCode', href: '/dashboard/leetcode', icon: Brain },
  { name: 'Badges', href: '/badges', icon: Award },
  { name: 'Challenges', href: '/challenges', icon: Calendar },
  { name: 'Settings', href: '/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-surface border-r border-border flex flex-col">
      <div className="p-6 border-b border-border">
        <h1 className="text-2xl font-mono font-bold text-primary">DevPulse</h1>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname?.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-2 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary/20 text-primary border-l-2 border-primary'
                  : 'text-textSecondary hover:bg-surfaceElevated hover:text-textPrimary'
              )}
            >
              <item.icon className="w-5 h-5" />
              <span>{item.name}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}