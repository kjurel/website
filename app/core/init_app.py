import logging.config
import time
import typing

from app.api import common, instagram
from app.core.exceptions import APIException, on_api_exception
from app.settings.config import settings
from app.settings.log import DEFAULT_LOGGING
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from tortoise.contrib.fastapi import register_tortoise


def configure_logging(log_settings: dict = None):
  log_settings = log_settings or DEFAULT_LOGGING
  logging.config.dictConfig(log_settings)


def init_middlewares(app: FastAPI):
  
  @app.middleware("http")
  async def add_process_time_header(
      request: Request,
      call_next: typing.Callable[[Request],
                                 typing.Awaitable[Response]]
  ):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
  
  app.add_middleware(
      CORSMiddleware,
      allow_origins=settings.CORS_ORIGINS,
      allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
      allow_methods=settings.CORS_ALLOW_METHODS,
      allow_headers=settings.CORS_ALLOW_HEADERS,
  )
  
  if settings.production:
    app.add_middleware(HTTPSRedirectMiddleware)


def register_db(app: FastAPI, db_url: str | None = None):
  db_url = db_url or settings.POSTGRES_URL
  app_list = settings.get_db_app_list(migrations=True)
  register_tortoise(
      app,
      db_url=db_url,
      modules={ "models": app_list },
      generate_schemas=True,
      add_exception_handlers=True,
  )


def get_tortoise_config() -> dict[str, typing.Any]:
  app_list = settings.get_db_app_list(migrations=True)
  tconfig = {
      "connections": settings.get_db_connentions(),
      "apps": {
          "models": {
              "models": app_list,
              "default_connection": "default",
          }
      },
  }
  return tconfig


TORTOISE_ORM = get_tortoise_config()


def register_exceptions(app: FastAPI):
  app.add_exception_handler(APIException, on_api_exception)


def register_routers(app: FastAPI):
  app.include_router(common.router, prefix=settings.API_ENDPOINT)
  app.include_router(instagram.router, prefix=settings.API_ENDPOINT)
