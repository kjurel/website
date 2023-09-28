import { initTRPC, Router } from "@trpc/server";
export { fetchRequestHandler } from "@trpc/server/adapters/fetch";

const t = initTRPC.create();

export const router = t.router;
export const middleware = t.middleware;
export const publicProcedure = t.procedure;

// const routerConfig: Router =

export const appRouter = router({
  hello: publicProcedure.query(() => {
    return {
      message: "hello world",
    };
  }),
  goodbye: publicProcedure.mutation(async () => {
    return {
      message: "goobye",
    };
  }),
});
