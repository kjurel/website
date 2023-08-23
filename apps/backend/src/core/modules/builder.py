from __future__ import annotations

import io
import random
import typing

import pydantic
from src.core.packages.artwork import font_loader, image, typecheck, video
from translate import Translator


class BuilderData(pydantic.BaseModel):
    username: str
    icon: image
    caption_text: str
    caption_statics: dict[str, list[str]]
    hashtags_opts: list[str]
    hashtags_statics: dict[str, list[str]]
    usertags_amount: int
    usertags_statics: dict[str, int]
    location_string: str
    location_statics: dict[str, int]

    @pydantic.validator("icon", pre=True)
    def validate_icon(cls, v):
        return image.Ex.Image.open(v) if isinstance(v, bytes) else v


class Builder(pydantic.BaseModel):
    _translator: Translator = pydantic.PrivateAttr(Translator("ja"))
    engine: tuple[str, int]
    media: list[image | video]
    data: BuilderData

    @pydantic.validator("media", pre=True)
    def validate_media(cls, v):
        def get_media(m: str | image | video | bytes) -> image | video:
            if isinstance(m, image) or isinstance(m, video):
                return m
            elif isinstance(m, (str, bytes)):
                if isinstance(typecheck(m), image):
                    return image.Ex.Image.open(m)
                else:
                    return (
                        video.Load.frompath(m)
                        if isinstance(m, str)
                        else video.Load.frombytes(m)
                    )
            else:
                raise TypeError

        if not isinstance(v, (str, bytes, image, video)):
            raise TypeError
        return [get_media(i) for i in v]

    @pydantic.validator("engine")
    def validate_engine(cls, v):
        if not isinstance(v, tuple):
            raise TypeError

        raise pydantic.ValidationError

    def content(self) -> tuple[list[bytes], list[str]]:
        attrname, attrindex = self.engine
        callback: typing.Callable[[Builder], list[image | video]]
        if (
            callback := getattr(self.__class__, f"{attrname}_content_type_{attrindex}")
        ) is None:
            raise ValueError
        stack: list[image | video] = callback(self)
        ## setting up api-call
        # if len(stack) == 1:
        #     if stack[0].EXTENSION == "jpg":
        #         self.api = "photo"
        #     elif stack[0].EXTENSION == "mp4":
        #         if stack[0].orientation.isPotrait:
        #             self.api = "clip"
        #         else:
        #             self.api = "video"
        # else:
        #     self.api = "album"
        retbytes = [x.get_bytes for x in stack]
        retexten = [x.EXTENSION for x in stack]
        return retbytes, retexten

    def captions(self) -> str:
        def get_line(line: str) -> str:
            line = line.replace("${text}", self.data.caption_text)
            line = line.replace(
                "${source}", self.extra.get("source", "unknown/comment")
            )
            line = line.replace(
                "${translated_japanese_text}",
                self._translator.translate(self.data.caption_text),
            )
            line = line.replace("${username}", self.data.username)
            return line

        return "\n".join(
            [
                get_line(each_line)
                for each_line in self.data.caption_statics[self.engine[0]]
            ]
        )

    def hashtags(self):
        retval: list[str] = list()
        for tag in self.data.hashtags_opts:
            if tag in self.data.hashtags_statics.keys():
                retval.extend(self.data.hashtags_statics[tag])

        return " ".join(retval)

    def usertags(self):
        all_usertags = list(self.data.usertags_statics.values())
        random.shuffle(all_usertags)

        return [x for i, x in enumerate(all_usertags) if i < self.data.usertags_amount]

    def location(self):
        return self.data.location_statics[self.data.location_string]

    def Polls_content_type_0(self) -> list[image]:
        imgs = [obj.img for obj in self.media if isinstance(obj, image)]

        COMP = image.Ex.Image.new("RGB", (1080, 1920), "black")
        BD = 4
        font = font_loader("Now-Regular.otf", 25)
        for im, offset in zip(imgs, (0, 960)):
            bg = (
                image(img=im.copy())
                .crop((1080 - BD * 2, 960 - BD * 2), "retain height")
                .add_rounded_corners(25)
                .get_copy
            )
            fg = (
                image(img=im.copy())
                .resize("height", 450)
                .add_rounded_corners(25)
                .get_copy
            )
            COMP.paste(
                bg.filter(image.Ex.ImageFilter.GaussianBlur(20)),
                (BD, BD + offset),
                bg,
            )
            COMP.paste(fg, (138, 255 + offset), fg)
            image.Ex.ImageDraw.Draw(COMP).text(
                (145, 670 + offset),
                f"@{self.data.username}",
                fill="white",
                font=font,
                stroke_fill="black",
                stroke_width=1,
            )
        return [image(img=COMP)]

    def Fanarts_content_type_0(self) -> list[image]:
        return [
            obj.set_ratio("1:1", "solid")
            for obj in self.media
            if isinstance(obj, image)
        ]

    def Fanarts_content_type_1(self) -> list[image]:  # bottom_bar
        def draw_box(draw: image.Ex.ImageDraw.ImageDraw):
            draw.rounded_rectangle(
                xy=(
                    (0 + BOX_OUTLINE_RADIUS, 1920 - BOX_HEIGHT),
                    (1920 - BOX_OUTLINE_RADIUS, 1920 + BOX_HEIGHT),
                ),
                radius=BOX_RADIUS,
                fill=(0, 0, 0, 210),
                outline="white",
                width=BOX_OUTLINE_RADIUS,
            )

        def draw_text(draw: image.Ex.ImageDraw.ImageDraw):
            draw.text((TEXT_RULER_X, TEXT_RULER_Y), "Created by ", "white", light_font)
            draw.text(
                (TEXT_RULER_X + light_font.getsize("Created by ")[0], TEXT_RULER_Y),
                aut,
                "white",
                dark_font,
            )
            draw.text(
                (1920 - TEXT_RULER_X - wooble_font.getsize(src)[0], TEXT_RULER_Y),
                src,
                "white",
                wooble_font,
            )

        def draw_icon(img: image.Ex.Image.Image):
            icon: image.Ex.Image.Image = getattr(Asset(), f"icon_{src}")
            icon = (
                image(img=icon.convert("RGBA"))
                .resize("height", ICON_SIZE)
                .add_rounded_corners(ICON_CORNER)
                .get_copy
            )

            img.paste(
                icon,
                (
                    1920
                    - TEXT_RULER_X
                    - wooble_font.getsize(src)[0]
                    - ICON_SIZE
                    - ICON_GAP,
                    1920 - ICON_GAP - ICON_SIZE,
                ),
                icon,
            )

        source: str = self.extra.get("source", "unknown/comment")
        src, aut = source.split("/")
        if src == "unknown":
            raise NotImplementedError()

        BOX_HEIGHT = 135
        BOX_RADIUS = 35
        BOX_OUTLINE_RADIUS = 0
        TEXT_SIZE = 100
        light_font = font_loader("Yantramanav-Light.ttf", TEXT_SIZE)
        dark_font = font_loader("Yantramanav-Regular.ttf", TEXT_SIZE)
        wooble_font = font_loader("ChangaOne-Regular.ttf", TEXT_SIZE)
        TEXT_RULER_X = 20
        TEXT_RULER_Y = round(
            1920
            - (BOX_HEIGHT / 2)
            - (light_font.getsize("Created by {}".format(source))[1] / 2)
        )
        ICON_CORNER = 10
        ICON_SIZE = 90
        ICON_GAP = round((1920 - TEXT_RULER_Y - ICON_SIZE) / 2)

        ims = [
            obj.set_ratio("1:1", "solid")
            for obj in self.media
            if isinstance(obj, image)
        ]
        for im in ims:
            draw = image.Ex.ImageDraw.Draw(im.img, "RGBA")
            draw_box(draw=draw)
            draw_text(draw=draw)
            draw_icon(img=im.img)

        return ims

    def Reels_content_type_0(self):
        return self.media
