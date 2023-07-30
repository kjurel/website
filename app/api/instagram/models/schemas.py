from __future__ import annotations

import functools
import json
import typing
from datetime import datetime

import pydantic
from app.core.base.base_json import BaseJSONDecoder


class UserMetadataExtra(pydantic.BaseModel):
  cursor_follower: str
  refresh: dict[str, datetime] | None = None
  
  class Config:
    extra = "ignore"
    json_encoders = {
        datetime:
        lambda obj: dict(_type=type(obj).__name__,
                         value=obj.timestamp())
    }
    json_loads = functools.partial(json.loads, cls=BaseJSONDecoder)


class UserConfig(pydantic.BaseModel):
  username_change: str
  farms: dict[str, int]
  quality: bool = False
  interaction_session_limit: int


class PostMedia(pydantic.BaseModel):
  media: bytes
  mime: str
  
  class Config:
    extra = "forbid"
    json_encoders = {
        bytes:
        lambda obj: dict(_type=type(obj).__name__,
                         value=obj.decode("utf-8"))
    }
    json_loads = functools.partial(json.loads, cls=BaseJSONDecoder)


class PostData(pydantic.BaseModel):
  caption_text: str
  hashtags_opts: list[str]
  location_string: str
  usertags_amount: int
  extra: dict[str, typing.Any]
  
  class Config:
    extra = "ignore"
    smart_union = True
  
  @pydantic.root_validator(pre=True)
  def build_extra(cls, values: dict[str, typing.Any]) -> dict[str, typing.Any]:
    all_required_field_names = {
        field.alias
        for field in cls.__fields__.values() if field.alias != "extra"
    }                                                                  # to support alias
    
    extra: dict[str, typing.Any] = {}
    for field_name in list(values):
      if field_name not in all_required_field_names:
        extra[field_name] = values.pop(field_name)
    values["extra"] = extra
    return values
