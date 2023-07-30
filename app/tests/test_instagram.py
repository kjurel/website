import io
import json
from os import environ

import pytest
import requests
from src.applications.instagram.models import User
from fastapi import FastAPI
from httpx import AsyncClient

fakeuser = {
    "username": "fakename",
    "password": "fakepassword",
    "instagram_device": None,
    "usercnfg": None,
    "userdata": None,
    "userinfo": None,
}


@pytest.mark.asyncio
async def test_user(client: FastAPI, tortoise):
  # """
  # GIVEN a fastapi application configured for testing
  # WHEN the "/" page is requested (GET)
  # THEN check that the response is valid
  # """
  # create user
  async with AsyncClient(app=client, base_url="http://localhost") as ac:
    # creating a user
    r = await ac.post(
        "/api/instagram/u/",
        headers=dict(accept="application/json"),
        files=dict(
            f=(
                "user.json",
                io.BytesIO(json.dumps(fakeuser).encode()),
                "application/json"
            )
        ),
        auth=(environ["MASTER_USER"],
              environ["MASTER_PASS"])
    )
    assert r.status_code == 201
    # checking if user was created
    assert len(await User.all()) == 1
    assert (user := await User.get(username="fakename")) is not None
    assert user.username == fakeuser["username"]
    assert user.instagram_device == fakeuser["instagram_device"]
    assert user.usercnfg == fakeuser["usercnfg"]
    assert user.userdata == fakeuser["userdata"]
    assert user.userinfo == fakeuser["userinfo"]
    # authenticating with the user
    r = await ac.post(
        "/api/instagram/u/",
        headers=dict(accept="application/json"),
        files=dict(
            f=(
                "user.json",
                io.BytesIO(json.dumps(fakeuser).encode()),
                "application/json"
            )
        ),
        auth=(environ["MASTER_USER"],
              environ["MASTER_PASS"])
    )
    assert r.status_code == 201
  
  # headers = {
  #   'accept': 'application/json',
  #     }
  
  # data = {
  #     'grant_type': '',
  #     'username': 'reyomensukuna',
  #     'password': 'ryomensukuna100k',
  #     'scope': '',
  #     'client_id': '',
  #     'client_secret': '',
  # }
  
  # response = requests.post('http://localhost:8000/api/instagram/access-token', headers=headers, data=data)


def delete_user():
  headers = {
      'accept':
      'application/json',
      'Authorization':
      'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJyZXlvbWVuc3VrdW5hIiwiZXhwIjoxNjUzMzIzMjY0fQ.u5QlWxMR1qIcshIxU8yy5orYSSKMb3nP4Xo7a0TU8NI',
  }
  
  response = requests.delete(
      'http://localhost:8000/api/instagram/u/',
      headers=headers
  )


def get_user():
  
  headers = {
      'accept':
      'application/json',
      'Authorization':
      'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJyZXlvbWVuc3VrdW5hIiwiZXhwIjoxNjUzMzI0OTI1fQ.7keVlAZC4tyl3X3onHmof-0KlxVAC_qVYxVc7PGTt3k',
  }
  
  response = requests.get(
      'http://localhost:8000/api/instagram/u/',
      headers=headers
  )
