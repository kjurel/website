# This is the first file to run
import os
import typing
from functools import lru_cache
from importlib import import_module

import pydantic


class Settings(pydantic.BaseSettings):
    SERVER_HOST = "localhost"
    API_ENDPOINT = "/api"
    MODULE_ENDPOINT = API_ENDPOINT + "/{}"
    TOKEN_URL = MODULE_ENDPOINT + "/access-token"

    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT = os.path.join(BASE_DIR, "app/logs")

    CORS_ORIGINS = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5000",
        "http://localhost:3000",
    ]
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOW_METHODS = ["*"]
    CORS_ALLOW_HEADERS = ["*"]

    APPLICATIONS_MODULE = "app.applications"
    APPLICATIONS = {"common","instagram", "reddit", "xtra"}
    
    MIGRATIONS_MODULE = "migrations.models"

    # ENV-VARS
    POSTGRES_URL: pydantic.PostgresDsn
    REDIS_URL: pydantic.RedisDsn
    RABBIT_URL: pydantic.AmqpDsn

    SECRET_KEY: str  # openssl rand -hex 32

    def get_db_connentions(self) -> dict[str, typing.Any]:
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

    def app_list_props_checker(
        self,  *args, submodule_name: str,
    ) -> typing.Generator[str | None, None, None]:
        for app in self.APPLICATIONS:
            module_name = f"{self.APPLICATIONS_MODULE}.{app}.{submodule_name}"
            for dunder in args:
                module = import_module(module_name)
                if getattr(module, dunder, False) is True:
                    yield module_name
                else:
                    yield None

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

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    from dotenv import load_dotenv

    load_dotenv(encoding="utf-8")
    return Settings()  # type: ignore


settings = get_settings()