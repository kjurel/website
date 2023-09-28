from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi_utils.timing import add_timing_middleware

from backend.apps import cmn, instagram, reddit

app = FastAPI()

add_timing_middleware(app)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:5000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

if __name__ == "__main__":
    app.add_middleware(HTTPSRedirectMiddleware)

mainRouter = APIRouter()

mainRouter.include_router(cmn.router)
mainRouter.include_router(instagram.router)
mainRouter.include_router(reddit.router)

app.include_router(mainRouter, prefix="/api/py")
