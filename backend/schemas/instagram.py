from __future__ import annotations

import functools
import json
import typing as t
from datetime import datetime

import pydantic

from ..core.base.base_json import BaseJSONDecoder

DeviceInputs = t.NewType(
    "DeviceInputs", dict[t.Literal["country", "code", "locale", "tz"], t.Any]
)
UsertagInputs = t.NewType("UsertagInputs", list[int])
Caption = t.NewType("Caption", dict[str, list[str]])
Hashtags = t.NewType("Hashtags", dict[str, list[str]])
Usertags = t.NewType("Usertags", dict[str, int])
Location = t.NewType("Location", dict[str, int])


class UserConfig(pydantic.BaseModel):
    niche: t.Optional[str] = None
    niche_subcat: t.Optional[str] = None
    farms: t.Optional[dict[str, int]] = None
    quality: bool = False

    class Config:
        extra = "ignore"
        json_encoders = {
            datetime: lambda obj: dict(_type=type(obj).__name__, value=obj.timestamp())
        }
        json_loads = functools.partial(json.loads, cls=BaseJSONDecoder)


class PostMedia(pydantic.BaseModel):
    media: bytes
    mime: str

    class Config:
        extra = "forbid"
        json_encoders = {
            bytes: lambda obj: dict(_type=type(obj).__name__, value=obj.decode("utf-8"))
        }
        json_loads = functools.partial(json.loads, cls=BaseJSONDecoder)


class PostData(pydantic.BaseModel):
    caption_text: str
    hashtags_opts: list[str]
    location_string: str
    usertags_amount: int
    extra: dict[str, t.Any]

    class Config:
        extra = "ignore"
        smart_union = True

    @pydantic.root_validator(pre=True)
    def build_extra(cls, values: dict[str, t.Any]) -> dict[str, t.Any]:
        all_required_field_names = {
            field.alias for field in cls.__fields__.values() if field.alias != "extra"
        }  # to support alias

        extra: dict[str, t.Any] = {}
        for field_name in list(values):
            if field_name not in all_required_field_names:
                extra[field_name] = values.pop(field_name)
        values["extra"] = extra
        return values
