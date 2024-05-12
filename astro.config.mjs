// import { ValidateEnv } from "vite-plugin-validate-env";
import vercel from "@astrojs/vercel/serverless";
import { defineConfig } from "astro/config";
import solidJs from "@astrojs/solid-js";

import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  site: "https://www.kanishkk.vercel.app",
  output: "server",
  adapter: vercel({
    webAnalytics: { enabled: true },
    speedInsights: { enabled: true },
    imageService: true,
    functionPerRoute: false,
  }),
  vite: {
    build: { external: ["xlsx"] },
    // plugins: [ValidateEnv()],
  },
  integrations: [solidJs(), tailwind()],
});
