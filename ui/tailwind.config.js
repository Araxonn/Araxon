/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        arx: {
          bg: '#080B14',
          sidebar: '#0A0D16',
          card: '#0D1220',
          input: '#111827',
          border: '#1E293B',
          blue: '#3B82F6',
          cyan: '#06B6D4',
          green: '#10B981',
          purple: '#8B5CF6',
          orange: '#F59E0B',
          orb: '#1D4ED8',
          muted: '#475569',
          secondary: '#94A3B8',
          text: '#F1F5F9',
          red: '#EF4444',
          active: 'rgba(59,130,246,0.15)',
        }
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
