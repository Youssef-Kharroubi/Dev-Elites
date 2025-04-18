/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        dark: "#0a0a0a",
        light: "#f7f8f8",
        content: "#8a8f98",
      },
    },
    container: {
      center: true,
      padding: "24px",
    }
  },
  plugins: [],
};