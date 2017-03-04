# -*- coding: utf-8 -*-

from pipelines import RMMPipeline
from pipelines import SimhashPipeline
from pipelines import MyNewsPipeline
# import math
# words_with_freq_file = "/home/ubuntu/Downloads/MyNews/webdict_with_freq.txt"
# f = open(words_with_freq_file)
# line = f.readline()
# w = {}
# c = 0
# while line:
# # self.stop_words_set.add(line)
#     fields = line.split(' ')
#     if len(fields) == 2:
#         w[fields[0]] = long(fields[1])
#         c = c + long(fields[1])
#     line = f.readline()
# print c
# f.close()
# for (k, v) in w.items():
#     w[k] = math.log(c / (v + 1))

item = {
    'tag': u'test',
    'title': u"研背后有盘棋",
    'time': u'2017-02-27',
    'url': u'http://news.xinhuanet.com/politics/2017-02/27/c_1120533145.htm',

    'context': u'\
        传统的hash算法只负责将原始内容尽量均匀随机地映射为一个签名值，\
        原理上相当于伪随机数产生算法。传统hash算法产生的两个签名，\
        如果相等，说明原始内容在一定概率下是相等的;如果不相等，\
        除了说明原始内容不相等外，不再提供任何信息，\
        因为即使原始内容只相差一个字节，所产生的签名也很可能差别极大。'}
rmm = RMMPipeline()
rmm.open_spider(None)
rmm.process_item(item, None)

sm = SimhashPipeline()
sm.process_item(item, None)

# m = MyNewsPipeline()
#
# item = {}
# item["url"] = u"test"
# item["title"] = u"中国"
# item["tag"] = u"test"
# item["time"] = u"2017-02-24"
# item["context"] = u"test"
# item["summary"] = u"test"
# item["keywords"] = [u"test1", u"test2"]
# item["cover"] = u"test"
# item["image_md5"] = u"md5"
#
# m.open_spider(None)
# m.process_item(item, None)
