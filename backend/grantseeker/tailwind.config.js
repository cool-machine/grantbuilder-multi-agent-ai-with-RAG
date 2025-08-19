/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'custom-red': '#990000',
        'custom-red-dark': '#800000',
        'custom-blue': '#011F5B',
        'custom-blue-light': '#1a3a7a',
      }
    },
  },
  plugins: [],
};
