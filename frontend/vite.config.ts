/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ command }) => ({
  // Built assets are collected by Django's collectstatic and served by
  // WhiteNoise under STATIC_URL ("static/"). Without this, index.html
  // references root-relative paths like /assets/*.js that never reach
  // WhiteNoise and instead get swallowed by the SPA catch-all route,
  // which serves index.html back for every unmatched path. Scoped to
  // `build` only so the local dev server still runs at the site root.
  base: command === "build" ? "/static/" : "/",
  plugins: [react(), tailwindcss()],
  server: {
    host: true,
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    globals: true,
  },
}));
