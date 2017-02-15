# from scrapy_redis.spiders import RedisSpider
import logging
import scrapy
import redis

logger = logging.getLogger(__name__)


class BaseSpider(scrapy.Spider):
    name = 'BaseSpider'
    redis_ip = "localhost"
    redis_port = 6379
    redis_db = 0
    timeout = 1
    unique_urls = "unique_urls"

    def __init__(self):
        try:
            self.redis_client = redis.StrictRedis(host=self.redis_ip,
                                                  port=self.redis_port,
                                                  db=self.redis_db)
            logger.debug("filter connect redis client success.")
        except:
            logger.debug("filter redis connect error")
            raise

    def parse(self, response):
        pass

    def parse_item(self, response):
        pass

    def parse_title(self, response, item):
        pass

    def parse_tag(self, response, item):
        pass

    def parse_time(self, response, item):
        pass

    def parse_context(self, response, item):
        pass

    def parse_cover(self, response, item):
        pass

    def parse_image_md5(self, response, item):
        pass

    def get_uniq_url(self, url):
        try:
            uniq_url = self.redis_client.brpop(self.unique_urls, self.timeout)
            logger.debug("get url success")
            if uniq_url is not None:
                url = uniq_url
                logger.debug("url instance: %s" % url)
        except:
            pass

        return url
