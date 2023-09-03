from __future__ import annotations

from app.api.instagram.models.database import USER_PYDANTIC, User
from app.api.instagram.models.schemas import UserConfig, UserMetadataExtra
from app.api.instagram.routers.auth import OAUTH2
from app.api.instagram.utilities import generate_new_device
from app.core.authentication import BasicAuth, TokenAuth
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)

userRouter = APIRouter(prefix="/user", tags=["Instagram User"])


@userRouter.get(
    "/",
    responses={200: {"content": {"aplication/json": {}}}},
    response_class=Response,
)
async def get_user(user: User = Depends(TokenAuth)):
    # (await User_pydantic.from_tortoise_orm(user)).json(encoder=None)

    return Response(content=await user.to_json(), media_type="application/json")


@userRouter.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(f: UploadFile, _=Depends(BasicAuth)):
    if f.content_type == "aplication/json":
        await (user := await User.from_json(f.file.read())).save()
    else:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    return USER_PYDANTIC.from_tortoise_orm(user)


@userRouter.delete("/")
async def delete_user(user: User = Depends(TokenAuth)):
    return await user.delete()


@userRouter.patch("/device")
async def update_instagram_device(
    country: str = Body(...),
    code: int = Body(...),
    locale: str = Body(...),
    tz: float = Body(...),
    user: User = Depends(TokenAuth),
):
    j = generate_new_device(dict(country=country, code=code, locale=locale, tz=tz))
    return await user.update_from_dict(dict(instagram_device=j)).save()


@userRouter.patch("/icon")
async def set_icon(f: UploadFile | None = File(None), user: User = Depends(OAUTH2)):
    if f is None:
        v = None
    elif f.content_type == "image/png":
        v = await f.read()
    else:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    await user.update_from_dict(dict(icon=v)).save()
    return "Icon updated"


@userRouter.patch("/metadataextra")
async def patch_metadata(
    extrametadata: UserMetadataExtra, user: User = Depends(OAUTH2)
):
    user.metadata.extra = extrametadata
    return await user.save()


@userRouter.patch("/config")
async def patch_config(config: UserConfig, user: User = Depends(OAUTH2)):
    user.config = config
    return await user.save()
