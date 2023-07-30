import { createTRPCProxyClient, httpBatchLink } from "@trpc/client";
import type { AppRouter } from "./_app";
export const trpc = createTRPCProxyClient<AppRouter>({
  links: [
    httpBatchLink({
      url: "/api/trpc",
      headers() {
        return {
          // "X-Session": cookies,
        };
      },
    }),
  ],
});
