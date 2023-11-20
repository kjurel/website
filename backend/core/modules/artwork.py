from __future__ import annotations

import io
import os
import re
import typing as t
from zipfile import ZipFile

import numpy as np
import pydantic
# from .editing import image
import requests
from PIL.Image import Image


class image(pydantic.BaseModel):
  EXTENSION: t.ClassVar[str] = "jpg"
  SIZE: t.ClassVar[t.Dict[str, t.Tuple[int, int]]] = {
      "1:1": ( 1920, 1920 ),
      "4:5": ( 1920, 2400 ),
      "16:9": ( 1920, 1080 ),
  }
  RENDER_SETTINGS: t.ClassVar[t.Dict[str, t.Any]] = {
      "fp": None,
      "format": "JPEG",
      "resample": 1,
  }                                                                                    # ANTIALIAS
  img: Image
  
  def __repr__(self) -> str:
    attribs = [ f"{k}: {v}" for k, v in self.img.__dict__.items() ]
    return f"{self.__class__.__name__}({', '.join(attribs)})"
  
  def __eq__(self, other) -> bool:
    if isinstance(other, self.__class__):
      return not self.Ex.ImageChops.difference(self.img, other.img).getbbox()
    return False
  
  class Config:
    extra = "forbid"
    smart_union = True
    arbitrary_types_allowed = True
  
  class Ex:
    from PIL import (Image, ImageChops, ImageDraw, ImageFilter, ImageFont,
                     UnidentifiedImageError)
  
  @property
  def get_copy(self) -> Ex.Image.Image:
    return self.img.copy()
  
  @property
  def get_bytes(self) -> bytes:
    bt = io.BytesIO()
    kwgs = self.RENDER_SETTINGS.copy()
    kwgs["fp"] = bt
    self.img.save(**kwgs)
    return bt.getvalue()
  
  class OrientationChecker:
    
    def __init__(self, im: image) -> None:
      self.im = im
      self.isPotrait = self.im.img.height > self.im.img.width
      self.isLandscape = self.im.img.height < self.im.img.width
      self.isSquare = not self.isPotrait and not self.isLandscape
  
  @property
  def orientation(self) -> image.OrientationChecker:
    return self.OrientationChecker(self)
  
  def blur(self, blur_radius: float):
    """Applies gaussian blur to the image"""
    self.img = self.img.filter(self.Ex.ImageFilter.GaussianBlur(blur_radius))
    return self
  
  def crop(self, size: tuple[int, int], force_method: t.Optional[str] = None):
    """Crops the image to the given size, while maintainig the ascept ratio"""
    x, y = (round(value / 2) for value in self.img.size)
    width, height = size
    if force_method and force_method == "from center":
                                                                                       # crops the center of the image as per the provided size parameter
      x, y = (round(value) for value in (x - width / 2, y - height / 2))
    elif (force_method == "protect height"
          ) or (force_method is None and self.orientation.isLandscape):
                                                                                       # doesnt crop the height, works good for lanscape images
      im = self.resize("height", height).get_copy
      x, y = (round(value) for value in ((im.width - width) / 2, 0))
    elif force_method == "protect width" or (
        force_method is None and self.orientation.isPotrait
    ):
                                                                                       # doesnt crop the width, works good for potrait images
      im = self.resize("width", width).get_copy
      x, y = (round(value) for value in ( 0, (im.height - height) / 2 ))
    else:
      raise ValueError("Invalid method was passed.")
    box = ( x, y, x + width, y + height )
    self.img = im.crop(box)
    return self
  
  def resize(self, parameter: t.Literal["height", "width"], parameter_value: int):
    """Resizes the image, accodring to a parameter, maitatining the aspect ratio"""
    if parameter == "height":
      new_height = parameter_value
      new_width = new_height * self.img.width / self.img.height
    elif parameter == "width":
      new_width = parameter_value
      new_height = new_width * self.img.height / self.img.width
    else:
      raise ValueError("Invalid parameter was passed.")
    size = round(new_width), round(new_height)
    self.img = self.img.resize(size, self.Ex.Image.ANTIALIAS)
    return self
  
  def add_rounded_corners(
      self,
      edge_radius: int,
      return_mask: bool = False,
      ol_kwargs: dict[str, float | str] = None,
  ):
    """Applies round corners to the image.
        The roundedness is relative to the size of the image.
        Enabling `return_mask` will break the chain."""
    imgmask = self.img.getchannel("A")
    crvmask = self.Ex.Image.new("L", self.img.size, "black")
    self.Ex.ImageDraw.Draw(crvmask).rounded_rectangle((( 0, 0 ), imgmask.size),
                                                      edge_radius,
                                                      "white")
    mask = self.Ex.Image.composite(imgmask, crvmask, crvmask)
    self.img.putalpha(mask.convert("L"))
    if ol_kwargs is not None:                                                          # {"outline":None, "width":None}
      outline = self.Ex.Image.new("RGBA", mask.size, ( 0, 0, 0, 0 ))
      self.Ex.ImageDraw.Draw(outline).rounded_rectangle((( 0, 0 ), mask.size),
                                                        edge_radius, ( 0, 0, 0, 0 ),
                                                        **ol_kwargs)
      self.img.paste(outline, ( 0, 0 ), outline)
    return self if not return_mask else image(img=mask)
  
  def add_text(
      self,
      xy: tuple[float, float],
      text: str,
      font: Ex.ImageFont.ImageFont,
      angle: float = 0,
  ):
    """Applies text to the image, the text can be customised.
        The angle of rotation is in anti - clockwise direction."""
    w, h = (attr + 5 for attr in font.getsize(text))
    mask = self.Ex.Image.new("RGBA", ( w, h ), ( 0, 0, 0, 0 ))
    self.Ex.ImageDraw.Draw(mask).text(( 0, 0 ),
                                      text,
                                      "#FFFFFF",
                                      font,
                                      stroke_width=3,
                                      stroke_fill="#000000")
    mask = mask.rotate(
        angle, resample=self.Ex.Image.ANTIALIAS, expand=True, fillcolor=( 0, 0, 0, 0 )
    )
    self.img.paste(mask, xy, mask)
    return self
  
  def set_ratio(self, ratio: str, background: typing.Literal["solid", "blur"]) -> image:
    size = self.SIZE[ratio]
    
    if self.orientation.isSquare:
      self.img = self.img.resize(size, self.Ex.Image.ANTIALIAS)
      return self
    
    larger_proportion: typing.Literal[
        "height", "width"] = ("height" if self.orientation.isPotrait else "width")
    flag: typing.Literal[0, 1] = 1 if self.orientation.isPotrait else 0
    
    if background == "solid":
      img_matrix = np.array(self.img)
      avg_list = list()
      rows, cols, _ = img_matrix.shape
      for index in range(10):
        avg_list.append(list(np.average(img_matrix[index], axis=0)))                   # top
        avg_list.append(list(np.average(img_matrix[rows - index - 1], axis=0)))        # bottom
        avg_list.append(list(np.average(img_matrix[...][0], axis=0)))                  # left
                                                                                       # rigth
        try:
          avg_list.append(list(np.average(img_matrix[...][cols - index - 1], axis=0)))
        except Exception as e:
          e
      avg_color = [round(ele) for ele in np.average(avg_list, axis=0)]
      bg = self.Ex.Image.new("RGB", size, tuple(avg_color))
      fg = image(img=self.get_copy).resize(larger_proportion, size[flag]).img
      cord = (
          self.orientation.isPotrait * round((size[0] - fg.width) / 2),
          self.orientation.isLandscape * round((size[1] - fg.height) / 2),
      )
      bg.paste(fg, cord)
      img = bg
    
    elif background == "blur":
      bg = image(img=self.get_copy).crop(size).blur(20).img
      fg = image(img=self.get_copy).resize(larger_proportion, size[flag]).img
      cord = (
          self.orientation.isPotrait * round((size[0] - fg.width) / 2),
          self.orientation.isLandscape * round((size[1] - fg.height) / 2),
      )
      bg.paste(fg, cord)
      img = bg
    
    else:
      ValueError("Invalid background passed")
    self.img = img
    return self
  
  @staticmethod
  def wrap_text(text: str, font: Ex.ImageFont.ImageFont, max_width: int) -> str:
    """Returns a string for given text and font of wrapped lines"""
    lines = []
    line = ""
    i = 0
    if font.getsize(text)[0] <= max_width:
      lines.append(text)
    else:
      words = text.split(" ")
                                                                                       # append every word to a line while its width is shorter than the image width
      while i < len(words):
        while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
          line = line + words[i] + " "
          i += 1
        if not line:
          line = words[i]
          i += 1
        lines.append(line)
    return "\n".join(lines)


