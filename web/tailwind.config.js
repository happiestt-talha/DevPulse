/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#0F0A2E',
        surface: '#1E1B4B',
        surfaceElevated: '#2D2A63',
        border: '#3B3980',
        primary: '#7C3AED',
        primaryLight: '#A78BFA',
        cyan: '#06B6D4',
        amber: '#F59E0B',
        green: '#10B981',
        red: '#EF4444',
        textPrimary: '#F1F5F9',
        textSecondary: '#94A3B8',
        xpGold: '#FBBF24',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};