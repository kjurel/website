import { createTRPCProxyClient, httpBatchLink, loggerLink } from "@trpc/client";
import type { AppRouter } from "@server/routers/_app";

export const client = createTRPCProxyClient<AppRouter>({
  links: [
    loggerLink(),
    httpBatchLink({
      url: "/api",
      // You can pass any HTTP headers you wish here
    }),
  ],
});

