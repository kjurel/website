import { defineMiddleware } from "astro:middleware";

// `context` and `next` are automatically typed
export const onRequest = defineMiddleware((context, next) => {
  const { locals } = context;
  // intercept response data from a request
  // optionally, transform the response by modifying `locals`
  locals.title = "Website";
  locals.welcomeTitle = () => "Welcome";

  // return a Response or the result of calling `next()`
  return next();
});
