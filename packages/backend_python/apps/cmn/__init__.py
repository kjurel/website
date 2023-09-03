__database__ = False
__router__ = True
__celery_backlinks__ = False
__scrapy_backlinks__ = True

from fastapi import APIRouter

from .router import testRouter

router = APIRouter(prefix="")
router.include_router(testRouter)
