from scrapy.dupefilter import RFPDupeFilter

from pybloomfilter import BloomFilter


class SeenURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""
    def __init__(self, path=None):
        self.urls_seen = BloomFilter(10000000, 0.001)

    def request_seen(self, request):
        return self.urls_seen.add(request.url)
