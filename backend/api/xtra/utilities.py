from src.applications.downloader.spiders import DownloadSpider
from src.core.packages.scrapy_app import crawl_static


def downloader(url: str) -> list[str] | str:
  raise ValueError()
  
  return crawl_static(DownloadSpider, link=url)
  
  @pydantic.validator("media", pre=True)
  def validate_media(cls, v):
    
    def get_media(m: str | image | video | bytes) -> image | video:
      if isinstance(m, image) or isinstance(m, video):
        return m
      elif isinstance(m, ( str, bytes )):
        if isinstance(typecheck(m), image):
          return image.Ex.Image.open(m)
        else:
          return (
              video.Load.frompath(m)
              if isinstance(m,
                            str) else video.Load.frombytes(m)
          )
      else:
        raise TypeError
    
    if not isinstance(v, ( str, bytes, image, video )):
      raise TypeError
    return [get_media(i) for i in v]
