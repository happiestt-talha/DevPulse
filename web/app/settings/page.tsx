'use client';

import { useAuthStore } from '@/lib/store';
import { signInWithGitHub, signOut } from '@/lib/auth';
import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { Github, Clock, Brain, LogOut, CheckCircle2, XCircle, ExternalLink, User, Shield, RefreshCw, Unlink } from 'lucide-react';
import Image from 'next/image';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export default function SettingsPage() {
  const user = useAuthStore((state) => state.user);
  const accessToken = useAuthStore((state) => state.accessToken);
  const [goalHours, setGoalHours] = useState(user?.weekly_goal_hours || 20);
  const [goalProblems, setGoalProblems] = useState(user?.weekly_goal_problems || 10);
  const [leetcodeUsername, setLeetcodeUsername] = useState('');
  const [leetcodeLoading, setLeetcodeLoading] = useState(false);
  const [wakatimeLoading, setWakatimeLoading] = useState(false);
  const [disconnectLoading, setDisconnectLoading] = useState<string | null>(null);
  const [saveLoading, setSaveLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const queryClient = useQueryClient();

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 4000);
  };

  const refreshUser = async () => {
    const userRes = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    if (userRes.ok) {
      const updatedUser = await userRes.json();
      useAuthStore.getState().setUser(updatedUser);
    }
  };

  const saveGoals = async () => {
    setSaveLoading(true);
    try {
      await fetch(`${API_BASE}/user/goals`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify({ weekly_goal_hours: goalHours, weekly_goal_problems: goalProblems }),
      });
      queryClient.invalidateQueries({ queryKey: ['overview'] });
      showMessage('success', 'Goals saved successfully!');
    } catch {
      showMessage('error', 'Failed to save goals.');
    } finally {
      setSaveLoading(false);
    }
  };

  const connectWakaTime = async () => {
    setWakatimeLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/wakatime/authorize`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      if (data.authorization_url) {
        window.location.href = data.authorization_url;
      } else {
        showMessage('error', 'Could not get WakaTime authorization URL.');
      }
    } catch {
      showMessage('error', 'Failed to connect WakaTime.');
    } finally {
      setWakatimeLoading(false);
    }
  };

  const disconnectWakaTime = async () => {
    setDisconnectLoading('wakatime');
    try {
      const res = await fetch(`${API_BASE}/auth/wakatime/disconnect`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (res.ok) {
        await refreshUser();
        queryClient.invalidateQueries({ queryKey: ['wakatime'] });
        showMessage('success', 'WakaTime disconnected.');
      } else {
        showMessage('error', 'Failed to disconnect WakaTime.');
      }
    } catch {
      showMessage('error', 'Failed to disconnect WakaTime.');
    } finally {
      setDisconnectLoading(null);
    }
  };

  const connectLeetCode = async () => {
    if (!leetcodeUsername.trim()) {
      showMessage('error', 'Please enter your LeetCode username.');
      return;
    }
    setLeetcodeLoading(true);
    try {
      const res = await fetch(`${API_BASE}/auth/leetcode/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${accessToken}` },
        body: JSON.stringify({ username: leetcodeUsername.trim() }),
      });
      const data = await res.json();
      if (res.ok) {
        showMessage('success', `LeetCode connected as "${data.username}"!`);
        await refreshUser();
        queryClient.invalidateQueries({ queryKey: ['leetcode'] });
        setLeetcodeUsername('');
      } else {
        showMessage('error', data.detail || 'Failed to connect LeetCode.');
      }
    } catch {
      showMessage('error', 'Failed to connect LeetCode.');
    } finally {
      setLeetcodeLoading(false);
    }
  };

  const disconnectLeetCode = async () => {
    setDisconnectLoading('leetcode');
    try {
      const res = await fetch(`${API_BASE}/auth/leetcode/disconnect`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (res.ok) {
        await refreshUser();
        queryClient.invalidateQueries({ queryKey: ['leetcode'] });
        showMessage('success', 'LeetCode disconnected.');
      } else {
        showMessage('error', 'Failed to disconnect LeetCode.');
      }
    } catch {
      showMessage('error', 'Failed to disconnect LeetCode.');
    } finally {
      setDisconnectLoading(null);
    }
  };

  return (
    <div className="max-w-2xl space-y-8">
      <h1 className="text-2xl font-bold">Settings</h1>

      {/* Toast message */}
      {message && (
        <div className={`rounded-lg px-4 py-3 text-sm flex items-center gap-2 ${message.type === 'success' ? 'bg-green/10 text-green border border-green/30' : 'bg-red/10 text-red border border-red/30'}`}>
          {message.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
          {message.text}
        </div>
      )}

      {/* Account Section */}
      <div className="bg-surface rounded-xl border border-border p-6 space-y-4">
        <div className="flex items-center gap-2 mb-2">
          <User className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold">Account</h2>
        </div>
        <div className="flex items-center gap-4">
          {user?.avatar_url && (
            <Image src={user.avatar_url} alt="avatar" width={48} height={48} className="rounded-full" />
          )}
          <div>
            <p className="font-medium">{user?.display_name || user?.github_username}</p>
            <p className="text-sm text-textSecondary">{user?.email || 'No email'}</p>
          </div>
        </div>
        <div className="pt-2 border-t border-border flex flex-wrap gap-3">
          <button
            onClick={() => {
              signOut();
              // After sign out, user can sign in with a different GitHub account
            }}
            className="flex items-center gap-2 px-4 py-2 text-sm bg-red/10 text-red border border-red/30 rounded-lg hover:bg-red/20 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
          <button
            onClick={signInWithGitHub}
            className="flex items-center gap-2 px-4 py-2 text-sm bg-primary/10 text-primary border border-primary/30 rounded-lg hover:bg-primary/20 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Switch GitHub Account
          </button>
        </div>
        <p className="text-xs text-textSecondary">To switch GitHub accounts, click "Switch GitHub Account" to re-authenticate with a different GitHub profile.</p>
      </div>

      {/* Integrations Section */}
      <div className="bg-surface rounded-xl border border-border p-6 space-y-6">
        <div className="flex items-center gap-2 mb-2">
          <Shield className="w-5 h-5 text-primary" />
          <h2 className="text-xl font-semibold">Connected Integrations</h2>
        </div>

        {/* GitHub - always connected (signed in via GitHub) */}
        <div className="flex items-center justify-between p-4 bg-surfaceElevated rounded-lg">
          <div className="flex items-center gap-3">
            <Github className="w-6 h-6 text-textPrimary" />
            <div>
              <p className="font-medium">GitHub</p>
              <p className="text-xs text-textSecondary">Commits, PRs, contributions</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-green" />
            <span className="text-sm text-green font-medium">{user?.github_username}</span>
          </div>
        </div>

        {/* WakaTime */}
        <div className="p-4 bg-surfaceElevated rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Clock className="w-6 h-6 text-cyan" />
              <div>
                <p className="font-medium">WakaTime</p>
                <p className="text-xs text-textSecondary">Coding time, languages, projects</p>
              </div>
            </div>
            {user?.wakatime_connected ? (
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green" />
                <span className="text-sm text-green font-medium">Connected</span>
              </div>
            ) : (
              <XCircle className="w-5 h-5 text-textSecondary" />
            )}
          </div>
          <div className="flex gap-2">
            {user?.wakatime_connected ? (
              <>
                <button
                  onClick={connectWakaTime}
                  disabled={wakatimeLoading}
                  className="flex items-center gap-2 px-4 py-2 text-sm bg-cyan/10 text-cyan border border-cyan/30 rounded-lg hover:bg-cyan/20 transition-colors disabled:opacity-50"
                >
                  <RefreshCw className="w-4 h-4" />
                  {wakatimeLoading ? 'Reconnecting...' : 'Reconnect'}
                </button>
                <button
                  onClick={disconnectWakaTime}
                  disabled={disconnectLoading === 'wakatime'}
                  className="flex items-center gap-2 px-4 py-2 text-sm bg-red/10 text-red border border-red/30 rounded-lg hover:bg-red/20 transition-colors disabled:opacity-50"
                >
                  <Unlink className="w-4 h-4" />
                  {disconnectLoading === 'wakatime' ? 'Disconnecting...' : 'Disconnect'}
                </button>
              </>
            ) : (
              <button
                onClick={connectWakaTime}
                disabled={wakatimeLoading}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-cyan/10 text-cyan border border-cyan/30 rounded-lg hover:bg-cyan/20 transition-colors disabled:opacity-50"
              >
                <ExternalLink className="w-4 h-4" />
                {wakatimeLoading ? 'Connecting...' : 'Connect WakaTime'}
              </button>
            )}
          </div>
        </div>

        {/* LeetCode */}
        <div className="p-4 bg-surfaceElevated rounded-lg space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Brain className="w-6 h-6 text-amber" />
              <div>
                <p className="font-medium">LeetCode</p>
                <p className="text-xs text-textSecondary">Problems solved, ranking, streaks</p>
              </div>
            </div>
            {user?.leetcode_connected ? (
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green" />
                <span className="text-sm text-green font-medium">{user?.leetcode_username || 'Connected'}</span>
              </div>
            ) : (
              <XCircle className="w-5 h-5 text-textSecondary" />
            )}
          </div>
          {user?.leetcode_connected ? (
            <div className="flex gap-2">
              <button
                onClick={() => {
                  // To change account, disconnect first then show input
                  disconnectLeetCode();
                }}
                disabled={disconnectLoading === 'leetcode'}
                className="flex items-center gap-2 px-4 py-2 text-sm bg-red/10 text-red border border-red/30 rounded-lg hover:bg-red/20 transition-colors disabled:opacity-50"
              >
                <Unlink className="w-4 h-4" />
                {disconnectLoading === 'leetcode' ? 'Disconnecting...' : 'Disconnect'}
              </button>
            </div>
          ) : (
            <div className="flex gap-2">
              <input
                type="text"
                value={leetcodeUsername}
                onChange={(e) => setLeetcodeUsername(e.target.value)}
                placeholder="Enter your LeetCode username"
                className="flex-1 bg-surface border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-primary/50 transition-colors"
                onKeyDown={(e) => e.key === 'Enter' && connectLeetCode()}
              />
              <button
                onClick={connectLeetCode}
                disabled={leetcodeLoading}
                className="px-4 py-2 text-sm bg-amber/10 text-amber border border-amber/30 rounded-lg hover:bg-amber/20 transition-colors disabled:opacity-50"
              >
                {leetcodeLoading ? 'Connecting...' : 'Connect'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Weekly Goals Section */}
      <div className="bg-surface rounded-xl border border-border p-6 space-y-6">
        <h2 className="text-xl font-semibold">Weekly Goals</h2>
        <div>
          <label className="block text-sm font-medium mb-2 text-textSecondary">Coding Goal (hours/week)</label>
          <input
            type="number"
            value={goalHours}
            onChange={(e) => setGoalHours(Number(e.target.value))}
            min={1}
            max={168}
            className="w-full bg-surfaceElevated border border-border rounded-lg px-4 py-2 focus:outline-none focus:border-primary/50 transition-colors"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-2 text-textSecondary">Problems Goal (problems/week)</label>
          <input
            type="number"
            value={goalProblems}
            onChange={(e) => setGoalProblems(Number(e.target.value))}
            min={1}
            max={100}
            className="w-full bg-surfaceElevated border border-border rounded-lg px-4 py-2 focus:outline-none focus:border-primary/50 transition-colors"
          />
        </div>
        <button
          onClick={saveGoals}
          disabled={saveLoading}
          className="bg-primary hover:bg-primary/90 px-6 py-2 rounded-lg text-white font-medium transition-colors disabled:opacity-50"
        >
          {saveLoading ? 'Saving...' : 'Save Goals'}
        </button>
      </div>
    </div>
  );
}