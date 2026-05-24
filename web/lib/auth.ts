import { useAuthStore } from './store';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export const signInWithGitHub = () => {
  // Redirect to backend's GitHub OAuth endpoint
  window.location.href = `${API_BASE}/auth/github`;
};

export const handleAuthCallback = async (code: string) => {
  const res = await fetch(`${API_BASE}/auth/github/callback?code=${code}`, {
    method: 'GET',
    credentials: 'include',
  });
  const data = await res.json();
  if (data.access_token) {
    useAuthStore.getState().setAccessToken(data.access_token);
    // Fetch user profile
    const userRes = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${data.access_token}` },
    });
    const user = await userRes.json();
    useAuthStore.getState().setUser(user);
    return true;
  }
  return false;
};

export const signOut = () => {
  useAuthStore.getState().logout();
  window.location.href = '/';
};

export const getAccessToken = () => useAuthStore.getState().accessToken;