import { z } from "zod";

import { deicmsLoginRouter } from "@server/routers/deicms";
import { mergeRouters, router } from "@server/trpc";

export const appRouter = router({
  deicms: mergeRouters(deicmsLoginRouter), // put procedures under "deicms" namespace
});

// You can then access the merged route with
// http://localhost:3000/trpc/<NAMESPACE>.<PROCEDURE>

export type AppRouter = typeof appRouter;
