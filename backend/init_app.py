from __future__ import annotations

import importlib
import inspect
import os
import typing as t
from glob import glob

from fastapi import APIRouter, FastAPI
from tortoise.contrib.fastapi import register_tortoise

from .controllers import Routers
from .core.exceptions import APIException, on_api_exception, unhandled_exception_handler
from .middlewares import configure_middlewares
from .prefs import settings
from .utils.schemas import File


class App:
    def __init__(self, base: t.Optional[str]) -> None:
        # get importing path
        if base:
            self._base_url = base
        else:
            self._base_url = "/" + (
                inspect.stack()[-1]
                .filename.split("website", 1)[-1]
                .rstrip(".py")
                .rstrip("/index")
            )  # dont use complex "index" files

        self._app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)
        configure_middlewares(self._app)
        self._app.add_exception_handler(APIException, on_api_exception)
        self._app.add_exception_handler(APIException, unhandled_exception_handler)

    def _get_file_list(
        self, subdir: str = "controllers"
    ) -> t.Generator[File, None, None]:
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

    def title(self, t: str, /):
        self._app.title = t
        return self

    def description(self, t: str, /):
        self._app.description = t
        return self

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

        PROJECT_ROOT = os.path.abspath(
            os.path.join(os.path.dirname(__file__), os.pardir)
        )
        PROJECT_ROOT = os.path.dirname(__file__)
        APPS_MODULE = "backend.controllers"
        pth = os.path.join(PROJECT_ROOT, os.path.basename("controllers"), "**.py")
        for f in glob(pth):
            if f.find("__init__.py") != -1:
                continue
            name = os.path.basename(f).rstrip(".py")
            if name not in ct:
                continue

            module = ".".join([APPS_MODULE, name])

            # condition for database
            rt = getattr(importlib.import_module(module), "router", None)
            if rt is not None:
                print("router added")
                self.mainRouter.include_router(rt, prefix=f"/{name}")
        return self

    def attach_controllers(self):
        self._app.include_router(self.mainRouter, prefix=self._base_url)
        return self
