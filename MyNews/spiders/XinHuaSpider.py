# coding: UTF-8
import scrapy

import sys
sys.path.append('..')
sys.path.append('../..')

from MyNews.items import MyNewsItem
from BaseSpider import BaseSpider


class XinHuaSpider(BaseSpider):
    name = 'XinHuaSpider'
    # allowed_domains = ['163.com']
    # start_urls = [
    #     'http://news.163.com/',
    # ]
    allowed_domains = ['xinhuanet.com', 'news.cn']
    start_urls = [
        # 'http://war.163.com/16/1203/09/C7BNRS0E000181KT.html',
        'http://www.xinhuanet.com/'
    ]

    def parse(self, response):
        urls = response.xpath("//*/@href").extract()
        for url in urls:
            url = response.urljoin(url)
            url = self.get_uniq_url(url)
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        item = MyNewsItem()
        item["url"] = response.url
        self.parse_title(response, item)
        self.parse_tag(response, item)
        self.parse_time(response, item)
        self.parse_context(response, item)
        self.parse_cover(response, item)
        self.parse_image_md5(response, item)

        yield item

    def parse_title(self, response, item):
        tmp = response.xpath('//*[@id="title"]/text()').extract()
        if tmp is None or len(tmp) == 0:
            item["title"] = u""
        else:
            self.log("tmp is :\n%s" % tmp)
            item["title"] = tmp[0]

    def parse_tag(self, response, item):
        tmp = response.xpath('//*[@class="curDiv clearfix"]/span/text()').extract_first()

        if tmp is None or len(tmp) == 0:
            item["tag"] = u""
        else:
            item["tag"] = tmp

        if u"" == item["tag"]:
            tmp = response.xpath('//*[@class="s_pd"]/text()').extract()
        if tmp is None or len(tmp) == 0:
            item["tag"] = u""
        else:
            item["tag"] = tmp[1:]

        if u"" == item["tag"]:
            tmp = response.xpath('//*[@class="curDiv clearfix"]/span/text()').extract()
        if tmp is None or len(tmp) == 0:
            item["tag"] = u""
        else:
            item["tag"] = tmp

        if u"" == item["tag"]:
            item["tag"] = u"其他"
        # temporary
        item["tag"] = u"其他"

    def parse_time(self, response, item):
        tmp = \
            response.xpath('//*[@class="time"]/text()').extract()

        if tmp is None or len(tmp) == 0:
            item["time"] = u""
        else:
            item["time"] = tmp[0].lstrip()
            self.log('time is:\n%s' % item['time'])
            if len(item["time"]) >= 10:
                item["time"] = item["time"][:10]
                item["time"] = item["time"][:4] + u"-" +\
                    item["time"][5:7] + u"-" + \
                    item["time"][8:10]
            else:
                item["time"] = u""
            self.log('time is:\n%s' % item['time'])

        if "" == item["time"]:
            tmp = \
                response.xpath('//*[@id="pubtime"]/text()').extract()
        if tmp is None or len(tmp) == 0:
            item["time"] = u""
        else:
            item["time"] = tmp[0].lstrip()
            self.log('time is:\n%s' % item['time'])
            if len(item["time"]) >= 10:
                item["time"] = item["time"][:10]
                item["time"] = item["time"][:4] + u"-" +\
                    item["time"][5:7] + u"-" + \
                    item["time"][8:10]
            else:
                item["time"] = u""
            self.log('time is:\n%s' % item['time'])

    def parse_context(self, response, item):
        tmp = response.xpath('//*[@id="article"]/p/text()').extract()

        if tmp is None or len(tmp) == 0:
            item["context"] = u""
        else:
            for p in tmp:
                item["context"] = p + u"\r\n"

        if "" == item["context"]:
            tmp = response.xpath('//*[@id="content"]/p/text()').extract()

        if tmp is None or len(tmp) == 0:
            item["context"] = u""
        else:
            for p in tmp:
                item["context"] = p + u"\r\n"

    def parse_cover(self, response, item):
        tmp = response.xpath('//*[@id="article"]/p/img/@src').extract_first()

        if tmp is None or len(tmp) == 0:
            item["cover"] = u""
        else:
            item["cover"] = tmp

        if "" == item["cover"]:
            tmp = response.xpath('//*[@id="content"]/p/img/@src').extract_first()
        if tmp is None or len(tmp) == 0:
            item["cover"] = u""
        else:
            item["cover"] = tmp

        if "" != item["cover"]:
            item["cover"] = response.urljoin(item["cover"])

    def parse_image_md5(self, response, item):
        item['image_md5'] = u''
