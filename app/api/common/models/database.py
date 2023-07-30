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
