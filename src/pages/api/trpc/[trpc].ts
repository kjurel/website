import { fetchRequestHandler } from "@website/server";
import type { APIRoute } from "astro";
import { appRouter } from "@server/index";

export const all: APIRoute = ({ request }) => {
  return fetchRequestHandler({
    req: request,
    endpoint: "/api/trpc",
    router: appRouter,
    createContext: async ({ req }) => {
      return { session: req.headers.get("X-Session") ?? undefined };
    },
  });
};
