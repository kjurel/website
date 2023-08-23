import { z } from "zod";
import { publicProcedure, router } from "../index";

export default router({
  greeting: publicProcedure
    .input(
      z.object({
        name: z.string(),
      })
    )
    .mutation(({ input }) => {
      return input.name;
    }),
});
