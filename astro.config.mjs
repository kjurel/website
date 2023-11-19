import mdx from "@astrojs/mdx";
import prefetch from "@astrojs/prefetch";
import solidJs from "@astrojs/solid-js";
import vercel from "@astrojs/vercel/serverless";
import unocss from "unocss/astro";
import { presetAttributify, presetIcons, presetUno, transformerDirectives, transformerVariantGroup } from "unocss";

import { presetDaisy } from "unocss-preset-daisy";
import { presetHeadlessUi } from "unocss-preset-primitives";

import { ValidateEnv } from "vite-plugin-validate-env";
// import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "astro/config";
// https://astro.build/config
export default defineConfig({
  site: "https://www.kanishkk.vercel.app",
  output: "server",
  adapter: vercel({
    webAnalytics: {
      enabled: true,
    },
    speedInsights: {
      enabled: true,
    },
    imageService: true,
    functionPerRoute: false,
  }),
  integrations: [
    mdx({
      syntaxHighlight: "shiki",
      shikiConfig: { theme: "dracula" },
      remarkRehype: { footnoteLabel: "Footnotes" },
      gfm: false,
    }),
    unocss({
      injectReset: true,

      shortcuts: [{ "i-logo": "i-logos-astro w-6em h-6em transform transition-800" }],
      presets: [
        presetUno({
          content: ["./src/**/*.{astro,html,svelte,vue,js,ts,jsx,tsx}"],
        }),
        presetIcons({
          extraProperties: {
            display: "inline-block",
            "vertical-align": "middle",
          },
        }),
        presetAttributify(),
        presetDaisy({
          themes: false, // true: all themes | false: only light + dark | array: specific themes like this ["light", "dark", "cupcake"]
          darkTheme: "dark", // name of one of the included themes for dark mode
          base: true, // applies background color and foreground color for root element by default
          styled: true, // include daisyUI colors and design decisions for all components
          utils: true, // adds responsive and modifier utility classes
          rtl: false, // rotate style direction from left-to-right to right-to-left. You also need to add dir="rtl" to your html tag and install `tailwindcss-flip` plugin for Tailwind CSS.
          prefix: "", // prefix for daisyUI classnames (components, modifiers and responsive class names. Not colors)
          logs: true, // Shows info about daisyUI version and used config in the console when building your CSS
        }),
        presetHeadlessUi(),
      ],
      transformers: [transformerDirectives(), transformerVariantGroup()],
    }),
    prefetch({
      // Allow up to three links to be prefetched concurrently
      throttle: 3,
    }),
    solidJs(),
  ],
  vite: {
    // plugins: [ValidateEnv()],
  },
});
