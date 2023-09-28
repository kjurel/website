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
