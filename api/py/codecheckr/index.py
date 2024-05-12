import io
import itertools
import typing as t
import zipfile

import copydetect
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRouter

CORS_ORIGINS = [
    "http://localhost:4321",
    "https://kanishkk.vercel.app",
    "https://website-git-main-tokcide.vercel.app",
]
# CORS_REGEX_ORIGINS = ["https:\/\/website-(?:[a-zA-Z0-9_-]+)-tokcide\.vercel\.app"]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*", "X-Request-With", "X-Request-Id"]
app = FastAPI(
    docs_url="/api/py/codecheckr/docs", openapi_url="/api/py/codecheckr/openapi.json"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    # allow_origin_regex=CORS_REGEX_ORIGINS,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=CORS_ALLOW_METHODS,
    allow_headers=CORS_ALLOW_HEADERS,
    expose_headers=["X-Request-ID"],
)
router = APIRouter()


@router.get("/api/py/codecheckr")
async def reqG():
    return {"command": "success"}


@router.post("/api/py/codecheckr")
async def reqP(f: t.Optional[UploadFile] = File(None)):
    # if (f is None) or (f.content_type != "application/zip"):
    #    raise ValueError
    v = await f.read()
    retval = []
    codes_fings: list[copydetect.CodeFingerprint] = []
    with io.BytesIO(v) as zip_buffer:
        with zipfile.ZipFile(zip_buffer, "r") as zip_ref:
            for z in zip_ref.infolist():
                if z.is_dir():
                    continue
                codes_fings.append(
                    copydetect.CodeFingerprint(
                        z.filename, 25, 1, fp=zip_ref.open(z.filename)
                    )
                )
    codes_pairs = list(itertools.combinations(codes_fings, 2))
    for pair in codes_pairs:
        token_overlap, similarities, slices = copydetect.compare_files(pair[0], pair[1])
        retval.append(
            {
                "pairs": [p.filename for p in pair],
                "token_overlap": int(token_overlap),
                "similarities": [float(s) for s in similarities],
                # "slices": slices,
            }
        )
    print(retval)
    return retval


app.include_router(router)
