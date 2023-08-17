from datetime import datetime

import pydantic
import scrapy
from scrapy.http import TextResponse
from scrapy.selector import Selector, SelectorList


class Item(pydantic.BaseModel):
    url: str
    title: str
    scale: tuple[int, int]  # width x height
    size: str
    time: datetime
    user: str

    class Config:
        extra = "forbid"
        smart_union = True
        arbitrary_types_allowed = True


class Spider(scrapy.Spider):
    name = "WikiaSpider"
    allowed_domains = ["fandom.com"]

    def __init__(self, anime_tag="", **kwargs):
        # animeTag = jujutsu-kaisen
        self.start_urls = [
            f"https://{anime_tag}.fandom.com/wiki/Special:MIMESearch"
            "/image/png?limit=1000&offset=0&mime=image%2Fpng"
        ]
        super().__init__(name=None, **kwargs)
        self.return_value: list[Item] = list()
        self.output_callback = kwargs["args"].get("callback")

    def parse(self, response: TextResponse):
        # inspect_response(response, self)
        item: Selector
        items: SelectorList = response.css("ol.special li")

        for item in items:
            dimension_size: str
            rawtime: str
            _, _, _, _, dimension_size, _, rawtime = item.css("::text").getall()

            it = Item(
                url=item.css("a.internal::attr(href)").get(),
                title=item.css("a.internal::attr(title)").get(),
                scale=tuple(
                    (ss := dimension_size.strip(" . . ").split(" . . "))[0].split(" × ")
                ),
                size=ss[1],
                time=datetime.strptime(rawtime, " . . %H:%M, %d %B %Y"),
                user=item.css("a:last-child::attr(href)").get(),
            )

            self.return_value.append(it)

            yield it

        next_page = response.css("a.mw-nextlink::attr(href)").get()

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def close(self, spider, reason):
        self.output_callback(self.return_value)
