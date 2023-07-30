import { defineConfig } from 'astro/config';
// import vercel from '@astrojs/vercel/serverless';
import solidJs from '@astrojs/solid-js';
import unocss from '@unocss/astro';
import presetWind from '@unocss/preset-wind';

// import purgecss from 'astro-purgecss';

// https://astro.build/config
export default defineConfig({
  site: 'https://www.kanishkk.vercek.app',
  // outDir: './dist',
  // output: 'server',
  // adapter: vercel({ analytics: true }),
  integrations: [
    solidJs(),
    unocss({
      presets: [
        presetWind(),
        /* more presets */
      ],
    }),
    // purgecss(),
  ],
  vite: {
    plugins: [],
  },
});
