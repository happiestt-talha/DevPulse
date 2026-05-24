'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/lib/store';

const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export default function WakaTimeCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const accessToken = useAuthStore.getState().accessToken;

    if (!code) {
      setError('Missing authorization code');
      return;
    }

    if (!accessToken) {
      setError('You must be logged in to connect WakaTime.');
      return;
    }

    const connectWakaTime = async () => {
      try {
        const res = await fetch(`${API_BASE}/auth/wakatime/connect`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({ code }),
        });

        if (res.ok) {
          // Refresh user data
          const userRes = await fetch(`${API_BASE}/auth/me`, {
            headers: { Authorization: `Bearer ${accessToken}` },
          });
          if (userRes.ok) {
            const updatedUser = await userRes.json();
            useAuthStore.getState().setUser(updatedUser);
          }
          router.replace('/settings');
        } else {
          const data = await res.json();
          setError(data.detail || 'Failed to connect WakaTime.');
        }
      } catch (err) {
        console.error('WakaTime callback error:', err);
        setError('Failed to connect WakaTime. Please try again.');
      }
    };

    connectWakaTime();
  }, [searchParams, router]);

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <p className="text-red text-lg mb-4">{error}</p>
          <a href="/settings" className="text-primary hover:underline">
            Back to Settings
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="animate-spin w-8 h-8 border-4 border-cyan border-t-transparent rounded-full mx-auto mb-4" />
        <p className="text-textSecondary">Connecting WakaTime...</p>
      </div>
    </div>
  );
}