class video(pydantic.BaseModel):
  EXTENSION: typing.ClassVar[str] = "mp4"
  SIZE: typing.ClassVar[dict[str, tuple[int, int]]] = {
      "banner.content.size": ( 1820, 1024 )
  }
  RENDER_SETTINGS: typing.ClassVar[dict[str, typing.Any]] = {
      "fps": 30,
      "codec": "libx264",
      "audio": True,
      "audio_codec": "aac",
      "temp_audiofile": "temp-audio.m4a",
      "remove_temp": True,
  }
  vid: Ex.VideoFileClip
  
  def __repr__(self) -> str:
    return f"{self.__class__.__name__}({', '.join([f'{k}: {v}' for k, v in self.vid.__dict__.items()])})"
  
  class Config:
    extra = "forbid"
    smart_union = True
    arbitrary_types_allowed = True
  
  class Ex:
    from moviepy.editor import CompositeVideoClip, ImageClip, VideoFileClip

    # CompositeVideoClip = CompositeVideoClip
    # ImageClip = ImageClip
    # VideoFileClip = VideoFileClip
  
  class OrientationChecker:
    
    def __init__(self, vi: video) -> None:
      self.vi = vi
      self.isPotrait: bool = self.vi.vid.size[1] > self.vi.vid.size[0]
      self.isLandscape: bool = self.vi.vid.size[1] < self.vi.vid.size[0]
      self.isSquare: bool = not self.isPotrait and not self.isLandscape
  
  @property
  def orientation(self) -> video.OrientationChecker:
    return self.OrientationChecker(self)
  
  class Load:
    
    @classmethod
    def frompath(cls, path: str):
      with open(path, "rb") as f:
        return cls.frombytes(f.read())
    
    @staticmethod
    def frombytes(byt: bytes):
      with open("t.mp4", "wb") as f:
        f.write(byt)
      retval = video(vid=video.Ex.VideoFileClip(filename="t.mp4"))
      os.remove("t.mp4")
      return retval
  
  @property
  def get_copy(self) -> Ex.VideoFileClip:
    return self.vid.copy()
  
  @property
  def get_bytes(self) -> bytes:
    # add preset="ultrafast" for faster writing
    self.vid.write_videofile(filename="t.mp4", **self.RENDER_SETTINGS)
    with open("t.mp4", "rb") as f:
      byt = f.read()
    os.remove("t.mp4")
    return byt
  
  def add_rounded_corners(self, edge_radius: int):
    """Applies round corners to the video"""
    mask = image(img=image.Ex.Image.new("RGB", self.vid.size)
                 ).add_rounded_corners(edge_radius, True)
    self.vid = self.vid.set_mask(
        self.Ex.ImageClip(np.array(mask.img.convert("RGB")), ismask=True)
    )
    return self
  
  def add_text(
      self, xy: tuple[float, float], text: str, font: image.Ex.ImageFont.ImageFont
  ):
    """Applies text to self object, the text can be customised.
        The angle of rotation is in anti - clockwise direction."""
    im = (
        image(img=image.Ex.Image.new("RGBA", self.vid.size, ( 0, 0, 0, 0 ))
              ).add_text(xy, text, font).get_copy
    )
    clip = video.Ex.ImageClip(np.array(im),
                              duration=self.vid.duration).set_fps(self.vid.fps)
    self.vid = video.Ex.CompositeVideoClip([self.vid, clip],
                                           use_bgclip=True,
                                           size=( 1920, 1920 ))
    return self


