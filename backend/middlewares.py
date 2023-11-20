from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi_utils.timing import add_timing_middleware

from .prefs import settings


def configure_middlewares(app: FastAPI) -> None:
    add_timing_middleware(app, prefix="app")
    add_cors_middleware(app)
    if settings.PRODUCTION:
        app.add_middleware(HTTPSRedirectMiddleware)


def add_cors_middleware(app: FastAPI, /):
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origins_regex=settings.CORS_REGEX_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        expose_headers=["X-Request-ID"],
    )
