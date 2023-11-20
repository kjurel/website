from __future__ import annotations

import io
import json
import typing as t
from datetime import datetime
from enum import Enum
from random import Random

import instagrapi
import instagrapi.exceptions
import instagrapi.types
import pydantic
from tortoise import fields
from tortoise.contrib.pydantic.creator import pydantic_model_creator

from ..core.base.base_models import BaseDB, BaseUser
from ..schemas.instagram import DeviceInputs, PostData, PostMedia, UserConfig
from ..utilities import TrashManager


class InstagramUser(BaseUser):
    device: dict[str, t.Any] = fields.JSONField(  # type: ignore[assignment]
        default=lambda: InstagramUser.generate_new_device(), null=True
    )
    icon: bytes = fields.BinaryField()  # type: ignore[assignment]
    captions: dict[str, list[str]] = fields.JSONField()  # type: ignore[assignment]
    hashtags: dict[str, list[str]] = fields.JSONField()  # type: ignore[assignment]
    location: dict[str, int] = fields.JSONField()  # type: ignore[assignment]
    usertags: dict[str, int] = fields.JSONField()  # type: ignore[assignment]

    config: UserConfig = fields.JSONField(  # type: ignore[assignment]
        null=True,
        default=lambda: UserConfig().json(),
        encoder=lambda x: x.json(),
        decoder=lambda x: UserConfig.parse_raw(x),
        validators=[lambda x: UserConfig.validate(x)],
    )

    post: fields.ForeignKeyRelation["InstagramPost"]


    def __init__(self, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)
        self.session = instagrapi.Client(self.device)

    @staticmethod
    def generate_new_device(D: DeviceInputs | None = None):
        L = instagrapi.Client()
        vD = D or {"country": "IN", "code": 356, "locale": "en_IN", "tz": 5.5}
        L.set_country(str(vD["country"]))
        L.set_country_code(int(vD["code"]))
        L.set_locale(str(vD["locale"]))
        L.set_timezone_offset(int(float(vD["tz"]) * 3600))

        return L.get_settings()

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
        file.write(json.dumps(await self.to_dict(), cls=JSONEncoder).encode("utf-8"))

        return file.getvalue()

    @classmethod
    async def from_json(cls, file: bytes, /) -> InstagramUser:
        class JSONDecoder(json.JSONDecoder):
            def __init__(self, *args, **kwargs):
                json.JSONDecoder.__init__(
                    self, object_hook=self.object_hook, *args, **kwargs
                )

            def object_hook(self, obj):
                if "_type" not in obj:
                    return obj
                type = obj["_type"]
                if type == "bytes":
                    return obj["value"].encode(obj["encoding"])
                return obj

        return cls(**json.loads(file, cls=JSONDecoder))  # use io.bytesio if doesnt work

    async def get_post(self, **kwargs) -> InstagramPost | None:
        return await self.post.filter(**kwargs).order_by("modified_at").first()

    async def login(self, password: str):
        session = self.session
        try:
            session.login(username=self.username, password=password)
        except instagrapi.exceptions.LoginRequired:
            session.relogin()
            self.device = session.settings
            await self.save()

    class Meta:
        abstract = False
        table = "InstagramUser"
        table_description = "data about instagram accounts"


