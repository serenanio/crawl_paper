# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ConfauthorItem(scrapy.Item):
    paper_name = scrapy.Field()
    cite_num = scrapy.Field()
    author = scrapy.Field()
    rank = scrapy.Field()

    author_page = scrapy.Field()
    ACM_author_profile = scrapy.Field()
    Mathematics_Genealogy_profile = scrapy.Field()
    Wikipedia_article = scrapy.Field()
    Google_Scholar_profile = scrapy.Field()
    Scopus_profile = scrapy.Field()
    affiliation = scrapy.Field()
    award = scrapy.Field()
    pass
