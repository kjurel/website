from fastapi import APIRouter
from fastapi_class import View


@View(recogRouter := APIRouter(prefix="/facerecog", tags=["Face Recognition"]))
class recogView:
    def get(self):
        return {"service": "not working"}


router = APIRouter()
router.include_router(recogRouter)
