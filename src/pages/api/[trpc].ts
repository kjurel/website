import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import { appRouter } from "@server/routers/_app";
import { createContext } from "@server/context";
import type { APIRoute } from "astro";

export const ALL: APIRoute = (opts) => {
  return fetchRequestHandler({
    endpoint: "/api",
    req: opts.request,
    router: appRouter,
    createContext,
  });
};
