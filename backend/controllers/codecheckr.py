import io
import itertools
import zipfile

import copydetect
from fastapi import APIRouter, File, UploadFile
from fastapi_class import View


@View(checkRouter := APIRouter(prefix="/codecheckr", tags=["Code Checkr"]))
class checkrView:
    def get(self):
        return {"service": "working"}

    async def post(self, f: UploadFile = File(...)):
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
            token_overlap, similarities, slices = copydetect.compare_files(
                pair[0], pair[1]
            )
            retval.append(
                {
                    "pairs": [p.filename for p in pair],
                    "token_overlap": int(token_overlap),
                    "similarities": [float(s) for s in similarities],
                    # "slices": slices,
                }
            )
        return retval


router = APIRouter()
router.include_router(checkRouter)
