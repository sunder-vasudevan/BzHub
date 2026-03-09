import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#6D28D9",
        "primary-dark": "#5B21B6",
        accent: "#22D3EE",
        surface: "#F5F6FA",
      },
    },
  },
  plugins: [],
  darkMode: "class",
};
export default config;
