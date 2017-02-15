# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import redis
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import logging

from MyNews.items import MyNewsItem

logger = logging.getLogger(__name__)


class ImagesPipeline(ImagesPipeline):
    '''
    MyNews project's download image pipeline
    '''
    def get_media_requests(self, item, info):
        if item['cover'] is not None and item['cover'] != "":
            yield scrapy.Request(item['cover'])

    def item_completed(self, result, item, info):
        imagePath = None
        imageMD5 = None
        for ok, x in result:
            if ok:
                imagePath = x['path']
                imageMD5 = x['checksum']
        if imagePath is not None and len(imagePath) != 0:
            item["cover"] = imagePath
        if imageMD5 is not None and len(imageMD5) != 0:
            item['image_md5'] = imageMD5


class RedisPipeline(object):
    redis_ip = "localhost"
    redis_port = 6379
    redis_db = 0
    urls_buf = []
    max_urls_count = 10
    url_cache_pool = "url_cache_pool"

    def __init__(self):
        pass

    def open_spider(self, spider):
        try:
            self.redis_client = redis.StrictRedis(host=self.redis_ip,
                                                  port=self.redis_port,
                                                  db=self.redis_db)
            logger.debug("connect redis client success.")
        except:
            logger.debug("redis connect error")
            raise

    def append_url(self, url):
        logger.debug("urls_buf length is %d" % len(self.urls_buf))
        self.urls_buf.append(url)
        if len(self.urls_buf) > self.max_urls_count:
            logger.debug("urls_buf is %s" % self.urls_buf)
            self.send_urls()
            return

    def send_urls(self):
        if (len(self.urls_buf) != 0):
            p = self.redis_client.pipeline()
            for url in self.urls_buf:
                p.lpush(self.url_cache_pool, url)
            p.execute()
            self.urls_buf = []

    def process_item(self, item, spider):
        if (MyNewsItem.TestItem(item) is False):
            logger.debug("item is %s" % item)
            if item is not None and item["url"] is not None:
                self.append_url(item["url"])
            raise DropItem("item is invaild.\n%s" % item)

        return item

    def close_spider(self, spider):
        logger.debug("close redis client success.")
        self.send_urls()


class MyNewsPipeline(object):
    db_ip = "localhost"
    db_username = "root"
    db_password = "tencent.com"
    db_name = "MyNewsDB"

    def __init__(self):
        pass

    def open_spider(self, spider):
        try:
            self.db = MySQLdb.connect(host=self.db_ip,
                                      user=self.db_username,
                                      passwd=self.db_password,
                                      db=self.db_name)
            self.cursor = self.db.cursor()
            self.db.set_character_set('utf8')
            self.cursor.execute('SET NAMES utf8;')
            self.cursor.execute('SET CHARACTER SET utf8;')
            self.cursor.execute('SET character_set_connection=utf8;')
            self.db.commit()
            logger.debug("connect mysql client success.")
        except:
            logger.debug("connect mysql error")
            raise

    def process_item(self, item, spider):
        self.insert_into_mysql(item)
        return item

    def insert_into_mysql(self, item):
        sql = "INSERT INTO MyNews(url, title, tag, time, context, cover) \
            Values('%s', '%s', '%s', '%s', '%s', '%s')" % (
            item["url"], item["title"], item["tag"], item["time"],
            item["context"], item["cover"])

        logger.debug("sql is :\n%s" % sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            raise

    def close_spider(self, spider):
        try:
            self.db.close()
            logger.debug("close mysql client success.")
        except:
            logger.debug("close mysql client error.")
            pass


class FilterPipeline(object):
    redis_ip = "localhost"
    redis_port = 6379
    redis_db = 0
    timeout = 0.1
    unique_urls = "unique_urls"

    def __init__(self):
        pass

    def open_spider(self, spider):
        try:
            self.redis_client = redis.StrictRedis(host=self.redis_ip,
                                                  port=self.redis_port,
                                                  db=self.redis_db)
            logger.debug("filter connect redis client success.")
        except:
            logger.debug("filter redis connect error")
            raise

    def get_uniq_url(self, item):
        try:
            url = self.redis_client.brpop(self.unique_urls, self.timeout)
            logger.debug("url instance: %s" % url)
        except:
            logger.debug("timeout")
            return item["url"]
        return url

    def process_item(self, item, spider):
        item["url"] = self.get_uniq_url(item)
        return item

    def close_spider(self, spider):
        logger.debug("close redis client success.")
