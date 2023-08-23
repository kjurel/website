This is my personal project, I specifically made for learing more stuff.
It hosts my porfolio and some small projects that I didnt think needed a separate repo.
Enjoy!!

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

# Turborepo starter

This is an official starter Turborepo.

## Using this example

Run the following command:

```sh
npx create-turbo@latest
```

## What's inside?

This Turborepo includes the following packages/apps:

### Apps and Packages

- `docs`: a [Next.js](https://nextjs.org/) app
- `web`: another [Next.js](https://nextjs.org/) app
- `ui`: a stub React component library shared by both `web` and `docs` applications
- `eslint-config-custom`: `eslint` configurations (includes `eslint-config-next` and `eslint-config-prettier`)
- `tsconfig`: `tsconfig.json`s used throughout the monorepo

Each package/app is 100% [TypeScript](https://www.typescriptlang.org/).

### Utilities

This Turborepo has some additional tools already setup for you:

- [TypeScript](https://www.typescriptlang.org/) for static type checking
- [ESLint](https://eslint.org/) for code linting
- [Prettier](https://prettier.io) for code formatting

### Build

To build all apps and packages, run the following command:

```
cd my-turborepo
pnpm build
```

### Develop

To develop all apps and packages, run the following command:

```
cd my-turborepo
pnpm dev
```

### Remote Caching

Turborepo can use a technique known as [Remote Caching](https://turbo.build/repo/docs/core-concepts/remote-caching) to share cache artifacts across machines, enabling you to share build caches with your team and CI/CD pipelines.

By default, Turborepo will cache locally. To enable Remote Caching you will need an account with Vercel. If you don't have an account you can [create one](https://vercel.com/signup), then enter the following commands:

```
cd my-turborepo
npx turbo login
```

This will authenticate the Turborepo CLI with your [Vercel account](https://vercel.com/docs/concepts/personal-accounts/overview).

Next, you can link your Turborepo to your Remote Cache by running the following command from the root of your Turborepo:

```
npx turbo link
```

## Useful Links

Learn more about the power of Turborepo:

- [Tasks](https://turbo.build/repo/docs/core-concepts/monorepos/running-tasks)
- [Caching](https://turbo.build/repo/docs/core-concepts/caching)
- [Remote Caching](https://turbo.build/repo/docs/core-concepts/remote-caching)
- [Filtering](https://turbo.build/repo/docs/core-concepts/monorepos/filtering)
- [Configuration Options](https://turbo.build/repo/docs/reference/configuration)
- [CLI Usage](https://turbo.build/repo/docs/reference/command-line-reference)

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
