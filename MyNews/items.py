# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from datetime import datetime

import scrapy


class MyNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    time = scrapy.Field()
    tag = scrapy.Field()
    context = scrapy.Field()
    cover = scrapy.Field()

    @staticmethod
    def TestItem(item):
        if ( "" == item["title"] or "" == item["tag"] or "" == item["context"]):
            return False
        try :
            d = datetime.strptime(item["time"], "%Y-%m-%d");
        except:
            return False

        return True
