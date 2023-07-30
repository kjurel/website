from app.api.common.routers.worker import workerRouter
from fastapi import APIRouter

router = APIRouter(prefix="/")
router.include_router(workerRouter)
