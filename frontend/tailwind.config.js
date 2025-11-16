/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'jellyseerr-dark': '#0F0F14',
        'jellyseerr-card': '#1A1D29',
        'download-progress': '#f97316',
        'queue-progress': '#3b82f6',
        'complete-progress': '#22c55e',
        'failed-progress': '#ef4444',
      },
      keyframes: {
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      animation: {
        shimmer: 'shimmer 2s infinite',
      },
    },
  },
  plugins: [],
}
