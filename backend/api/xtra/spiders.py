import scrapy
from playwright.sync_api._generated import Page
from scrapy.http import TextResponse
from scrapy.selector import SelectorList
from scrapy.spiders import Spider
from scrapy_playwright.page import PageMethod


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
                PageMethod("wait_for_selector",
                           "div.download-wrapper a")
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
