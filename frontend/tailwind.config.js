/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#3b82f6",
        accent: "#10b981",
        warning: "#f59e0b",
      },
    },
  },
  plugins: [],
};
