from app.core.base.base_models import BaseDB
from tortoise import fields


class RemoteCache(BaseDB):
  name: str = fields.CharField(max_length=255, null=False, unique=True)
  data: bytes = fields.BinaryField()
  
  class Meta:
    abstract = False
    table = "RemoteCache"
    table_description = "data about non-slug files"
  
  class PydanticMeta:
    pass

from app.api.common.models.database import RemoteCache
from tortoise.contrib.pydantic import pydantic_model_creator

CACHE_PYDANTIC = pydantic_model_creator(
    RemoteCache,
    name="RemoteCache",
    exclude_readonly=True
)
