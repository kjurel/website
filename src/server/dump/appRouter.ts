import { initTRPC } from "@trpc/server";
import { z } from "zod";

export const t = initTRPC.create();

export const appRouter = t.router({
  hello: t.procedure.query(() => {
    return {
      message: "hello world",
    };
  }),
  getUser: t.procedure.input(z.string()).query((opts) => {
    return { id: opts.input, name: "Bilbo" };
  }),
  createUser: t.procedure.input(z.object({ name: z.string().min(5) })).mutation(async (opts) => {
    // use your ORM of choice
    return await UserModel.create({
      data: opts.input,
    });
  }),
});

// export type definition of API
export type AppRouter = typeof appRouter;
