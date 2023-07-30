__database__ = True
__not_implemented__ = False
__celery_backlinks__ = True
__scrapy_backlinks__ = False

from app.api.reddit.routers import router as r
from fastapi import APIRouter

router = APIRouter(prefix="/reddit")
router.include_router(r)
