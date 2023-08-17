from __future__ import annotations

from os import environ

from app.settings.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_login import LoginManager


async def BasicAuth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    username = credentials.username == environ["MASTER_USER"]
    password = credentials.password == environ["MASTER_PASS"]

    if username and password:
        return None
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def TokenAuth(token_url_appname: str, scopes: dict[str, str]):
    return LoginManager(
        secret=settings.SECRET_KEY,
        token_url=settings.TOKEN_URL.format(),
    )
