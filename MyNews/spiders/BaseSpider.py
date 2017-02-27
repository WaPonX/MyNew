# from scrapy_redis.spiders import RedisSpider
import logging
from scrapy.spiders import Spider
import redis

logger = logging.getLogger(__name__)


class BaseSpider(Spider):
    name = 'BaseSpider'
    redis_ip = "localhost"
    redis_port = 6379
    redis_db = 0
    redis_client = None
    timeout = 1
    unique_urls = "unique_urls"

    def __connect(self):
        if self.redis_client is None:
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

    def parse_keywords(self, response, item):
        pass

    def get_uniq_url(self, url):
        try:
            self.__connect()
            uniq_url = self.redis_client.brpop(self.unique_urls, self.timeout)
            logger.debug("get url success")
            if uniq_url is not None:
                if isinstance(uniq_url, tuple) and len(uniq_url) >= 2:
                    url = uniq_url[2]
                    logger.debug("url instance: %s" % url)

        except:
            logger.debug("get url timeout")

        return url
