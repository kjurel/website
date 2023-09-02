import importlib
import logging.config
import typing as t

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi_profiler import PyInstrumentProfilerMiddleware
from fastapi_utils.timing import add_timing_middleware
from tortoise.contrib.fastapi import register_tortoise

from .exceptions import APIException, on_api_exception, unhandled_exception_handler
from .settings import DEFAULT_LOGGING, settings

TORTOISE_ORM = settings.get_tortoise_config()


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
        is_print_each_request=False,  # Set to True to show request profile on stdout on each request
        open_in_browser=True,  # Set to true to open your web-browser automatically when the server shuts down
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=["X-Request-ID"],
    )

    if production:
        app.add_middleware(HTTPSRedirectMiddleware)


def app_factory() -> FastAPI:
    kwargs: dict[str, t.Any] = {}
    if settings.PRODUCTION:
        kwargs.update(openapi_url=None)
        kwargs.update(docs_url=None)
        kwargs.update(redoc_url=None)

    app = FastAPI(debug=settings.DEBUG, **kwargs)

    configure_logging()
    configure_middlewares(app, settings.PRODUCTION)

    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=not settings.PRODUCTION,
    )

    app.add_exception_handler(APIException, on_api_exception)
    app.add_exception_handler(APIException, unhandled_exception_handler)

    r = APIRouter()
    for ap in settings.get_applist:
        if ap.router and ap.router.prop:
            rt = getattr(importlib.import_module(ap.router.module), "router", None)
            print(rt)
            if rt is not None:
                r.include_router(rt, prefix="/" + ap.name)
    app.include_router(r, prefix=settings.API_ENDPOINT)
    # app.include_router(instagram.router, prefix=settings.API_ENDPOINT)
    return app
