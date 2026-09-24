import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { resolveApiUrl } from "./api-url";

export default defineConfig(({ command, mode }) => {
  if (command === "build") {
    const env = loadEnv(mode, ".", "");
    resolveApiUrl({ configuredUrl: env.VITE_API_URL, development: false });
  }

  return { plugins: [react()] };
});
