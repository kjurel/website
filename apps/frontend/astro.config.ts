import { defineConfig } from "astro/config";
import vercel from "@astrojs/vercel/serverless";
import solidJs from "@astrojs/solid-js";
import tailwind from "@astrojs/tailwind";
import tsconfigPaths from "vite-tsconfig-paths";
import { ValidateEnv } from "@julr/vite-plugin-validate-env";
import { qrcode } from "vite-plugin-qrcode";

// https://astro.build/config
export default defineConfig({
  site: "https://www.kanishkk.vercek.app",
  output: "server",
  adapter: vercel({ analytics: true }),
  integrations: [solidJs(), tailwind()],
  vite: {
    plugins: [tsconfigPaths(), ValidateEnv(), qrcode()],
  },
});
