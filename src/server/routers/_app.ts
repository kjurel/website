import { z } from "zod";

import { deicmsLoginRouter } from "@server/routers/deicms";
import { netaidUserRouter } from "@server/routers/netaid";
import { mergeRouters, router } from "@server/trpc";

export const appRouter = router({
  deicms: mergeRouters(deicmsLoginRouter), // put procedures under "deicms" namespace
  netaid: mergeRouters(netaidUserRouter)
});

// You can then access the merged route with
// http://localhost:3000/trpc/<NAMESPACE>.<PROCEDURE>

export type AppRouter = typeof appRouter;
