<details>
  <summary>applications/instagram/routers - post routes</summary>
  
  ```python
    @postRouter.head("/")
    async def head_post(postid: int = None, preset: str = None, user: User = Depends(TokenAuth)):
        if preset: post = await user.get_post(preset=preset, status=Post.Status.UNBUILT)
        elif postid: post = await user.get_post(id=postid)
        else: raise HTTPException(status.HTTP_400_BAD_REQUEST)
        if post is None: raise HTTPException(status.HTTP_404_NOT_FOUND)

        match post.status:
            case Post.Status.UNBUILT:
                await post.build_withBuilder()
                return f"Build post {post.id}"
            case Post.Status.WAITING:
                session = user.login()
                lk = await user.post(session, post.id)
                return f"Posted at {lk}"
            case _: raise HTTPException(status.HTTP_403_FORBIDDEN)


    @postRouter.get("/", responses={200: {"content": {"image/jpeg": {}}}}, response_class=Response)
    async def get_post(preset: str = None, postid: int = None, user: User = Depends(TokenAuth)):
        if preset: post = await user.get_post(preset=preset)
        elif postid: post = await user.get_post(id=postid)
        else: raise HTTPException(status.HTTP_400_BAD_REQUEST)
        if post is None: raise HTTPException(status.HTTP_404_NOT_FOUND)
        return Response(content=await post.show(), media_type="image/jpeg")


    @postRouter.post("/")
    async def create_post(
        files: list[UploadFile] = File(...),
        caption: str | None = Form(None),
        kwargs: dict[str, int | str | list[str]] | None = Form(None),
        preset: str = Form(...),
        engine: int = Form(...),
        thumbnail: UploadFile | None = File(None),
        disable_likes: bool = Form(True),
        user: User = Depends(TokenAuth),
    ):

        post = Post(
            user=user,
            rawcontent_files=[await f.read() for f in files],
            rawcontent_types=[f.content_type for f in files],
        )
        if caption: post.rawcaption = caption
        if kwargs: post.rawkwargs = kwargs
        post.preset, post.engine = preset, engine
        if thumbnail: post.thumbnail = await thumbnail.read()
        post.disable_likes = disable_likes
        post.status = Post.Status.UNBUILT.value
        await post.save()
        return await POST_PYDANTIC.from_tortoise_orm(post)


    @postRouter.patch("/")
    async def update_post(
        postid: int,
        caption: str | None = Form(None),
        kwargs: str | None = Form(None),
        preset: str | None = Form(None),
        engine: int | None = Form(None),
        thumbnail: UploadFile | None = File(None),
        user: User = Depends(TokenAuth),
    ):

        if (post := await user.get_post(id=postid)) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        match post.status:
            case Post.Status.UNBUILT: pass
            case Post.Status.WAITING: await delete_post(postid)
            case _: raise HTTPException(status.HTTP_403_FORBIDDEN)

        if caption is not None: post.rawcaption = caption
        if kwargs is not None: post.rawkwargs = kwargs
        if preset is not None: post.preset = preset
        if engine is not None: post.engine = engine
        if thumbnail is not None: post.thumbnail = await thumbnail.read()
        return await post.save()


    @postRouter.delete("/")
    async def delete_post(postid: int, user: User = Depends(TokenAuth)):
        if (post := await user.get_post(id=postid)) is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        match post.status:
            case Post.Status.UNBUILT:
                await post.delete()
                return "Post deleted."
            case Post.Status.WAITING:
                (
                    post.api,
                    post.content_files,
                    post.content_types,
                    post.caption,
                    post.hashtags,
                    post.usertags,
                    post.location,
                ) = (None for _ in range(7))

                post.status = Post.Status.UNBUILT
                await post.save()
                return f"Post ( id={post.id} ) delegated to {Post.Status.UNBUILT}"
            case _: raise HTTPException(status.HTTP_403_FORBIDDEN)

````
</details>

<details>
<summary>applications/instagram/models - post models</summary>

```python
  class RawPost(BaseDB):
      content_files: list[bytes] = fields.JSONField(null=False)
      content_types: list[str] = fields.JSONField(null=False)
      caption: str = fields.TextField(null=False, default="")
      hashtags: list[str] = fields.JSONField(null=False, default=[])
      usertags: int = fields.SmallIntField(null=False, default=0)
      location: str = fields.CharField(128, null=False, default="")

      post: fields.OneToOneRelation[Post] = fields.OneToOneField(
          model_name="models.Post",
          on_delete=fields.CASCADE,
          related_name="raw",
          to_field="id",
      )

      class Config:
          abstract = False
          table = "RawInstagramPost"
          table_description = "raw post data"

      def build(self):
          pass


  class Post(BaseDB):
      class Status(Enum):
          UNDEFINED = "undefined"
          UNBUILT = "unbuilt"
          WAITING = "waiting"
          POSTED = "posted"

      class Api(Enum):
          PHOTO = "photo"
          VIDEO = "video"
          REELS = "clip"
          ALBUM = "album"

      preset: str = fields.CharField(max_length=20, null=False)
      engine: int = fields.IntField(null=False)
      thumbnail: bytes | None = fields.BinaryField(null=True, default=None)
      disable_likes: bool = fields.BooleanField(default=True)  # type:ignore

      # required by instagrapi client for posting
      api: str = fields.CharEnumField(Api, null=True)  # type:ignore
      content_files: list[bytes] = fields.JSONField(null=True)
      content_types: list[str] = fields.JSONField(null=True)
      caption: str = fields.TextField(null=True)
      usertags: list[int] | None = fields.JSONField(null=True)
      location: int | None = fields.IntField(null=True, default=None)
      hashtags: str | None = fields.TextField(null=True, default=None)

      status: str = fields.CharEnumField(Status, default=Status.UNDEFINED)  # type:ignore
      date_posted: datetime.datetime = fields.DatetimeField()

      post: fields.OneToOneRelation["RawPost"]  # check for nullablitiy
      user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
          "models.User", related_name="posts"
      )

      async def show(self) -> bytes:
          return Viewer.post(**(await self.to_dict()))

      async def build_withBuilder(self) -> None:
          if self.status != self.Status.UNBUILT:
              raise ValueError("status must be unbuilt but was %s" % self.status)

          B = Builder(
              engine=(self.preset, self.engine),
              media=self.rawcontent_files,
              icon=(await self.user).icon,
              userinfo=(await self.user).userinfo,
              **self.rawkwargs,
          )

          self.content_files, self.extensions = B.content()
          self.caption = B.captions(self.rawcaption)
          self.hashtags = B.hashtags(self.rawkwargs.get("hashtags", ["general"]))
          self.usertags = B.usertags(self.rawkwargs.get("usertags", 0))
          self.location = B.location()
          self.status = self.Status.WAITING.value

          return await self.save()

      class Meta:
          table = "InstagramPost"
          table_description = "data about instagram post by accounts"

      async def post(
          self, session: instagrapi.Client, trash: TrashManager | None = None
      ) -> str:
          if not trash:
              trash = TrashManager()

          upload_kwargs: dict[str, typing.Any] = {}

          upload_kwargs["path"] = [
              trash.save(b, f"{i}.{e.split('/')[-1]}")
              for i, (b, e) in enumerate(zip(self.content_files, self.content_types))
          ]
          if len(upload_kwargs["path"]) != 1:
              upload_kwargs["path"] = upload_kwargs["path"][0]

          upload_kwargs["caption"] = self.caption

          if self.usertags:
              upload_kwargs["usertags"] = [
                  instagrapi.types.Usertag(
                      user=session.user_short_gql(userid),
                      x=random.random(),
                      y=random.random(),
                  )
                  for userid in self.usertags
              ]

          if self.location:
              upload_kwargs["location"] = session.location_info(self.location)
          # classmethod
          upload_kwargs["extra_data"] = dict(
              like_and_view_counts_disabled=int(self.disable_likes)
          )
          if self.thumbnail and self.api in ("clip", "video"):
              upload_kwargs["thumbnail"] = trash.save(self.thumbnail, "t.jpg")

          api_upload: typing.Callable[[], instagrapi.types.Media] = getattr(
              session, f"{self.api}_upload"
          )

          POST = api_upload(**upload_kwargs)
          await self.update_from_dict(dict(status=Post.Status.POSTED.value)).save()
          if self.hashtags:
              COMMENT = session.media_comment(POST.id, "Tags")
              session.media_comment(POST.id, self.hashtags, int(COMMENT.pk))

          return "https://www.instagram.com/p/" + POST.id

      def repost(self):
          pass

````

</details>

<details>
<summary>CamelModel</summary>

```python
from pydantic import BaseModel
from humps import camelize


def to_camel(string):
    return camelize(string)


class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
class User(CamelModel):
    first_name: str
    last_name: str = None
    age: int
```

</details>
