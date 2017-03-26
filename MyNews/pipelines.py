# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from ctypes import c_ubyte
from datetime import datetime
import math
import re
import redis
import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
import logging

import MySQLdb

logger = logging.getLogger(__name__)


class ImagesPipeline(ImagesPipeline):
    '''
    MyNews project's download image pipeline
    '''
    def get_media_requests(self, item, info):
        if item['cover'] is not None and item['cover'] != "":
            yield scrapy.Request(item['cover'])

    def item_completed(self, results, item, info):
        logger.debug("results is %s" % results)
        image_paths = [x["path"] for ok, x in results if ok]
        if len(image_paths) > 0:
            item["cover"] = u'/home/ubuntu/Image/MyNews/img/' + image_paths[0]
        return item
        # for ok, x in result:
        #    if ok:
        #        item["cover"] = x['path']
        #        item['image_md5'] = x['checksum']
        #    logger.debug("x is %s " % x)


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
        # logger.debug("urls_buf length is %d" % len(self.urls_buf))
        self.urls_buf.append(url)
        if len(self.urls_buf) > self.max_urls_count:
            # logger.debug("urls_buf is %s" % self.urls_buf)
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
        # append url to redis ignore the item used or not
        self.append_url(item["url"])
        return item

    def close_spider(self, spider):
        logger.debug("close redis client success.")
        self.send_urls()


class RMMPipeline(object):
    """
    use RMM algorithm cut the title.
    """
    words_file = "/home/ubuntu/Downloads/MyNews/words.txt"
    stop_words_file = "/home/ubuntu/Downloads/MyNews/stop_words.txt"
    words_with_freq_file = "/home/ubuntu/Downloads/MyNews/webdict_with_freq.txt"
    words_set = set()
    stop_words_set = set()
    words_freq_dict = {}
    count_freq = 0
    max_keywords_count = 10

    def __load_data(self):
        # load sign in words
        # logger.debug("start loading data")
        f = open(self.words_file)
        line = f.readline()
        while line:
            self.words_set.add(line[:-1].decode('utf8'))
            line = f.readline()
        f.close()

        # logger.debug("start loading stop words")
        # load stop words
        f = open(self.stop_words_file)
        line = f.readline()
        while line:
            self.stop_words_set.add(line[:-1].decode('utf8'))
            line = f.readline()
        f.close()

        # logger.debug("start loading words frequence")
        # load words with frequence
        f = open(self.words_with_freq_file)
        # f = open(self.stop_words_file)
        line = f.readline()
        while line:
            fields = line.split(' ')
            if len(fields) == 2:
                self.words_freq_dict[fields[0].decode('utf8')] = long(fields[1])
                self.count_freq = self.count_freq + long(fields[1])
            line = f.readline()
        f.close()
        # logger.debug("start count IDF")
        # IDF
        for (k, v) in self.words_freq_dict.items():
            self.words_freq_dict[k] = math.log(self.count_freq / (v + 1))
        # logger.debug("end count IDF")

    def open_spider(self, spider):
        self.__load_data()
        # logger.debug('words_set len is %d' % len(self.words_set))

    def check_item(self, item):
        logger.debug("checkitem %s" % item)
        if "" == item["title"] or "" == item["tag"] or "" == item["context"]:
            logger.debug("invailitem %s " % item)
            return False

        # if len(item['cover']) == 0 or len(item['image_md5']) == 0:
        #    return False

        try:
            d = datetime.strptime(item["time"], "%Y-%m-%d")
        except:
            logger.debug("time's format is error.")
            return False

        return True

    def process_item(self, item, spider):
        # judge the item is vaild or not
        if self.check_item(item) == False:
            # logger.debug("item is %s" % item)
            raise DropItem("item is invaild.\n%s" % item)
        logger.debug("waponxie items is vaild")

        title_keywords = self.__cut_sentence(item['title'])

        # split context
        # split_re = u'[。，？！、；：“”（）【】—……《》*~,\.\?/:;""\'\'\r\n\[\]\{\}\s]'
        split_re = u'[。，？！、；：“”（）【】———……《》*~,\.\?/:;""\'\'\[\]\{\}\s]'
        sentences = re.split(split_re, item['context'].replace(u"\r\n", " "))

        logger.debug(sentences)
        context_keywords = {}
        for sentence in sentences:
            logger.debug(sentence)
            if len(sentence) == 0:
                continue
            for (k, v) in self.__cut_sentence(sentence).items():
                if k in context_keywords.keys():
                    context_keywords[k] = context_keywords[k] + v
                else:
                    context_keywords[k] = v

        # TF-IDF algorithm
        keywords = context_keywords
        for (k, v) in title_keywords.items():
            if k in keywords:
                keywords[k] = keywords[k] + v
            else:
                keywords[k] = v
        words_tf_idf = {}

        # count TF-IDF
        for (k, v) in keywords.items():
            if k in self.words_freq_dict:
                words_tf_idf[k] = v * self.words_freq_dict[k]
            else:
                words_tf_idf[k] = v * 1

        item['keywords'] = self.__get_keywords(words_tf_idf)
        item['tf_idf'] = {}
        for key in item['keywords']:
            item['tf_idf'][key] = words_tf_idf[key]
        # logger.debug("keywords is %s" % item['keywords'])
        self.__check_keywords(keywords)

        return item

    def __get_keywords(self, words_tf_idf):
        desc_tf_idf = sorted(words_tf_idf.items(),
                              lambda x, y: cmp(x[1], y[1]),
                              reverse = True)
        result = []
        count = 0
        for item in desc_tf_idf:
            if count >= self.max_keywords_count:
                break
            else:
                result.append(item[0])
                count = count + 1
        return result

    def __check_keywords(self, keywords):
        pass

    # clear stop words from words
    def __clear_stop_words(self, words):
        for k in words.keys():
            if k in self.stop_words_set:
                del words[k]

    def __cut_sentence(self, sentence, max_len=6):
        if not isinstance(sentence, basestring):
            logger.debug("sentence is not a string")
            return []
        # sentence = sentence.decode("utf-8")
        # logger.debug("sentence is %s " % sentence)
        sentence = sentence.replace(r'\r', '')
        sentence = sentence.strip()
        sen_len = len(sentence)
        cur = sen_len
        word_with_freq = {}
        while cur > 0:
            end = cur
            index = None
            for index in range(max_len, 0, -1):
                word = sentence[(cur - index): cur]
                logger.debug("word is %s " % word)
                # if word in words_set
                # then push the word in word_with_freq
                if word in self.words_set:
                    if word not in word_with_freq:
                        word_with_freq[word] = 0
                    word_with_freq[word] = word_with_freq[word] + 1
                    end = cur - index
                    break

            # new words
            # if not match in words_set
            # choose the last one word as keyword
            # and push then word in the words_set
            if end == cur:
                end = cur - 1
                word = sentence[end: cur]
                if word not in word_with_freq:
                    word_with_freq[word] = 0
                word_with_freq[word] = word_with_freq[word] + 1
                self.words_set.add(word)
            cur = end

        # clear stop words from word_with_freq
        self.__clear_stop_words(word_with_freq)
        logger.debug("word_with_freq is %s " % word_with_freq)

        return word_with_freq

    def close_spider(self, spider):
        self.words_set.clear()

