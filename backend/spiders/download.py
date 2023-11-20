import scrapy
from ..core.modules.artwork import image, video, typecheck
import pydantic
from playwright.sync_api._generated import Page
from scrapy.http import TextResponse
from scrapy.selector import SelectorList
from scrapy.spiders import Spider
from scrapy_playwright.page import PageMethod

from ..core.modules.scrapy_app import crawl_static


class Item(scrapy.Item):
    url = scrapy.Field()


class DownloadSpider(Spider):
    name = "download"
    custom_settings = dict(
        DOWNLOAD_HANDLERS={
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        TWISTED_REACTOR="twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    )

    def __init__(self, name=None, link=None, **kwargs):
        super().__init__(name, **kwargs)
        self.link: str = link
        if self.link is None:
            raise ValueError("Link must be specified")
        self.return_value: list[Item] = list()
        self.output_callback = kwargs["args"].get("callback")

    def start_requests(self):
        yield scrapy.Request(
            "sssinstagram.com/p/Cfiwuj-Kttj/",
            meta=dict(
                playwright=True,
                playwright_include_page=True,
                playwright_page_methods=[
                    # PageMethod(
                    # 'click', '"input[name=\"DownloaderForm\\[url\\]\"]"'),
                    #     PageMethod(
                    #         'fill', 'input[name=\"DownloaderForm\\[url\\]\"]"',
                    #         self.link),
                    #     PageMethod('click', 'button:has-text(\"Download photo\")'),
                    PageMethod("wait_for_selector", "div.download-wrapper a")
                ],
                errback=self.errback,
            ),
        )

    async def parse(self, response: TextResponse):
        page: Page = response.meta["playwright_page"]
        await page.screenshot(path="example.png", full_page=True)
        await page.close()

        url: SelectorList = response.css("div.download-wrapper a::attr(href)")
        it = Item(url=url.get())

        self.return_value.append(it)
        yield it

    def close(self, spider, reason):
        self.output_callback(self.return_value)

    async def errback(self, failure):
        page: Page = failure.request.meta["playwright_page"]
        await page.close()


# ------


def downloader(url: str) -> list[str] | str:
    raise ValueError()

    return crawl_static(DownloadSpider, link=url)

    @pydantic.validator("media", pre=True)
    def validate_media(cls, v):
        def get_media(m: str | image | video | bytes) -> image | video:
            if isinstance(m, image) or isinstance(m, video):
                return m
            elif isinstance(m, (str, bytes)):
                if isinstance(typecheck(m), image):
                    return image.Ex.Image.open(m)
                else:
                    return (
                        video.Load.frompath(m)
                        if isinstance(m, str)
                        else video.Load.frombytes(m)
                    )
            else:
                raise TypeError

        if not isinstance(v, (str, bytes, image, video)):
            raise TypeError
        return [get_media(i) for i in v]
