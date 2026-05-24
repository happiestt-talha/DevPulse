'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = searchParams.get('access_token');

    if (!accessToken) {
      setError('Missing access token');
      return;
    }

    // Store the token and fetch user profile
    const completeAuth = async () => {
      try {
        useAuthStore.getState().setAccessToken(accessToken);

        const userRes = await fetch(`${API_BASE}/auth/me`, {
          headers: { Authorization: `Bearer ${accessToken}` },
        });

        if (!userRes.ok) {
          throw new Error('Failed to fetch user profile');
        }

        const user = await userRes.json();
        useAuthStore.getState().setUser(user);

        router.replace('/dashboard');
      } catch (err) {
        console.error('Auth callback error:', err);
        setError('Authentication failed. Please try again.');
      }
    };

    completeAuth();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <p className="text-red text-lg mb-4">{error}</p>
          <a href="/" className="text-primary hover:underline">
            Back to home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-textSecondary">Completing sign in...</p>
      </div>
    </div>
  );
}
