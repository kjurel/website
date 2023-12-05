from __future__ import annotations

import typing as t
from functools import lru_cache

import pydantic
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PRODUCTION: bool = True
    DEBUG: bool

    AUTHENTICATION_MASTER_USERNAME: str
    AUTHENTICATION_MASTER_PASSWORD: str
    AUTHENTICATION_SECRET_KEY: str  # openssl rand -hex 32
    AUTHENTICATION_TOKEN_URL: str

    DATABASE_POSTGRES_URL: pydantic.PostgresDsn
    DATABASE_REDIS_URL: pydantic.RedisDsn
    DATABASE_RABBIT_URL: pydantic.AmqpDsn

    # MiddlewareSettings
    CORS_ORIGINS: t.ClassVar[t.List[str]] = [
        "http://localhost:4321",
        "https://kanishkk.vercel.app",
        "https://website-git-main-tokcide.vercel.app",
    ]
    CORS_REGEX_ORIGINS: t.ClassVar[
        str
    ] = r"https:\/\/website-(?:[a-zA-Z0-9_-]+)-tokcide\.vercel\.app"

    CORS_ALLOW_CREDENTIALS: t.ClassVar[bool] = True
    CORS_ALLOW_METHODS: t.ClassVar[t.List[str]] = ["*"]
    CORS_ALLOW_HEADERS: t.ClassVar[t.List[str]] = [
        "*",
        "X-Request-With",
        "X-Request-Id",
    ]

    class Config:
        env_prefix = "PYTHON_"
        env_file = ".env", ".env.local"
        env_encoding = "utf-8"
        case_sensitive = False

    def get_tortoise_config(self, m: t.List[str], /):
        # "default": {
        #     "engine": "tortoise.backends.asyncpg",
        #     "db_url": self.DATABASE_POSTGRES_URL,
        #     "credentials": {
        #         "host": self.DATABASE_POSTGRES_URL.hosts()[0],
        #         "port": self.DATABASE_POSTGRES_URL.port,
        #         "user": self.DATABASE_POSTGRES_URL.user,
        #         "password": self.DATABASE_POSTGRES_URL.password,
        #         "database": None
        #         if self.DATABASE_POSTGRES_URL.path is None
        #         else self.DATABASE_POSTGRES_URL.path[1:],
        #     },
        # }
        return {
            "connections": {"default": self.DATABASE_POSTGRES_URL},
            "apps": {
                "models": {
                    "models": m,
                    "default_connection": "default",
                }
            },
        }


@lru_cache()
def get_settings():
    return Settings()  # type: ignore


settings = get_settings()
# class Settings2(pydantic.BaseSettings):
#     # AppSettings
#     SERVER_HOST = "localhost"
#     API_ENDPOINT = "/api/py"
#     CONTROLLER_ENDPOINT = API_ENDPOINT + "/{}"
#     TOKEN_URL = CONTROLLER_ENDPOINT.format("/access-token")
#
#     PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
#     CONTROLLERS_ROOT = os.path.join(PROJECT_ROOT, "controllers")
#     MODELS_ROOT = os.path.join(PROJECT_ROOT, "models")
#     MIGRATIONS_ROOT = os.path.join(PROJECT_ROOT, "migrations")
#     # backend.apps
#     APPS_MODULE = ".".join([os.path.basename(f) for f in (PROJECT_ROOT, APPS_ROOT)])
#     # backend.migrations
#     MIGS_MODULE = ".".join(
#         [os.path.basename(f) for f in (PROJECT_ROOT, MIGS_ROOT)] + ["models"]
#     )
#
#     def get_controllers(self, controller_names: t.Optional[Routers]) -> list[App]:
#         pth = os.path.join(
#             self.PROJECT_ROOT, os.path.basename(self.APPS_ROOT), "**/__init__.py"
#         )
#         retval: list[App] = []
#         for f in glob(pth):
#             name = os.path.basename(os.path.dirname(f))
#             if app_names and name not in app_names:
#                 continue
#             module = ".".join([self.APPS_MODULE, name])
#             dbprop: AppProps = AppProps(
#                 prop=getattr(importlib.import_module(module), self.APPS_DB_PROP, False),
#                 module=".".join([module, "modelDatabase.py"]),
#             )
#             rtprop: AppProps = AppProps(
#                 prop=getattr(importlib.import_module(module), self.APPS_RT_PROP, False),
#                 # module=".".join([module, "router"]),
#                 module=module,
#             )
#             retval.append(App(name=name, module=module, database=dbprop, router=rtprop))
#         return retval
#
#
#     # DatabaseSettings
#     POSTGRES_URL: pydantic.PostgresDsn
#     REDIS_URL: pydantic.RedisDsn
#     RABBIT_URL: pydantic.AmqpDsn
#
#     SECRET_KEY: str  # openssl rand -hex 32
#
#     def get_tortoise_config(
#         self, app_names: t.Optional[list[str]]
#     ) -> t.Dict[str, t.Any]:
#         return {
#             "connections": {
#                 "default": {
#                     "engine": "tortoise.backends.asyncpg",
#                     "db_url": self.POSTGRES_URL,
#                     "credentials": {
#                         "host": self.POSTGRES_URL.host,
#                         "port": self.POSTGRES_URL.port,
#                         "user": self.POSTGRES_URL.user,
#                         "password": self.POSTGRES_URL.password,
#                         "database": None
#                         if self.POSTGRES_URL.path is None
#                         else self.POSTGRES_URL.path[1:],
#                     },
#                 }
#             },
#             "apps": {
#                 "models": {
#                     "models": [
#                         app.database.module
#                         for app in self.get_applist(app_names)
#                         if app.database and app.database.prop
#                     ]
#                     + [settings.MIGS_MODULE],
#                     "default_connection": "default",
#                 }
#             },
#         }
#
#     class Config:
#         env_prefix = "PYTHON_"
#         env_file = ".env", ".env.local"
#         env_encoding = "utf-8"
#         case_sensitive = False
#
