from __future__ import annotations

import io
import json
import typing
from datetime import datetime
from enum import Enum
from random import Random

import instagrapi
import instagrapi.exceptions
import instagrapi.types
from app.api.instagram.models.schemas import (
    PostData,
    PostMedia,
    UserConfig,
    UserMetadataExtra,
)
from app.api.instagram.utilities import generate_new_device
from app.core.base.base_models import BaseDB, BaseUser
from app.utils.cleanup import TrashManager
from tortoise import fields


class UserMetadata(BaseDB):
  followers: list[int] = fields.JSONField()
  following: list[int] = fields.JSONField()
  requests: list[int] = fields.JSONField()
  
  extra: UserMetadataExtra = fields.JSONField(  # type: ignore[assignment]
      null=True,
      encoder=lambda x: x.json(),  # try models_as_dict=False if doesnt work
      decoder=lambda x: UserMetadataExtra.parse_raw(x),
      validators=[lambda x: UserMetadataExtra.validate(x)],
  )
  
  user: fields.OneToOneRelation[User] = fields.OneToOneField(
      model_name="models.User",
      on_delete=fields.CASCADE,
      related_name="metadata",
      to_field="id",
  )


class User(BaseUser):
  device: dict[
      str,
      typing.Any] = fields.JSONField(null=True,
                                     default=generate_new_device)
  anime: str = fields.CharField(max_length=128)      # fandom viable
  icon: bytes = fields.BinaryField()
  captions: dict[str, list[str]] = fields.JSONField()
  hashtags: dict[str, list[str]] = fields.JSONField()
  location: dict[str, int] = fields.JSONField()
  usertags: dict[str, int] = fields.JSONField()
  
  config: UserConfig = fields.JSONField(             # type: ignore[assignment]
      null=True,
      encoder=lambda x: x.json(),
      decoder=lambda x: UserConfig.parse_raw(x),
      validators=[lambda x: UserConfig.validate(x)],
  )
  
  metadata: fields.OneToOneRelation["UserMetadata"]  # check for nullablitiy
  
  post: fields.ForeignKeyRelation["Post"]
  
  def __init__(self, **kwargs: typing.Any) -> None:
    super().__init__(**kwargs)
    self.session = instagrapi.Client(self.device)
  
  async def to_json(self) -> bytes:
    
    class JSONEncoder(json.JSONEncoder):
      
      def default(self, obj):
        if isinstance(obj, bytes):
          return {
              "_type": "bytes",
              "encoding": "utf-8",
              "value": obj.decode("utf-8"),
          }
        return json.JSONEncoder.default(self, obj)
    
    file = io.BytesIO()
    file.write(
        json.dumps(await self.to_dict(),
                   cls=JSONEncoder).encode("utf-8")
    )
    
    return file.getvalue()
  
  @classmethod
  async def from_json(cls, file: bytes, /) -> User:
    
    class JSONDecoder(json.JSONDecoder):
      
      def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(
            self,
            object_hook=self.object_hook,
            *args,
            **kwargs
        )
      
      def object_hook(self, obj):
        if "_type" not in obj:
          return obj
        type = obj["_type"]
        if type == "bytes":
          return obj["value"].encode(obj["encoding"])
        return obj
    
    return cls(
        **json.loads(file,
                     cls=JSONDecoder)
    )                                                # use io.bytesio if doesnt work
  
  async def get_post(self, **kwargs) -> Post | None:
    return await self.post.filter(**kwargs).order_by("modified_at").first()
  
  async def login(self, password: str):
    session = self.session
    try:
      session.login(username=self.username, password=password)
    except instagrapi.exceptions.LoginRequired:
      session.relogin()
      self.device = session.settings
      await self.save()
    if name := self.config.username_change:
      try:
        session.account_edit(username=name)
      except Exception as e:
        ...
  
  class Meta:
    abstract = False
    table = "InstagramUser"
    table_description = "data about instagram accounts"


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
  
  content: list[PostMedia] = fields.JSONField(
      encoder=lambda x: x.json(),
      decoder=lambda x: PostMedia.parse_raw(x),
      validators=[lambda x: PostMedia.validate(x)],
  )
  kwargs: PostData = fields.JSONField(  # type: ignore[assignment]
      encoder=lambda x: x.json(),
      decoder=lambda x: PostData.parse_raw(x),
      validators=[lambda x: PostData.validate(x)],
  )
  
  api: Api = fields.CharEnumField(Api, null=False, max_length=10)
  preset: str = fields.CharField(max_length=128, null=False)
  thumbnail: bytes | None = fields.BinaryField(null=True, default=None)
  # set by build method
  caption: str = fields.TextField(null=True)
  hashtags: str | None = fields.TextField(null=True, default=None)
  location: int | None = fields.IntField(null=True, default=None)
  usertags: list[int] | None = fields.JSONField(null=True)
  # tweaks with default values
  disable_likes: bool = fields.BooleanField(
      default=True
  )                                                                   # type: ignore[assignment]
  
  status: Status = fields.CharEnumField(Status, default=Status.UNDEFINED)
  date_posted: datetime = fields.DatetimeField()
  
  user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
      "models.User",
      related_name="posts"
  )
  
  class Meta:
    table = "InstagramPost"
    table_description = "data about instagram post by accounts"
  
  async def build(self) -> None:
    if self.status != self.Status.UNBUILT:
      raise ValueError("status must be unbuilt but was %s" % self.status)
    
    from translate import Translator
    
    self.caption = "\n".join(
        [
            each_line.replace(
                "${text}",
                self.kwargs.caption_text
            ).replace(
                "${source}",
                self.kwargs.extra.get("source",
                                      "unknown/comment")
            ).replace(
                "${translated_japanese_text}",
                Translator("ja").translate(self.kwargs.caption_text),
            ).replace("${username}",
                      self.user.username)
            for each_line in self.user.captions.copy()[self.preset]
        ]
    )
    
    self.hashtags = " ".join(
        [
            tag for option in self.kwargs.hashtags_opts
            for tag in self.user.hashtags.get(option,
                                              tuple())
            if option in self.user.hashtags.keys()
        ]
    )
    
    self.location = self.user.location[self.kwargs.location_string]
    
    self.usertags = Random().sample(
        list(self.user.usertags.values()),
        self.kwargs.usertags_amount
    )
    
    self.status = self.Status.WAITING
    
    return await self.save()
  
  async def build_undo(self) -> None:
    (
        self.api,
        self.content_files,
        self.content_types,
        self.caption,
        self.hashtags,
        self.usertags,
        self.location,
    ) = ( None for _ in range(7) )
    
    self.status = Post.Status.UNBUILT
    await self.save()
  
  async def post(
      self,
      session: instagrapi.Client,
      trash: TrashManager | None = None
  ) -> str:
    if not trash:
      trash = TrashManager()
    
    upload_kwargs: dict[str, typing.Any] = {}
    
    upload_kwargs["path"] = [
        trash.save(o.media,
                   f"{i}.{o.mime.split('/')[-1]}") for i,
        o in enumerate(self.content)
    ]
    if len(upload_kwargs["path"]) != 1:
      upload_kwargs["path"] = upload_kwargs["path"][0]
    
    upload_kwargs["caption"] = self.caption
    
    if self.usertags:
      upload_kwargs["usertags"] = [
          instagrapi.types.Usertag(
              user=session.user_short_gql(userid),
              x=Random().random(),
              y=Random().random(),
          ) for userid in self.usertags
      ]
    
    if self.location:
      upload_kwargs["location"] = session.location_info(self.location)
                                                                      # classmethod
    upload_kwargs["extra_data"] = dict(
        like_and_view_counts_disabled=int(self.disable_likes)
    )
    if self.thumbnail and self.api in (Post.Api.REELS, Post.Api.VIDEO):
      upload_kwargs["thumbnail"] = trash.save(self.thumbnail, "t.jpg")
    
    api_upload: typing.Callable[
        [],
        instagrapi.types.Media] = getattr(session,
                                          f"{self.api}_upload")
    
    POST = api_upload(**upload_kwargs)
    await self.update_from_dict(dict(status=Post.Status.POSTED)).save()
    if self.hashtags:
      COMMENT = session.media_comment(POST.id, "Tags")
      session.media_comment(POST.id, self.hashtags, int(COMMENT.pk))
    
    return "https://www.instagram.com/p/" + POST.id
  
  def repost(self):
    pass
  
  def show(self) -> bytes:
    return bytes()
