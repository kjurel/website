import { createInsertSchema, createSelectSchema } from "drizzle-zod";
import { userIDTable } from "@/database/schema/netaid";
import { router, publicProcedure } from "@server/trpc";
import { db } from "@/database/client";
import bcrypt from "bcrypt";
import {eq} from "drizzle-orm"
import { z } from "zod";
const SALT_ROUNDS = 10;

export const netaidUserRouter = router({
  register: publicProcedure.input(createInsertSchema(userIDTable)).mutation(async ({ ctx, input }) => {
    const { name, password, aadhar_no } = input;
    // Check if user already exists
    const existingUser = await db.query.userIDTable.findFirst({
      where: (user, { eq }) => eq(user.aadhar_no, aadhar_no),
    });
    if (existingUser) return;

    // Hash the password
    const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);

    // Create a new user
    const newUser = await db
      .insert(userIDTable)
      .values({
        name,
        password: hashedPassword,
        aadhar_no,
      })
      .returning()
      .then((u) => u.at(0));

    return { id: newUser?.id, name: newUser?.name };
  }),
  login: publicProcedure
    .input(
      z.object({
        username: z.string(),
        password: z.string().min(6),
      })
    )
    .mutation(async ({ input }) => {
      const { username, password } = input;

      // Find the user
      const user = await db.query.userIDTable.findFirst({
        where: (user, { eq }) => eq(user.name, username),
      });
      if (!user) return;

      // Check the password
      const isPasswordValid = await bcrypt.compare(password, user.password);
      if (!isPasswordValid) return;

      return { id: user.id, name: user.name };
    }),
  getAllUsers: publicProcedure.query(async ()=>{
    const users = await db.query.userIDTable.findMany()
    return users
  })
  // deleteUsers: publicProcedure.input(z.array(z.string()).mutation(async ({input})=>{
  //   await db.delete(userIDTable).where(user=>input.includes(user.id))
  // })
});
