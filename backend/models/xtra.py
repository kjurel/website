from tortoise import fields
from tortoise.contrib.pydantic.creator import pydantic_model_creator

from ..core.base.base_models import BaseDB


class RemoteCache(BaseDB):
    name = fields.CharField(max_length=255, null=False, unique=True)
    data = fields.BinaryField()

    class Meta:
        abstract = False
        table = "RemoteCache"
        table_description = "data about non-slug files"

    class PydanticMeta:
        pass


CACHE_PYDANTIC = pydantic_model_creator(
    RemoteCache, name="RemoteCache", exclude_readonly=True
)
