from app.api.instagram.routers.auth import authRouter
from app.api.instagram.routers.post import postRouter
from app.api.instagram.routers.user import userRouter
from fastapi import APIRouter

router = APIRouter(prefix="/instagram")
router.include_router(authRouter)
router.include_router(postRouter)
router.include_router(userRouter)
