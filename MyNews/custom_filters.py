from scrapy.dupefilters import RFPDupeFilter
import logging

from pybloomfilter import BloomFilter


logger = logging.getLogger(__name__)


class RedisURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""
    bf = BloomFilter(10000000, 0.001)
    # def __init__(self, path=None, debug=False):
    #     self.debug = debug
    #     # pass


    def request_seen(self, request):
        # return self.urls_seen.add(request.url)
        # fp = self.request_fingerprint(request)
        # request.url = fp
        # logger.debug("after request url : %s" % request.url)
        # return fp != ""
        return self.bf.add(self.request_fingerprint(request))

    def request_fingerprint(self, request):
        return request.url
