# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CitationItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    paper_name = scrapy.Field()
    conf_type = scrapy.Field()
    conf = scrapy.Field()
    author_link = scrapy.Field()
    num = scrapy.Field()
    year = scrapy.Field()
    author_list = scrapy.Field()
    topic = scrapy.Field()
    cite_num = scrapy.Field()
    creat_time = scrapy.Field()
    cite_from = scrapy.Field()
    pass
