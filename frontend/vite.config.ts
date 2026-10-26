import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"
import path from "path"

// GitHub Pages deployment: base is repo name
const BASE = process.env.VITE_BASE || "/hireloop/"

export default defineConfig({
  plugins: [react()],
  base: BASE,
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: process.env.VITE_API_URL || "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
})