def typecheck(data: str | bytes) -> typing.Type[video | image]:
  # check if image only, no checks implemented for video
  
  try:
    image.Ex.Image.open(data) if isinstance(data, str) else image.Ex.Image.open(
        io.BytesIO(data)
    )
  except image.Ex.UnidentifiedImageError:
    return video
  else:
    return image


FONT_LINK = "https://www.cufonfonts.com/download/redirect/{}"
ICON_LINK = "https://img.icons8.com/color/480/000000/{}"

ICON_MAPPING = {
    "devianart": {
        "url": "devianart.png", "color": "#64DD17"
    },
    "instagram": {
        "url": "instagram-new--v1.png", "color": "#D71C61"
    },
    "reddit": {
        "url": "reddit.png", "color": "#D84315"
    },
    "twitter": {
        "url": "twitter--v1.png", "color": "#4CBAFF"
    },
}

FONT_MAPPING = {
    "Now-Regular.otf": "now",
    "ChangaOne-Regular.ttf": "changa-one",
    "LeagueSpartan-Bold.otf": "league-spartan",
    "Yantramanav-Light.ttf": "yantramanav",
    "Yantramanav-Regular.ttf": "yantramanav  ",
}


def font_loader(filename: str, size: int):
  fontName, familyName = filename.split(".")[0].split("-")
  url = FONT_LINK.format(
      "-".join(re.findall(r"[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))", fontName))
  ).lower()
  with requests.get(url) as r:
    r.raise_for_status()
    with ZipFile(io.BytesIO(r.content)) as zipfile:
      with zipfile.open(filename, mode="r") as f:
        return image.Ex.ImageFont.truetype(f, size)


def icon_loader(iconname: str):
  r = requests.get(ICON_LINK.format(ICON_MAPPING["url"][iconname]))
  return io.BytesIO(r.content)
