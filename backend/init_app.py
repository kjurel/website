from __future__ import annotations

import importlib
import inspect
import json
import os
import typing as t
from glob import glob

from fastapi import APIRouter, FastAPI
from fastapi.background import P
from tortoise.contrib.fastapi import register_tortoise

from .controllers import Routers
from .core.exceptions import APIException, on_api_exception, unhandled_exception_handler
from .middlewares import configure_middlewares
from .prefs import settings
from .utils.schemas import File


class App:
    def __init__(self, base: str) -> None:
        # get importing path
        self._base_url = base

        self._app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
        configure_middlewares(self._app)
        self._app.add_exception_handler(APIException, on_api_exception)
        self._app.add_exception_handler(APIException, unhandled_exception_handler)

    @classmethod
    def from_file(cls, file: str, vercel_json: bool = False):
        current_file = os.path.abspath(file)
        index = current_file.rfind("api")

        if index != -1:
            path_from_string = current_file[index - 1 :]
        else:
            raise ValueError("The string 'api' was not found in the file path.")

        base_string = path_from_string.rstrip(".py").rstrip("index").rstrip("/")

        if not vercel_json:
            return cls(base_string)

        with open("./vercel.json") as f:
            rewrites: t.List[
                t.Dict[t.Literal["destination"] | t.Literal["source"], str]
            ] = json.load(f).get("rewrites", [])

        # goto last slash and take string before slash
        for m in rewrites:
            if base_string == m["destination"]:
                src = m["source"]
                if (idx := src.rfind("/")) != -1:
                    base_string = src[:idx]  # updated from rewrites
        # complex regexes are not possible
        return cls(base_string)

    @staticmethod
    def _get_file_list(subdir: str) -> t.Generator[File, None, None]:
        """access files in a subdir inside backend"""
        PROJECT_ROOT = os.path.dirname(__file__)
        APPS_MODULE = ".".join(["backend", subdir])
        pth = os.path.join(PROJECT_ROOT, os.path.basename(subdir), "**.py")
        for f in glob(pth):
            filename = os.path.basename(f).rstrip(".py")
            module = ".".join([APPS_MODULE, filename])
            yield File(name=filename, path=f, import_string=module)

    @property
    def app(self):
        return self._app

    def docs(self):
        self._app.docs_url = self._base_url + "/docs"
        self._app.openapi_url = self._base_url + "/openapi.json"
        self._app.redoc_url = self._base_url + "/redoc"

    def tortoise(self):
        MIGS_MODULE = "migrations"
        MODELS = [f.import_string for f in self._get_file_list("models")]
        MODELS.append(MIGS_MODULE)
        TORTOISE_ORM_CONFIG = settings.get_tortoise_config(MODELS)
        register_tortoise(
            self._app,
            config=TORTOISE_ORM_CONFIG,
            generate_schemas=True,
            add_exception_handlers=not settings.PRODUCTION,
        )
        return

    def controllers(self, ct: Routers) -> App:
        self._ct = ct
        self.mainRouter = APIRouter()

        for f in self._get_file_list("controllers"):
            if f.path.find("__init__.py") != -1:
                continue
            if f.name not in ct:
                continue

            # condition for database
            rt = getattr(importlib.import_module(f.import_string), "router", None)
            if rt is not None:
                self.mainRouter.include_router(rt)
        return self

    def attach_controllers(self):
        self._app.include_router(self.mainRouter, prefix=self._base_url)

        @self._app.get(self._base_url)
        def basic():
            return {
                "service": "UP",
                "base_url": self._base_url,
                "controllers": self._ct,
            }

        return self
