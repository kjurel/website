__database__ = False
__router__ = False
__celery_backlinks__ = True
__scrapy_backlinks__ = False

# from app.api.instagram.routers.auth import authRouter
# from app.api.instagram.routers.post import postRouter
# from app.api.instagram.routers.user import userRouter
from fastapi import APIRouter

router = APIRouter(prefix="/instagram")
# router.include_router(authRouter)
# router.include_router(postRouter)
# router.include_router(userRouter)


# from app.api.instagram.routers import router as r
# from fastapi import APIRouter
#
# router = APIRouter(prefix="/instagram")
# router.include_router(r)
