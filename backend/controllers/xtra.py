# from app.core.models.database import RemoteCache
# from app.web.spiders import wikia
# from fastapi import APIRouter

# contentRouter = APIRouter(prefix="/content", tags=["Content"])

# @contentRouter.get("/verticalPolls")
# def verticalPolls(source: str, source_query: str):
#     match source:
#         case "fandom":
#             wikia.Spider()
#             RemoteCache
from __future__ import annotations

import io
import zipfile

import requests
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi_class import View

from ..core.authentication import BasicAuth
from ..spiders.download import downloader


@View(testRouter := APIRouter(prefix="/test", tags=["Testing"]))
class TestView:
    def get(self, name: str):
        return {"answer": f"Hello {name}"}


@View(downloadRouter := APIRouter(prefix="/", tags=["Download"]))
class DownloadView:
    RESPONSE_CLASS = {
        "get": {
            200: {"content": {"image/jpeg": {}, "video/mp4": {}, "application/zip": {}}}
        },
    }

    def get(self, url: str, _=Depends(BasicAuth)):
        try:
            cdn_url = downloader(url)
        except:
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        if isinstance(cdn_url, list):
            contents: list[bytes] = []
            media_types: list[str] = []
            for url in cdn_url:
                r = requests.get(url)
                r.raise_for_status()
                contents.append(r.content)
                media_types.append(r.headers["Content-Type"])
            f = io.BytesIO()
            with zipfile.ZipFile(f, "w") as archive:
                for content, media_type in zip(contents, media_types):
                    with archive.open(media_type, "w") as file:
                        file.write(content)
            content = f.getvalue()
            media_type = "application/zip"

        else:
            r = requests.get(url)
            r.raise_for_status()

            content = r.content
            media_type = r.headers["Content-Type"]

        return Response(content=r.content, media_type=r.headers["Content-Type"])
