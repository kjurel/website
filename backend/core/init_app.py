import logging.config
import typing as t

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi_profiler import PyInstrumentProfilerMiddleware
from fastapi_utils.timing import add_timing_middleware
from tortoise.contrib.fastapi import register_tortoise

from ..settings import DEFAULT_LOGGING, settings
from .exceptions import (APIException, on_api_exception,
                         unhandled_exception_handler)


def configure_logging() -> None:
    log_settings: t.Dict[str, t.Any] = DEFAULT_LOGGING
    logging.config.dictConfig(log_settings)


def configure_middlewares(app: FastAPI, production: bool = False) -> None:
    add_timing_middleware(app, prefix="app")
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        PyInstrumentProfilerMiddleware,
        server_app=app,  # Required to output the profile on server shutdown
        profiler_output_type="html",
        is_print_each_request=False,  # Set to True to show request profile on
        # stdout on each request
        open_in_browser=False,  # Set to true to open your web-browser automatically
        # when the server shuts down
        html_file_name="example_profile.html",  # Filename for output
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    if production:
        app.add_middleware(HTTPSRedirectMiddleware)


def register_exceptions(app: FastAPI) -> None:
    app.add_exception_handler(APIException, on_api_exception)
    app.add_exception_handler(APIException, unhandled_exception_handler)


def register_routers(app: FastAPI):
    app.include_router(common.router, prefix=settings.API_ENDPOINT)
    app.include_router(instagram.router, prefix=settings.API_ENDPOINT)


def register_routers(app: FastAPI):
    db_url = settings.POSTGRES_URL
    app_list = settings.get_db_app_list(migrations=True)
    register_tortoise(
        app,
        db_url=db_url,
        modules={"models": app_list},
        generate_schemas=True,
        add_exception_handlers=True,
    )


def get_tortoise_config() -> t.Dict[str, t.Any]:
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


def app_factory() -> FastAPI:
    kwargs: dict[str, t.Any] = {}
    if settings.PRODUCTION:
        kwargs.update(openapi_url=None)
        kwargs.update(docs_url=None)
        kwargs.update(redoc_url=None)
    application = FastAPI(debug=settings.DEBUG, **kwargs)
    return application
