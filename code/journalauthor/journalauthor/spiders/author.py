# -*- coding: utf-8 -*-
import pymongo
import pandas as pd
from random import choice
import requests
from lxml import etree
import time
from journalauthor.items import JournalauthorItem
import random
client = pymongo.MongoClient(host='localhost',port=27017)
db=client.paper
collection=db.author_list_lt100
collection2=db.author_scholarlink_lt100
collection3 = db.author_scholarlink
data = collection.find({'cite_num':{'$gt':0,'$lt':100}})

data1 = collection2.find()
data2 = collection3.find()

existpaper = pd.DataFrame(list(data1))
existpaper2 = pd.DataFrame(list(data2))
dicdata = pd.DataFrame(list(data))
print('begin to drop duplicates')
# 将两个dataframe合并并根据papername 去重
df1 = pd.concat([existpaper,dicdata],axis=0)
df = pd.concat([existpaper2,df1],axis=0)
paper_data = df.drop_duplicates(subset=['author_link'],keep=False)
paper_data = paper_data[paper_data['cite_num'] < 100]

print(len(paper_data))

# paper_data = pd.DataFrame(list(data))
paper = list(paper_data['paper_name'])
author_list = list(paper_data['author'])
author_link = list(paper_data['author_link'])
rank = list(paper_data['rank'])
type= list(paper_data['type'])
cite_num = list(paper_data['cite_num'])
import scrapy


class AuthorSpider(scrapy.Spider):
    name = 'author'
    allowed_domains = ['dblp.uni-trier.de']
    # start_urls = ['http://dblp.uni-trier.de/']
    def get_ua(self):
        ua = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
              'Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60',
              'Opera/8.0 (Windows NT 5.1; U; en)',
              'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
              'Mozilla/5.t0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
              'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
              'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
              'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
              'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
              'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 SE 2.X MetaSr 1.0',
              'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)',
              'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)',
              'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)',
              "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"]
        return choice(ua)

    def start_requests(self):
        for i in range(len(author_link)):
            time.sleep(random.randint(1, 3))
            print('=======', i, '========')
            url = author_link[i]
            header = {
                "User-Agent": self.get_ua(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Referer": url,
                "Connection": "keep-alive"
            }
            print(url)
            yield scrapy.Request(url=url, headers=header, callback=self.parse,
                                 meta={ "paper_name": paper[i], 'cite_num': cite_num[i],
                    'author': author_list[i], 'rank': rank[i],'author_link':author_link[i]})




    def parse(self, response):
        author_item = JournalauthorItem()
        author_item['paper_name'] = response.meta['paper_name']
        author_item['cite_num'] = response.meta['cite_num']
        author_item['author'] = response.meta['author']
        author_item['author_link'] = response.meta['author_link']
        author_item['rank'] = response.meta['rank']

        try:
            person = response.xpath('//*[@id="info-section"]/div[1]/div/ul/li//text()').extract()
            person = [x for x in person if x != ' ']
            affiliation = []
            award = []
            for i in range(len(person)):
                if person[i] == 'affiliation:':
                    affiliation.append(person[i + 1])
                elif person[i] == 'award:':
                    award.append(person[i + 1][1:])
            if len(affiliation)!=0:
                author_item['affiliation']=affiliation
            if len(award) != 0:
                author_item['award']=award
        except:
            pass

        links_name = response.xpath('//*[@id="main"]/header/nav/ul/li[1]/div[@class="body"]/ul[1]/li/a/text()').extract()
        links = response.xpath('//*[@id="main"]/header/nav/ul/li[1]/div[@class="body"]/ul[1]/li/a/@href').extract()
        author_page = []
        alinks=[]
        for i in range(len(links)):
            if 'author\'s page'in links_name[i] and len(author_page)==0:
                author_page.append(links[i])
                alinks.append(links[i])
                author_item['author_page'] = links[i]
            elif 'ACM author profile'in links_name[i]:
                author_item['ACM_author_profile']=links[i]
                alinks.append(links[i])
            elif 'Mathematics Genealogy profile' in links_name[i]:
                author_item['Mathematics_Genealogy_profile'] = links[i]
                alinks.append(links[i])
            elif 'Wikipedia article'in links_name[i]:
                author_item['Wikipedia_article']=links[i]
                alinks.append(links[i])
            elif 'Google Scholar profile'in links_name[i]:
                author_item['Google_Scholar_profile']=links[i]
                alinks.append(links[i])
            elif 'Scopus profile'in links[i]:
                author_item['Scopus_profile']=links[i]
                alinks.append(links[i])

        if len(alinks)>0:
            author_item['info']=1
        else:
            author_item['info']=0

        yield author_item





