/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        arx: {
          bg: '#05070a',
          sidebar: '#080b12',
          card: '#0c1019',
          'card-hover': '#111827',
          input: '#0f1419',
          border: '#1a2332',
          'border-glow': 'rgba(59,130,246,0.25)',
          blue: '#3B82F6',
          'blue-bright': '#60A5FA',
          cyan: '#06B6D4',
          'cyan-bright': '#22D3EE',
          green: '#10B981',
          purple: '#8B5CF6',
          orange: '#F59E0B',
          orb: '#1D4ED8',
          muted: '#64748B',
          secondary: '#94A3B8',
          text: '#F1F5F9',
          red: '#EF4444',
          active: 'rgba(59,130,246,0.12)',
          glow: 'rgba(59,130,246,0.35)',
        },
      },
      width: {
        72: '18rem',
        80: '20rem',
        88: '22rem',
        96: '24rem',
        300: '300px',
        360: '360px',
        420: '420px',
        600: '600px',
      },
      boxShadow: {
        'arx-glow': '0 0 20px rgba(59,130,246,0.35), 0 0 60px rgba(59,130,246,0.15)',
        'arx-glow-sm': '0 0 12px rgba(59,130,246,0.3)',
        'arx-glow-lg': '0 0 30px rgba(59,130,246,0.4), 0 0 80px rgba(59,130,246,0.2)',
        'arx-inner': 'inset 0 0 20px rgba(59,130,246,0.15)',
      },
      backgroundImage: {
        'arx-radial':
          'radial-gradient(ellipse at center, rgba(59,130,246,0.08) 0%, transparent 70%)',
        'arx-grid':
          'linear-gradient(rgba(59,130,246,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.03) 1px, transparent 1px)',
      },
      backgroundSize: {
        grid: '32px 32px',
      },
      animation: {
        'pulse-glow': 'pulse-glow 2s ease-in-out infinite',
        'spin-slow': 'spin 8s linear infinite',
        'wave': 'wave 1.5s ease-in-out infinite',
      },
      keyframes: {
        'pulse-glow': {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '1', transform: 'scale(1.02)' },
        },
        wave: {
          '0%, 100%': { transform: 'scaleY(0.4)' },
          '50%': { transform: 'scaleY(1)' },
        },
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
    },
  },
  plugins: [],
}
