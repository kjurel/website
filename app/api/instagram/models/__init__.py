from app.api.instagram.models.database import User, Post
from tortoise.contrib.pydantic import pydantic_model_creator

USER_PYDANTIC = pydantic_model_creator(
    User,
    name="User",
    exclude_readonly=True
)
POST_PYDANTIC = pydantic_model_creator(
    Post,
    name="Post",
    exclude_readonly=True
)
