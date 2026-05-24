import axios from 'axios';
import { useAuthStore } from './store';
import { useQuery, useMutation, UseQueryOptions } from '@tanstack/react-query';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().accessToken;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ----- Types -----
export interface GitHubStats {
  total_commits: number;
  total_prs_merged: number;
  total_issues_closed: number;
  total_stars_earned: number;
  top_languages: Array<{ language: string; percent: number }>;
  commits_30d: number;
  prs_merged_30d: number;
  reviews_given_30d: number;
  active_repos_30d: number;
  contribution_data: Array<{ date: string; count: number }>;
  synced_at: string;
}

export interface WakaTimeStats {
  total_seconds: number;
  today_seconds: number;
  week_seconds: number;
  languages: Array<{ name: string; percent: number }>;
  projects: Array<{ name: string; hours: number }>;
  editors: Array<{ name: string; percent: number }>;
  daily_breakdown: Array<{ date: string; seconds: number }>;
  best_day_seconds: number;
  best_day_date: string | null;
  synced_at: string;
}

export interface LeetCodeStats {
  total_solved: number;
  easy_solved: number;
  medium_solved: number;
  hard_solved: number;
  acceptance_rate: number;
  total_submissions: number;
  ranking: number;
  ranking_percentile: number;
  recent_submissions: Array<{ title: string; status: string; timestamp: number; lang: string }>;
  contest_rating: number;
  synced_at: string;
}

export interface Overview {
  developer_score: number;
  streak_current: number;
  streak_longest: number;
  level: number;
  total_xp: number;
  weekly_goal_hours: number;
  weekly_goal_problems: number;
  today: {
    commits: number;
    coding_minutes: number;
    problems_solved: number;
  };
}

export interface Badge {
  id: string;
  slug: string;
  name: string;
  description: string;
  xp_reward: number;
  color: string;
  category: string;
  earned: boolean;
  earned_at?: string;
  progress: number;
}

export interface XPInfo {
  total_xp: number;
  level: number;
  level_title: string;
  xp_to_next_level: number;
  recent_events: Array<{ source: string; amount: number; description: string; created_at: string }>;
}

export interface Challenge {
  id: string;
  title: string;
  description: string;
  target_metric: string;
  target_value: number;
  xp_reward: number;
  freeze_reward: number;
  current_value: number;
  completed: boolean;
}

// ----- API functions -----
export const fetchOverview = async (): Promise<Overview> => {
  const res = await api.get('/dashboard/overview');
  return res.data;
};

export const fetchGitHubStats = async (): Promise<GitHubStats> => {
  const res = await api.get('/dashboard/github');
  return res.data;
};

export const fetchWakaTimeStats = async (): Promise<WakaTimeStats> => {
  const res = await api.get('/dashboard/wakatime');
  return res.data;
};

export const fetchLeetCodeStats = async (): Promise<LeetCodeStats> => {
  const res = await api.get('/dashboard/leetcode');
  return res.data;
};

export const fetchBadges = async (): Promise<{ badges: Badge[] }> => {
  const res = await api.get('/gamification/badges');
  return res.data;
};

export const fetchXP = async (): Promise<XPInfo> => {
  const res = await api.get('/gamification/xp');
  return res.data;
};

export const fetchChallenges = async (): Promise<{ challenges: Challenge[] }> => {
  const res = await api.get('/gamification/challenges');
  return res.data;
};

export const useOverview = () => useQuery({ queryKey: ['overview'], queryFn: fetchOverview, retry: 1 });
export const useGitHubStats = () => useQuery({ queryKey: ['github'], queryFn: fetchGitHubStats, retry: 1 });
export const useWakaTimeStats = () => useQuery({ queryKey: ['wakatime'], queryFn: fetchWakaTimeStats, retry: 1 });
export const useLeetCodeStats = () => useQuery({ queryKey: ['leetcode'], queryFn: fetchLeetCodeStats, retry: 1 });
export const useBadges = () => useQuery({ queryKey: ['badges'], queryFn: fetchBadges, retry: 1 });
export const useXP = () => useQuery({ queryKey: ['xp'], queryFn: fetchXP, retry: 1 });
export const useChallenges = () => useQuery({ queryKey: ['challenges'], queryFn: fetchChallenges, retry: 1 });