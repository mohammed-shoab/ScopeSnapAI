import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // ScopeSnap brand colors (from prototype)
        brand: {
          green: "#1a8754",
          "green-light": "#e8f5ee",
          "green-dark": "#0f5c38",
          orange: "#c4600a",
          "orange-light": "#fef3e8",
          blue: "#1565c0",
          "blue-light": "#e3f0fd",
          red: "#c62828",
          "red-light": "#fce8e8",
          purple: "#6a1b9a",
          "purple-light": "#f3e8f9",
          gold: "#e6a817",
          "gold-light": "#fdf6e0",
        },
        surface: {
          bg: "#f7f7f3",
          card: "#ffffff",
          secondary: "#f0efea",
          border: "#e2dfd7",
        },
        text: {
          primary: "#1a1a18",
          secondary: "#7a7770",
          tertiary: "#a8a49c",
        },
        sidebar: {
          bg: "#1a1a18",
          hover: "rgba(255,255,255,.06)",
          active: "rgba(26,135,84,.2)",
          text: "rgba(255,255,255,.55)",
          "text-hover": "rgba(255,255,255,.85)",
          section: "rgba(255,255,255,.25)",
          divider: "rgba(255,255,255,.08)",
        },
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "monospace"],
      },
      borderRadius: {
        "ss": "14px",
        "ss-sm": "10px",
      },
      boxShadow: {
        "ss": "0 1px 3px rgba(0,0,0,.04), 0 4px 12px rgba(0,0,0,.03)",
        "ss-lg": "0 4px 20px rgba(0,0,0,.06)",
        "green": "0 4px 16px rgba(26,135,84,.25)",
      },
    },
  },
  plugins: [],
};

export default config;
