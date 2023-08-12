# This is the first file to run

import logging
import os
import typing as t
from functools import lru_cache
from importlib import import_module

import pydantic


class Settings(pydantic.BaseSettings):
    PRODUCTION = True
    DEBUG = True
    # AppSettings
    SERVER_HOST = "localhost"
    API_ENDPOINT = "/api"
    MODULE_ENDPOINT = API_ENDPOINT + "/{}"
    TOKEN_URL = MODULE_ENDPOINT + "/access-token"

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT = os.path.join(BASE_DIR, "app/logs")

    APPLICATIONS_MODULE = "app.applications"
    APPLICATIONS = {"common", "instagram", "reddit", "xtra"}
    MIGRATIONS_MODULE = "migrations.models"

    SECRET_KEY: str  # openssl rand -hex 32

    def app_list_props_checker(
        self,
        *args,
        submodule_name: str,
    ) -> t.Generator[str | None, None, None]:
        for app in self.APPLICATIONS:
            module_name = f"{self.APPLICATIONS_MODULE}.{app}.{submodule_name}"
            for dunder in args:
                module = import_module(module_name)
                if getattr(module, dunder, False) is True:
                    yield module_name
                else:
                    yield None

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

    def get_db_connentions(self) -> t.Dict[str, t.Any]:
        return {
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
        }

    def get_db_app_list(self, migrations: bool = False) -> list[str]:
        val = [
            name
            for name in self.app_list_props_checker(
                "__database__",
                submodule_name="models.database",
            )
            if name is not None
        ]
        if migrations:
            val.append(self.MIGRATIONS_MODULE)
        return val

    def get_tortoise_config(self) -> t.Dict[str, t.Any]:
        return {}

    class Config:
        env_file = ".env"
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
            "()": "backend.settings.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "backend.settings.RequireDebugTrue",
        },
        "correlation_id": {
            "()": "asgi_correlation_id.CorrelationIdFilter",
            "uuid_length": 32,
            "defaul_value": "-",
        },
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
            "filename": f"{AppSettings.LOGS_ROOT}/app_main.log",
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "main_formatter",
            "filters": ["require_debug_false"],
        },
        "debug_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": f"{AppSettings.LOGS_ROOT}/app_main_debug.log",
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 10,
            "formatter": "main_formatter",
            "filters": ["require_debug_true"],
        },
        "web": {
            "class": "logging.StreamHandler",
            "filters": ["correlation_id"],
            "formatter": "web",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console", "production_file", "debug_file", "web"],
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
