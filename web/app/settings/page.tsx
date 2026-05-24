'use client';

import { useAuthStore } from '@/lib/store';
import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';

export default function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const [goalHours, setGoalHours] = useState(user?.weekly_goal_hours || 20);
  const [goalProblems, setGoalProblems] = useState(user?.weekly_goal_problems || 10);
  const queryClient = useQueryClient();

  const saveGoals = async () => {
    // POST to backend endpoint (not implemented yet in Phase 4 spec, but kept for completeness)
    await fetch('/api/v1/user/goals', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${useAuthStore.getState().accessToken}` },
      body: JSON.stringify({ weekly_goal_hours: goalHours, weekly_goal_problems: goalProblems }),
    });
    queryClient.invalidateQueries({ queryKey: ['overview'] });
  };

  return (
    <div className="max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div className="bg-surface rounded-xl border border-border p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium mb-2">Weekly Coding Goal (hours)</label>
          <input type="number" value={goalHours} onChange={(e) => setGoalHours(Number(e.target.value))} className="w-full bg-surfaceElevated border border-border rounded-lg px-4 py-2" />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2">Weekly Problems Goal</label>
          <input type="number" value={goalProblems} onChange={(e) => setGoalProblems(Number(e.target.value))} className="w-full bg-surfaceElevated border border-border rounded-lg px-4 py-2" />
        </div>
        <button onClick={saveGoals} className="bg-primary px-4 py-2 rounded-lg">Save Goals</button>
      </div>
      <div className="bg-surface rounded-xl border border-border p-6">
        <h2 className="text-xl font-semibold mb-4">Connected Integrations</h2>
        <div className="space-y-2">
          <p>GitHub: {user?.github_username ? '✓ Connected' : '✗ Not connected'}</p>
          <p>WakaTime: {user?.wakatime_connected ? '✓ Connected' : '✗ Not connected'}</p>
          <p>LeetCode: {user?.leetcode_connected ? '✓ Connected' : '✗ Not connected'}</p>
        </div>
      </div>
    </div>
  );
}