from __future__ import annotations

import io
import zipfile

from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.applications.downloader.utilities import downloader
from src.core.authentication import BasicAuth

downloadRouter = APIRouter(prefix="/", tags=["Download"])

import requests


@downloadRouter.get(
    "/",
    responses={
        200: {
            "content": {
                "image/jpeg": {},
                "video/mp4": {},
                "application/zip": {}
            }
        }
    },
    response_class=Response,
)
async def download(url: str, _=Depends(BasicAuth)):
  
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
