import io
import itertools
import typing as t
import zipfile

import copydetect
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/api/py/codecheckr")
async def req(f: t.Optional[UploadFile] = File(None)):
    if (f is None) or (f.content_type != "application/zip"):
        raise ValueError
    v = await f.read()
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
        print(token_overlap, similarities, slices)

    return {"name": "success"}
