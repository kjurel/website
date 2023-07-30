import typing

from fastapi import FastAPI


def app_factory(
    logging: bool,
    middelewares: bool,
    exceptions: bool,
    routers: bool,
    postgres: bool,
) -> typing.Generator[FastAPI, None, FastAPI]:

  kwargs: dict[str, str | None] = {}
  
  if settings.production:
    kwargs.update(docs_url=None)
    kwargs.update(redoc_url=None)
  
  application = FastAPI(debug=settings.debug, dependencies=[settings])
  
  yield application
  
  try:
    from .settings.config import settings
  except ImportError:
    raise SettingNotFound("Can not import settings")
  else:
    from app.core.init_app import (
        configure_logging,
        init_middlewares,
        register_db,
        register_exceptions,
        register_routers
    )
  
  init_middlewares(application)
  register_exceptions(application)
  register_routers(application)
  register_db(application)
  
  if not settings.debug:
    configure_logging()
  
  return application


