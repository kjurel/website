from importlib import import_module

from scrapy.crawler import CrawlerProcess, Spider


class CustomCrawler:
    def __init__(self) -> None:
        self.output: list | None = None
        module = import_module("app.settings.config_scrapy")
        self.process = CrawlerProcess(
            settings={
                k.upper(): getattr(module, k)
                for k in dir(module)
                if not k.startswith("_")
            }  # priority="project"
        )

    def yield_output(self, data: list[dict]):
        self.output = data

    def crawl(self, cls: Spider, kwargs):
        self.process.crawl(cls, args={"callback": self.yield_output}, **kwargs)
        self.process.start()


def crawl_static(spider: Spider, **kwargs):
    crawler = CustomCrawler()
    crawler.crawl(spider, kwargs)
    return crawler.output
