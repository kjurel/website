from __future__ import annotations

import importlib
import logging
import os
import typing as t
from functools import lru_cache
from glob import glob

import pydantic


class AppProps(pydantic.BaseModel):
    prop: bool
    module: str


class App(pydantic.BaseModel):
    name: str
    module: str
    database: t.Optional[AppProps]
    router: t.Optional[AppProps]


class Settings(pydantic.BaseSettings):
    PRODUCTION = True
    DEBUG = True
    # AppSettings
    SERVER_HOST = "localhost"
    API_ENDPOINT = "/api/python"
    MODULE_ENDPOINT = API_ENDPOINT + "/{}"
    TOKEN_URL = MODULE_ENDPOINT + "/access-token"

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    APPS_ROOT = os.path.join(PROJECT_ROOT, "apps")
    LOGS_ROOT = os.path.join(PROJECT_ROOT, "logs")
    MIGS_ROOT = os.path.join(PROJECT_ROOT, "migrations")

    APPS_MODULE = ".".join([os.path.basename(f) for f in (PROJECT_ROOT, APPS_ROOT)])
    MIGS_MODULE = ".".join(
        [os.path.basename(f) for f in (PROJECT_ROOT, MIGS_ROOT)] + ["models"]
    )

    APPS_DB_PROP = "__database__"
    APPS_RT_PROP = "__router__"

    @property
    def get_applist(self) -> list[App]:
        pth = os.path.join(
            self.PROJECT_ROOT, os.path.basename(self.APPS_ROOT), "**/__init__.py"
        )
        retval: list[App] = []
        for f in glob(pth):
            name = os.path.basename(os.path.dirname(f))
            module = ".".join([self.APPS_MODULE, name])
            dbprop: AppProps = AppProps(
                prop=getattr(importlib.import_module(module), self.APPS_DB_PROP, False),
                module=".".join([module, "modelDatabase.py"]),
            )
            rtprop: AppProps = AppProps(
                prop=getattr(importlib.import_module(module), self.APPS_RT_PROP, False),
                # module=".".join([module, "router"]),
                module=module,
            )
            retval.append(App(name=name, module=module, database=dbprop, router=rtprop))
        return retval

    # MiddlewareSettings
    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5000",
        "http://localhost:3000",
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*", "X-Request-With", "X-Request-Id"]

    # DatabaseSettings
    POSTGRES_URL: pydantic.PostgresDsn
    REDIS_URL: pydantic.RedisDsn
    RABBIT_URL: pydantic.AmqpDsn

    SECRET_KEY: str  # openssl rand -hex 32

    def get_tortoise_config(self) -> t.Dict[str, t.Any]:
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "db_url": self.POSTGRES_URL,
                    "credentials": {
                        "host": self.POSTGRES_URL.host,
                        "port": self.POSTGRES_URL.port,
                        "user": self.POSTGRES_URL.user,
                        "password": self.POSTGRES_URL.password,
                        "database": None
                        if self.POSTGRES_URL.path is None
                        else self.POSTGRES_URL.path[1:],
                    },
                }
            },
            "apps": {
                "models": {
                    "models": [
                        app.database.module
                        for app in self.get_applist
                        if app.database and app.database.prop
                    ]
                    + [settings.MIGS_MODULE],
                    "default_connection": "default",
                }
            },
        }

    class Config:
        env_prefix = "PYTHON_"
        env_file = ".env", ".env.local"
        env_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings():
    from dotenv import load_dotenv

    load_dotenv(encoding="utf-8")
    return Settings()  # type: ignore


settings = get_settings()

DEFAULT_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "backendPython.core.settings.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "backendPython.core.settings.RequireDebugTrue",
        },
        # "correlation_id": {
        #     "()": "asgi_correlation_id.CorrelationIdFilter",
        #     "uuid_length": 32,
        #     "defaul_value": "-",
        # },
    },
    "formatters": {
        "main_formatter": {
            "format": "[%(levelname)s]:[%(name)s]: %(message)s "
            "(%(asctime)s; %(filename)s:%(lineno)d)",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "web": {
            "class": "logging.Formatter",
            "datefmt": "%H:%M:%S",
            "format": "%(levelname)s ... [%(correlation_id)s] %(name)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "filters": ["require_debug_true"],
            "class": "logging.StreamHandler",
            "formatter": "main_formatter",
        },
        "production_file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{settings.LOGS_ROOT}/app_main.log",
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "main_formatter",
            "filters": ["require_debug_false"],
        },
        "debug_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{settings.LOGS_ROOT}/app_main_debug.log",
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "main_formatter",
            "filters": ["require_debug_true"],
        },
        # "web": {
        #     "class": "logging.StreamHandler",
        #     "filters": ["correlation_id"],
        #     "formatter": "web",
        # },
    },
    "loggers": {
        "": {
            "handlers": ["console", "production_file", "debug_file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}


class RequireDebugFalse(logging.Filter):
    def filter(self, _):
        return not settings.DEBUG


class RequireDebugTrue(logging.Filter):
    def filter(self, _):
        return settings.DEBUG
