# things to add

- [x] supabase
- [ ] trpc
- [ ] axiom
- [ ] upstash

![Vercel deployments](https://img.shields.io/github/deployments/tokcide/website/production?label=vercel&logo=vercel&style=for-the-badge)

[![Netlify Status](https://api.netlify.com/api/v1/badges/dc211944-a755-4690-868f-f1549254266a/deploy-status)](https://app.netlify.com/sites/tokcide/deploys)

[![pnpm](https://img.shields.io/badge/pnpm-docs-informational?style=flat-square&logo=pnpm)](https://pnpm.io/pnpm-cli)
[![vite](https://img.shields.io/badge/vite-docs-informational?style=flat-square&logo=vite)](https://vitejs.dev/guide/)
[![astro](https://img.shields.io/badge/astro-docs-informational?style=flat-square&logo=astro)](https://docs.astro.build/en/core-concepts/astro-syntax/)
[![trpc](https://img.shields.io/badge/trpc-docs-informational?style=flat-square&logo=trpc)](https://trpc.io/docs)
[![solid](https://img.shields.io/badge/solid-docs-informational?style=flat-square&logo=solid)](https://www.solidjs.com/docs/latest)
[![supabase](https://img.shields.io/badge/supabase-docs-informational?style=flat-square&logo=supabase)](https://supabase.com/docs)
[![netlify](https://img.shields.io/badge/netlify-docs-informational?style=flat-square&logo=netlify)](https://app.netlify.com/)
[![zod](https://img.shields.io/badge/zod-docs-informational?style=flat-square&logo=zod)](https://zod.dev/)
[![nanostores](https://img.shields.io/badge/nanostores-docs-informational?style=flat-square&logo=nanostores)](https://zod.dev/)

[![nanostores](https://img.shields.io/github/stars/nanostores/nanostores?label=nanostores&logo=github&logoColor=black&style=social)](https://github.com/nanostores/nanostores)

[![simple-icons](https://img.shields.io/github/stars/simple-icons/simple-icons?label=simple-icons&style=for-the-badge)](https://github.com/simple-icons/simple-icons/blob/develop/slugs.md)

# Starter Kit: Basics

```
npm create astro@latest -- --template basics
```

[![Open in StackBlitz](https://developer.stackblitz.com/img/open_in_stackblitz.svg)](https://stackblitz.com/github/withastro/astro/tree/latest/examples/basics)
[![Open with CodeSandbox](https://assets.codesandbox.io/github/button-edit-lime.svg)](https://codesandbox.io/p/sandbox/github/withastro/astro/tree/latest/examples/basics)
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/withastro/astro?devcontainer_path=.devcontainer/basics/devcontainer.json)

> 🧑‍🚀 **Seasoned astronaut?** Delete this file. Have fun!

![basics](https://user-images.githubusercontent.com/4677417/186188965-73453154-fdec-4d6b-9c34-cb35c248ae5b.png)

## 🚀 Project Structure

Inside of your Astro project, you'll see the following folders and files:

```
/
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   └── Card.astro
│   ├── layouts/
│   │   └── Layout.astro
│   └── pages/
│       └── index.astro
└── package.json
```

Astro looks for `.astro` or `.md` files in the `src/pages/` directory. Each page is exposed as a route based on its file name.

There's nothing special about `src/components/`, but that's where we like to put any Astro/React/Vue/Svelte/Preact components.

Any static assets, like images, can be placed in the `public/` directory.

## 🧞 Commands

All commands are run from the root of the project, from a terminal:

| Command                 | Action                                           |
| :---------------------- | :----------------------------------------------- |
| `pnpm install`          | Installs dependencies                            |
| `pnpm run dev`          | Starts local dev server at `localhost:3000`      |
| `pnpm run build`        | Build your production site to `./dist/`          |
| `pnpm run preview`      | Preview your build locally, before deploying     |
| `pnpm run astro ...`    | Run CLI commands like `astro add`, `astro check` |
| `pnpm run astro --help` | Get help using the Astro CLI                     |

## 👀 Want to learn more?

Feel free to check [our documentation](https://docs.astro.build) or jump into our [Discord server](https://astro.build/chat).