class SimhashPipeline(object):
    seed = 131
    feature_len = 64

    def process_item(self, item, spider):
        item['strsimhash'] = self.simhash(item['tf_idf'])

        return item

    def simhash(self, feature_weight):
        hash_value = self.string_hash(feature_weight)

        simhash_string = ""
        for index in range(self.feature_len):
            if ((1 << index) & hash_value) > 0:
                simhash_string = '1' + simhash_string
            else:
                simhash_string = '0' + simhash_string
        return simhash_string

    def __cal_weigth(self, hash_value, weight=1):
        # bm = BitMap(self.feature_len)

        result = []
        for index in range(self.feature_len):
            if ((1 << index) & hash_value) > 0:
                result.append(weight)
            else:
                result.append(-weight)

        return result

    def hex_string_hash(self, feature_weight):
        return hex(self.string_hash(feature_weight))

    def string_hash(self, feature_weight):
        hash_weights = []

        for (string, weight) in feature_weight.items():
            hash_value = self.BKDRHash(string)
            hash_weights.append(self.__cal_weigth(hash_value, weight))

        total_weight = [0 for x in range(self.feature_len)]
        for i in range(len(hash_weights)):
            for j in range(len(hash_weights[i])):
                total_weight[j] += hash_weights[i][j]

        result = 0
        for index in range(len(total_weight)):
            if total_weight[index] > 0:
                result = result | (1 << index)

        return result

    def BKDRHash(self, string):
        hash_value = 0
        for c in string:
            hash_value = hash_value * self.seed + ord(c)

        return hash_value


class MyNewsPipeline(object):
    db_ip = "localhost"
    db_username = "root"
    db_password = "tencent.com"
    db_name = "mynews"

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
        if len(item["context"]) > 50:
            item["summary"] = item["context"][:50]
        else:
            item["summary"] = item["context"]

        self.insert_into_mysql(item)
        return item

    def insert_into_mysql(self, item):
        sql = "INSERT INTO mynews_raw(url, title, tag, time, context,\
            summary, keywords, cover, img_md5, strsimhash) \
            Values('%s', '%s', '%s', '%s', '%s',\
            '%s', '%s', '%s', '%s', '%s')" % (item["url"], item["title"], \
            item["tag"], item["time"],item["context"], item["summary"], \
            self.list2str(item["keywords"]), item["cover"], item["image_md5"], \
            item['strsimhash'])

        logger.debug("waponxie sql is :\n%s" % sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
            raise

    def list2str(self, l, sep=u';'):
        if not isinstance(l, list):
            raise DropItem("please input a list.")

        result = u''
        for item in l:
            if len(result) == 0:
                result = item
            else:
                result = result + sep + item
        return result

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
