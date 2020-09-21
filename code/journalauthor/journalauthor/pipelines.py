# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo
from journalauthor.settings import collection

class JournalauthorPipeline(object):
    def __init__(self):
        self.post = collection

    def process_item(self, item, spider):
        data = dict(item)
        self.post.insert(data)
        return item