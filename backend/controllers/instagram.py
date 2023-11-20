"""ONLY PYTHON"""
from __future__ import annotations

import typing as t

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
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_class import View, endpoint
from fastapi_login.exceptions import InvalidCredentialsException

from ..core.authentication import BasicAuth, TokenAuth
from ..models.instagram import USER_PYDANTIC
from ..models.instagram import InstagramUser as User
from ..models.instagram import UserConfig
from ..schemas.instagram import DeviceInputs

OAUTH2 = TokenAuth(
    scopes={"login": "Basic user previlages"},
)


@OAUTH2.user_loader()
async def load_user(username: str):
    user = await User.get(username=username)
    return user


@View(authRouter := APIRouter(prefix="/access-token", tags=["Authentication"]))
class AuthView:
    async def post(self, data: OAuth2PasswordRequestForm = Depends()):
        username = data.username
        password = data.password

        user = await load_user(username)
        if user and user.verify_password(password.encode()):
            scopes = data.scopes
            if "login" in scopes:
                print("login scope encountered in /access-token")
            access_token = OAUTH2.create_access_token(
                data=dict(sub=username), scopes=scopes
            )
            return {"access_token": access_token, "token_type": "bearer"}
        raise InvalidCredentialsException


@View(userRouter := APIRouter(prefix="/user", tags=["Instagram User"]))
class UserView:
    # responses={200: {"content": {"aplication/json": {}}}},
    # response_class=Response,
    @endpoint(status_code=200)
    async def get(self, user: User = Depends(TokenAuth)):
        # (await User_pydantic.from_tortoise_orm(user)).json(encoder=None)
        return Response(content=await user.to_json(), media_type="application/json")

    @endpoint(status_code=status.HTTP_201_CREATED)
    async def post(self, f: UploadFile, _=Depends(BasicAuth)):
        if f.content_type == "aplication/json":
            await (user := await User.from_json(f.file.read())).save()
        else:
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        return USER_PYDANTIC.from_tortoise_orm(user)

    async def delete(self, user: User = Depends(TokenAuth)):
        return await user.delete()

    @endpoint(("PATCH",), path="/device")
    async def update_instagram_device(
        self,
        country: str = Body(...),
        code: int = Body(...),
        locale: str = Body(...),
        tz: float = Body(...),
        user: User = Depends(TokenAuth),
    ):
        device_inputs: DeviceInputs = {
            "country": country,
            "code": code,
            "locale": locale,
            "tz": tz,
        }

        j = user.generate_new_device(device_inputs)
        return await user.update_from_dict(dict(instagram_device=j)).save()

    @staticmethod
    @endpoint(("PATCH",), path="/icon")
    async def set_icon(f: UploadFile | None = File(None), user: User = Depends(OAUTH2)):
        if f is None:
            v = None
        elif f.content_type == "image/png":
            v = await f.read()
        else:
            raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
        await user.update_from_dict(dict(icon=v)).save()
        return "Icon updated"

    @staticmethod
    @endpoint(("PATCH",), path="/config")
    async def patch_config(config: UserConfig, user: User = Depends(OAUTH2)):
        user.config = config
        return await user.save()


router = APIRouter()
router.include_router(authRouter)
router.include_router(userRouter)

# from __future__ import annotations

# from app.api.instagram.models import POST_PYDANTIC, Post, User
# from app.api.instagram.models.schemas import PostData, PostMedia
# from app.api.instagram.routers.auth import OAUTH2
# from fastapi import (APIRouter, Depends, File, Form, HTTPException, Response,
#                      Security, UploadFile, status)

# postRouter = APIRouter(prefix="/post", tags=["Instagram Post"])

# @postRouter.head("/")
# async def head_post(q: int | str, user: User = Security(OAUTH2, scopes=["login"])):
#     post_kwargs = (
#         dict(preset=q, status=Post.Status.UNBUILT) if type(q) is str else dict(id=q)
#     )
#     if (post := await user.get_post(**post_kwargs)) is None:
#         raise HTTPException(status.HTTP_404_NOT_FOUND)

#     match post.status:
#         case Post.Status.UNBUILT:
#             await post.build()
#             return f"Build post {post.id}"
#         case Post.Status.WAITING:
#             lk = await post.post(user.session)
#             return f"Posted at {lk}"
#         case _:
#             raise HTTPException(status.HTTP_403_FORBIDDEN)

# @postRouter.get(
#     "/", responses={200: {"content": {"image/jpeg": {}}}}, response_class=Response
# )
# async def get_post(
#     preset: str = None, postid: int = None, user: User = Depends(OAUTH2)
# ):
#     if preset:
#         post = await user.get_post(preset=preset)
#     elif postid:
#         post = await user.get_post(id=postid)
#     else:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST)
#     if post is None:
#         raise HTTPException(status.HTTP_404_NOT_FOUND)
#     return Response(content=await post.show(), media_type="image/jpeg")

# @postRouter.post("/")
# async def create_post(
#     files: list[UploadFile] = File(...),
#     caption: str | None = Form(None),
#     kwargs: dict[str, int | str | list[str]] | dict = Form(default=dict()),
#     preset: str = Form(...),
#     thumbnail: UploadFile | None = File(None),
#     disable_likes: bool = Form(True),
#     user: User = Depends(OAUTH2),
# ):

#     post = Post(
#         user=user,
#         content=[PostMedia(media=f.read(), mime=f.content_type) for f in files],
#     )
#     post.kwargs = PostData(caption_text=caption, **kwargs)

#     post.preset = preset
#     post.thumbnail = await thumbnail.read() if thumbnail else None
#     post.disable_likes = disable_likes
#     post.status = Post.Status.UNBUILT
#     await post.save()
#     return await POST_PYDANTIC.from_tortoise_orm(post)

# # @postRouter.patch("/")
# # async def update_post(
# #     postid: int,
# #     caption: str | None = Form(None),
# #     kwargs: str | None = Form(None),
# #     preset: str | None = Form(None),
# #     engine: int | None = Form(None),
# #     thumbnail: UploadFile | None = File(None),
# #     user: User = Depends(OAUTH2),
# # ):

# #     if (post := await user.get_post(id=postid)) is None:
# #         raise HTTPException(status.HTTP_404_NOT_FOUND)
# #     match post.status:
# #         case Post.Status.UNBUILT:
# #             pass
# #         case Post.Status.WAITING:
# #             await delete_post(postid)
# #         case _:
# #             raise HTTPException(status.HTTP_403_FORBIDDEN)

# #     if caption is not None:
# #         post.rawcaption = caption
# #     if kwargs is not None:
# #         post.rawkwargs = kwargs
# #     if preset is not None:
# #         post.preset = preset
# #     if engine is not None:
# #         post.engine = engine
# #     if thumbnail is not None:
# #         post.thumbnail = await thumbnail.read()
# #     return await post.save()

# @postRouter.delete("/")
# async def delete_post(postid: int, user: User = Depends(OAUTH2)):
#     if (post := await user.get_post(id=postid)) is None:
#         raise HTTPException(status.HTTP_404_NOT_FOUND)
#     match post.status:
#         case Post.Status.UNBUILT:
#             await post.delete()
#             return "Post deleted."
#         case Post.Status.WAITING:
#             await post.build_undo()
#             return f"Post ( id={post.id} ) delegated to {Post.Status.UNBUILT}"
#         case _:
#             raise HTTPException(status.HTTP_403_FORBIDDEN)
