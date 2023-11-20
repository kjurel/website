from __future__ import annotations

import typing as t
from os import environ

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi_login import LoginManager

from ..prefs import settings


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


def TokenAuth(scopes: t.Optional[dict[str, str]] = None):
    scopes = scopes or {}
    return LoginManager(
        secret=settings.AUTHENTICATION_SECRET_KEY,
        token_url=settings.AUTHENTICATION_TOKEN_URL,
        scopes=scopes,
    )
