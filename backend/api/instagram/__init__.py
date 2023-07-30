__database__ = True
__not_implemented__ = False
__celery_backlinks__ = True
__scrapy_backlinks__ = False

from app.api.instagram.routers import router as r
from fastapi import APIRouter

router = APIRouter(prefix="/instagram")
router.include_router(r)
