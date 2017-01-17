# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

from MyNews.items import MyNewsItem


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
        except:
            print "connect mysql error"
            raise

    def process_item(self, item, spider):
        if (MyNewsItem.TestItem(item) is False):
            raise DropItem("item is invaild.\n%s" % item)
        self.insert_into_mysql(item)
        return item

    def insert_into_mysql(self, item):
        sql = "INSERT INTO MyNews(url, title, tag, time, context, cover) \
            Values('%s', '%s', '%s', '%s', '%s', '%s')" % (
            item["url"], item["title"], item["tag"], item["time"],
            item["context"], item["cover"])

        print "sql is :\n%s" % sql
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            raise

    def close_spider(self, spider):
        try:
            self.db.close()
        except:
            pass
