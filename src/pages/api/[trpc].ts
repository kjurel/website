import { fetchRequestHandler } from "@trpc/server/adapters/fetch";
import type { APIRoute } from "astro";
import { appRouter } from "@/server/index";

export const ALL: APIRoute = ({ request }) => {
  return fetchRequestHandler({
    req: request,
    endpoint: "/api",
    router: appRouter,
    createContext: async ({ req }) => {
      return { session: req.headers.get("X-Session") ?? undefined };
    },
  });
};
