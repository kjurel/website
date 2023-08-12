from fastapi import APIRouter

from .routers import downloadRouter

router = APIRouter(prefix="/download")
router.include_router(downloadRouter)
