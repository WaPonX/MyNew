from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from WangYiSpider import WangYiSpider


process = CrawlerProcess(get_project_settings())

process.crawl(WangYiSpider)
process.start()
