import type { FetchCreateContextFnOptions } from "@trpc/server/adapters/fetch";
import type { inferAsyncReturnType } from "@trpc/server";

export function createContext({ req, resHeaders }: FetchCreateContextFnOptions) {
  const user = { name: req.headers.get("username") ?? "anonymous" };
  return { req, resHeaders, user };
}

export type Context = inferAsyncReturnType<typeof createContext>;
