import { defineConfig } from 'astro/config';
import vercel from '@astrojs/vercel/serverless';
import solidJs from '@astrojs/solid-js';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  site: 'https://www.kanishkk.vercek.app',
  output: 'server',
  adapter: vercel({ analytics: true }),
  integrations: [solidJs(), tailwind()],
  vite: {
    plugins: [],
  },
});
