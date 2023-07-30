from app.api.common.models.database import RemoteCache
from tortoise.contrib.pydantic import pydantic_model_creator

CACHE_PYDANTIC = pydantic_model_creator(
    RemoteCache,
    name="RemoteCache",
    exclude_readonly=True
)
