import json
import typing as t
from datetime import datetime

from pydantic import BaseModel


class BaseJSONDecoder(json.JSONDecoder):
    """Base class for decoding json objects
    Supported objects: `datetime`, `bytes`
    """

    def __init__(
        self, pydantic_maps: t.Optional[list[t.Type[BaseModel]]] = None, *args, **kwargs
    ):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
        self.pydantic_mappings = pydantic_maps or list()

    def object_hook(self, obj):
        _type = obj.get("_type")
        if _type is None:
            return obj

        if _type == datetime.__name__:
            return datetime.fromtimestamp(obj["value"])
        if _type == bytes.__name__:
            return obj["value"].encode("utf-8")

        del obj["_type"]

        mapping = {
            f.__name__: f for f in tuple(self.pydantic_mappings)
        }  # Use for nested pydantic objs only

        return mapping[_type].parse_obj(obj)
