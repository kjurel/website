from __future__ import annotations

from app.api.instagram.models import User
from app.core.authentication import TokenAuth
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login.exceptions import InvalidCredentialsException
from tortoise.contrib.pydantic import pydantic_model_creator

OAUTH2 = TokenAuth(
    token_url_appname=__name__.split(".")[-2],
    scopes={ "login": "this logs the user in and enable login related routes"},
)


@OAUTH2.user_loader()
async def load_user(username: str):
  user = await User.get(username=username)
  return user


authRouter = APIRouter(tags=["Authentication"])


@authRouter.post("/access-token")
async def token(data: OAuth2PasswordRequestForm = Depends()):
  username = data.username
  password = data.password
  
  user = await load_user(username)
  if user and user.passverify(password):
    scopes = data.scopes
    if "login" in scopes:
      user.login()
    access_token = OAUTH2.create_access_token(
        data=dict(sub=username),
        scopes=scopes
    )
    return { "access_token": access_token, "token_type": "bearer"}
  raise InvalidCredentialsException
