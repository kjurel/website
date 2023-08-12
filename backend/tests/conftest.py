"""Unit tests configuration module."""

pytest_plugins = []


import asyncio
from os import environ

import pytest
from src.main import app_factory, settings
from src.utils import reset_tortoise
from fastapi.testclient import TestClient
from tortoise import Tortoise

asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture(scope="session")
def client():
  test_client = app_factory(True)
  yield test_client


@pytest.fixture
async def database(tortoise):
  yield
  await reset_tortoise("public", False)


@pytest.fixture(scope="session")
async def tortoise():
  DATABASE_URL = environ["POSTGRES_TEST_URL"]
  await Tortoise.init(
      db_url=DATABASE_URL,
      modules={ "models": settings.get_db_app_list() }
  )
  await reset_tortoise("public", False)
  await Tortoise.generate_schemas()
  yield
  await Tortoise.close_connections()


@pytest.fixture(scope="session")
def event_loop():
  return asyncio.get_event_loop()
