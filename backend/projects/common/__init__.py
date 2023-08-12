__database__ = True
__not_implemented__ = False
__celery_backlinks__ = True
__scrapy_backlinks__ = True

from app.api.common.routers.worker import workerRouter
from fastapi import APIRouter

router = APIRouter(prefix="/")
router.include_router(workerRouter)


from app.api.common.routers import router as r
from fastapi import APIRouter

router = APIRouter(prefix="/cmn")
router.include_router(r)