class InstagramPost(BaseDB):
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

    content: list[PostMedia] = fields.JSONField(  # type: ignore[assignment]
        encoder=lambda x: x.json(),
        decoder=lambda x: pydantic.parse_raw_as(list[PostMedia], x),
        validators=[lambda x: PostMedia.validate(x)],
    )
    kwargs: PostData = fields.JSONField(  # type: ignore[assignment]
        encoder=lambda x: x.json(),
        decoder=lambda x: PostData.parse_raw(x),
        validators=[lambda x: PostData.validate(x)],
    )

    api = fields.CharEnumField(Api, null=True, max_length=10)
    preset = fields.CharField(max_length=128, null=False)
    thumbnail = fields.BinaryField(null=True, default=None)
    # set by build method
    caption: t.Optional[str] = fields.TextField(null=True)  # type: ignore[assignment]
    hashtags: t.Optional[str] = fields.TextField(
        null=True, default=None
    )  # type: ignore[assignment]
    location: t.Optional[int] = fields.IntField(
        null=True, default=None
    )  # type: ignore[assignment]
    usertags: t.Optional[list[int]] = fields.JSONField(null=True)  # type: ignore[assignment]
    # tweaks with default values
    disable_likes: bool = fields.BooleanField(default=True)  # type: ignore[assignment]

    status = fields.CharEnumField(Status, default=Status.UNDEFINED, max_length=5)
    date_posted: datetime = fields.DatetimeField()  # type: ignore[assignment]

    user: fields.ForeignKeyRelation[InstagramUser] = fields.ForeignKeyField(
        "models.InstagramUser", related_name="posts"
    )

    class Meta:
        table = "InstagramPost"
        table_description = "data about instagram post by accounts"

    async def build(self) -> None:
        if self.status != self.Status.UNBUILT:
            raise ValueError("status must be unbuilt but was %s" % self.status)

            # from translate import Translator

        self.caption = "\n".join(
            [
                each_line.replace("${text}", self.kwargs.caption_text).replace(
                    "${source}", self.kwargs.extra.get("source", "unknown/comment")
                )
                # .replace(
                #     "${translated_japanese_text}",
                #     Translator("ja").translate(self.kwargs.caption_text),
                # )
                .replace("${username}", self.user.username)
                for each_line in self.user.captions.copy()[self.preset]
            ]
        )

        self.hashtags = " ".join(
            [
                tag
                for option in self.kwargs.hashtags_opts
                for tag in self.user.hashtags.get(option, tuple())
                if option in self.user.hashtags.keys()
            ]
        )

        self.location = self.user.location[self.kwargs.location_string]

        self.usertags = Random().sample(
            list(self.user.usertags.values()), self.kwargs.usertags_amount
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
        ) = (None for _ in range(7))

        self.status = InstagramPost.Status.UNBUILT
        await self.save()

    async def post(
        self, session: instagrapi.Client, trash: TrashManager | None = None
    ) -> str:
        if not trash:
            trash = TrashManager()

        upload_kwargs: dict[str, t.Any] = {}

        upload_kwargs["path"] = [
            trash.save(o.media, f"{i}.{o.mime.split('/')[-1]}")
            for i, o in enumerate(self.content)
        ]
        if len(upload_kwargs["path"]) != 1:
            upload_kwargs["path"] = upload_kwargs["path"][0]

        upload_kwargs["caption"] = self.caption

        if self.usertags:
            upload_kwargs["usertags"] = [
                instagrapi.types.Usertag(
                    user=session.user_short_gql(str(userid)),
                    x=Random().random(),
                    y=Random().random(),
                )
                for userid in self.usertags
            ]

        if self.location:
            upload_kwargs["location"] = session.location_info(self.location)
            # classmethod
        upload_kwargs["extra_data"] = dict(
            like_and_view_counts_disabled=int(self.disable_likes)
        )
        if self.thumbnail and self.api in (
            InstagramPost.Api.REELS,
            InstagramPost.Api.VIDEO,
        ):
            upload_kwargs["thumbnail"] = trash.save(self.thumbnail, "t.jpg")

        api_upload: t.Callable[[], instagrapi.types.Media] = getattr(
            session, f"{self.api}_upload"
        )

        POST = api_upload(**upload_kwargs)
        await self.update_from_dict(dict(status=InstagramPost.Status.POSTED)).save()
        if self.hashtags:
            COMMENT = session.media_comment(POST.id, "Tags")
            session.media_comment(POST.id, self.hashtags, int(COMMENT.pk))

        return "https://www.instagram.com/p/" + POST.id

    def repost(self):
        pass

    def show(self, **kwargs) -> bytes:
        size = t.NamedTuple("size", [("width", int), ("height", int)])

        def loader(x: list[bytes]):
            return [
                image.Ex.Image.open(io.BytesIO(i))  # if isinstance(typecheck(i), image)
                # else image.Ex.Image.fromarray(video.Load.frombytes(i).vid.get_frame())
                for i in x
            ]

        size = cls.size(1080, 1920)
        bg = image.Ex.Image.new("RGB", size, "#333333")
        borders = 60

        def status(background: image.Ex.Image.Image):
            font = Asset.font_loader("Yantramanav-Regular.ttf", borders)
            text = kwargs["status"].capitalize()
            image.Ex.ImageDraw.Draw(background).text(
                (size.width - font.getsize(text)[0], 0), text, "white", font
            )

        def media_composite(
            bgcomp: image.Ex.Image.Image, medias: list[image.Ex.Image.Image]
        ):
            gap = 10
            mediasPerLine = int(len(medias) / 2)
            mediaSize = cls.size(
                (
                    k := round(
                        (bgcomp.width - (mediasPerLine + 1) * gap) / mediasPerLine
                    )
                ),
                k,
            )

            mediacomp = image.Ex.Image.new(
                "RGBA", (bgcomp.width - gap * 2, 394), (0, 0, 0, 0)
            )
            cords = [
                ((mediaSize.width + gap) * i, 0)
                if i + 1 < mediasPerLine
                else ((mediaSize.width + gap) * i, mediaSize.height + gap)
                for i in range(len(medias))
            ]
            for cord, img in zip(cords, [i.resize(mediaSize) for i in medias]):
                mediacomp.paste(img, cord)
            image(img=mediacomp).add_rounded_corners(25)
            bgcomp.paste(mediacomp, (gap, gap), mediacomp)
            return gap, (mediaSize.height + gap) * 2 + gap  # elemnt starter

        def rawdata_composite(rawcomp: image.Ex.Image.Image, m: typing.Any):
            starter = media_composite(rawcomp, m)
            font = Asset.font_loader("Yantramanav-Regular.ttf", borders)
            image.Ex.ImageDraw.Draw(rawcomp).text(
                starter,
                f"""Content-types: {kwargs['rawcontent_types']}
        Caption: \"{kwargs['rawcaption']}\"
        Kwargs: {kwargs['rawkwargs']}""",
                font=font,
            )

        def metadata_composite(
            bldcomp: image.Ex.Image.Image,
            thumbnail: image.Ex.Image.Image,
            m: typing.Any,
        ):
            starter = media_composite(bldcomp, m)
            gap = starter[0]
            image(img=thumbnail).resize(
                "height", bldcomp.height - gap - starter[1]
            ).add_rounded_corners(25)
            bldcomp.paste(
                thumbnail, ((k := bldcomp.width - gap - thumbnail.width), starter[1])
            )
            x_boud = k - gap
            font = Asset.font_loader("Yantramanav-Regular.ttf", borders)
            lines = (
                f"DISABLED_LIKES: {kwargs['disable_likes']}",
                f"Api:{kwargs['api']}, Preset:{kwargs['preset']}, Engine:{kwargs['engine']}",
                f"Caption: {kwargs['caption']}",
                f"Hashtags: {kwargs['hashtags']}",
                f"Usertags: {kwargs['usertags']}",
                f"Location: {kwargs['location']}",
            )
            text = image.wrap_text("\n".join(lines), font, x_boud)
            image.Ex.ImageDraw.Draw(bldcomp).text(starter, text, "white", font)

        status(bg)
        raw_composite = image.Ex.Image.new("RGBA", (1020, 1020), (0, 0, 0, 0))
        rawdata_composite(raw_composite, loader(kwargs["rawcontent_files"]))
        image(img=raw_composite).add_rounded_corners(
            25, ol_kwargs={"outline": "white", "width": 5}
        )
        bld_composite = image.Ex.Image.new("RGBA", (1020, 1020), (0, 0, 0, 0))
        metadata_composite(
            bld_composite,
            image.Ex.Image.open(kwargs["thumbnail"]),
            loader(kwargs["content_files"]),
        )
        image(img=bld_composite).add_rounded_corners(
            25, ol_kwargs={"outline": "white", "width": 5}
        )

        return image(img=bg).get_bytes
        return bytes()


USER_PYDANTIC = pydantic_model_creator(
    InstagramUser, name="InstagramUser", exclude_readonly=True
)
POST_PYDANTIC = pydantic_model_creator(
    InstagramPost, name="InstagramPost", exclude_readonly=True
)
