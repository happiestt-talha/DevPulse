import { NextRequest, NextResponse } from 'next/server';
import { handleAuthCallback } from '@/lib/auth';

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get('code');
  if (!code) {
    return NextResponse.redirect(new URL('/?error=missing_code', request.url));
  }
  const success = await handleAuthCallback(code);
  if (success) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  return NextResponse.redirect(new URL('/?error=auth_failed', request.url));
}