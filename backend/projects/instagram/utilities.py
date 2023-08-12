from __future__ import annotations

import functools
import json
import typing
from datetime import datetime

import pydantic


def generate_new_device(
    D: dict[typing.Literal["country",
                           "code",
                           "locale",
                           "tz"],
            typing.Any] | None = None
):
  import os
  
  import instagrapi
  
  L = instagrapi.Client()
  D = D or json.loads(os.environ["INSTAGRAM_DEFAULT_LOCATION_SETTING"])
  
  L.set_country(D["country"])
  L.set_country_code(int(D["code"]))
  L.set_locale(D["locale"])
  L.set_timezone_offset(D["tz"] * 3600)
  
  return L.get_settings()


class Viewer:
  size = typing.NamedTuple("size", [( "width", int ), ( "height", int )])
  
  def user() -> bytes:
    return bytes()
  
  @classmethod
  def post(cls, **kwargs) -> bytes:
    
    def loader(x: list[bytes]):
      return [
          image.Ex.Image.open(io.BytesIO(i)
                              )                                                                                                                 # if isinstance(typecheck(i), image)
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
          (size.width - font.getsize(text)[0],
           0),
          text,
          "white",
          font
      )
    
    def media_composite(
        bgcomp: image.Ex.Image.Image,
        medias: list[image.Ex.Image.Image]
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
          "RGBA",
          (bgcomp.width - gap * 2,
           394),
          ( 0,
            0,
            0,
            0 )
      )
      cords = [
          ((mediaSize.width + gap) * i,
           0) if i + 1 < mediasPerLine else
          ((mediaSize.width + gap) * i,
           mediaSize.height + gap) for i in range(len(medias))
      ]
      for cord, img in zip(cords, [i.resize(mediaSize) for i in medias]):
        mediacomp.paste(img, cord)
      image(img=mediacomp).add_rounded_corners(25)
      bgcomp.paste(mediacomp, ( gap, gap ), mediacomp)
      return gap, (mediaSize.height + gap) * 2 + gap                                                                                            # elemnt starter
    
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
      image(img=thumbnail).resize("height",
                                  bldcomp.height - gap -
                                  starter[1]).add_rounded_corners(25)
      bldcomp.paste(
          thumbnail,
          ((k := bldcomp.width - gap - thumbnail.width),
           starter[1])
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
    raw_composite = image.Ex.Image.new("RGBA", ( 1020, 1020 ), ( 0, 0, 0, 0 ))
    rawdata_composite(raw_composite, loader(kwargs["rawcontent_files"]))
    image(
        img=raw_composite
    ).add_rounded_corners(25,
                          ol_kwargs={
                              "outline": "white",
                              "width": 5
                          })
    bld_composite = image.Ex.Image.new("RGBA", ( 1020, 1020 ), ( 0, 0, 0, 0 ))
    metadata_composite(
        bld_composite,
        image.Ex.Image.open(kwargs["thumbnail"]),
        loader(kwargs["content_files"]),
    )
    image(
        img=bld_composite
    ).add_rounded_corners(25,
                          ol_kwargs={
                              "outline": "white",
                              "width": 5
                          })
    
    return image(img=bg).get_bytes
