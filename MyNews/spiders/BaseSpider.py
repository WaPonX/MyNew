from scrapy_redis.spiders import RedisSpider

class BaseSpider(RedisSpider):
    name = 'BaseSpider'

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
