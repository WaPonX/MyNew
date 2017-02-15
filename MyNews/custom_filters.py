from scrapy.dupefilters import RFPDupeFilter

import logging


logger = logging.getLogger(__name__)


class RedisURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""

    def __init__(self, path=None, debug=False):
        self.debug = debug
        # pass

    def request_seen(self, request):
        # return self.urls_seen.add(request.url)
        fp = self.request_fingerprint(request)
        request.url = fp
        logger.debug("after request url : %s" % request.url)
        return fp != ""

    def request_fingerprint(self, request):
        return request.url
