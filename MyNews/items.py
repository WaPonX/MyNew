# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import logging
import scrapy

logger = logging.getLogger(__name__)


class MyNewsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    time = scrapy.Field()
    tag = scrapy.Field()
    context = scrapy.Field()
    summary = scrapy.Field()
    cover = scrapy.Field()
    image_md5 = scrapy.Field()
    keywords = scrapy.Field()
    tf_idf = scrapy.Field()
    strsimhash = scrapy.Field()

    # @staticmethod
    # def TestItem(item):
    #     logger.debug("testitem %s " % item)
    #     if item is None:
    #         logger.debug("testitem %s " % item)
    #         return False

    #     return True
