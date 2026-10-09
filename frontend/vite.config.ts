import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { "@": path.resolve(__dirname, "./src") },
  },
  server: {
    port: 5173,
    host: true,
    watch: { usePolling: true },
    proxy: {
      "/api": {
        // Inside docker-compose, the FastAPI service is reachable at `backend`.
        // Override with VITE_API_TARGET=http://localhost:8000 for local dev.
        target: process.env.VITE_API_TARGET ?? "http://backend:8000",
        changeOrigin: true,
      },
    },
  },
});
