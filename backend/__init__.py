import pydantic
from fastapi import APIRouter


class Module:
    __database__: bool
    __router__: bool
    __celery_backlinks__: bool
    __scrapy_backlinks__: bool


class App(pydantic.BaseModel):
    routers: list[APIRouter]

    def setup_app(mainRouter: APIRouter, appRouter: APIRouter):
        mainRouter.include_router(APIRouter)
        pass
