# -*- coding: utf-8 -*-
import scrapy
import pymongo
from random import choice
import random
import time
import os
import difflib
from urllib.parse import quote
import string
from unicodedata import normalize, category
# from citation.items import CitationItem
import pandas as pd

client = pymongo.MongoClient(host='localhost',port=27017)
db=client.paper
collection=db.conf_paper_citation
data = collection.find({'cite_num':'null'})
df = pd.DataFrame(list(data))
print(df)
paper_data = df.drop_duplicates(subset=['paper_name'],keep=False)
paper = list(paper_data['paper_name'])
paper = paper[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
# author = [x[0] for x in list(paper_data['author_list'])]
author_list = list(paper_data['author_list'])[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
author_link = list(paper_data['author_link'])[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
conf_type = list(paper_data['conf_type'])[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
conf = list(paper_data['conf'])[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
topic = list(paper_data['topic'])[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
year = list(paper_data['year'])[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
num = list(paper_data['num'])[paper.index('Towards developing a large energy store using small scale distributed batteries: poster abstract'):]
print(len(paper))

class UpdateCitenumSpider(scrapy.Spider):
    name = 'update_citenum'
    allowed_domains = ['cn.bing.com/academic']
    # start_urls = ['http://cn.bing.com/academic']

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

    def dif_paper(self,paper1,paper2):
        paper1 = paper1.replace('-', '')
        paper1 = paper1.replace('[CITATION]', '')
        paper1 = paper1.replace('[C]', '')
        paper1 = paper1.replace('[引用]', '')
        paper1 = paper1.replace('°', '')
        paper1 = paper1.replace('&', 'and')
        paper1 = paper1.replace('[PDF]', '')
        paper1 = paper1.replace(' ', '').lower()
        paper2 = paper2.replace('-', '')
        paper2 = paper2.replace('°', '')
        paper2 = paper2.replace('&', 'and')
        paper2 = paper2.replace(' ', '').lower()
        print('paper1', paper1)
        print('paper2', paper2)
        print(paper1 == paper2)
        return paper1,paper2

    def start_requests(self):
        for i in range(len(paper)):
            # time.sleep(random.randint(1, 5))
            print('======================{}======================'.format(i))
            paper_name = paper[i].replace('#', '')
            # author1 = ''.join([c for c in normalize('NFD', author[i]) if category(c) != 'Mn'])
            # query = '+'.join(paper_name.split()) + '+' + '+'.join(author1.split())
            query = '+'.join(paper_name.split())
            url = 'https://cn.bing.com/academic/search?q={}'.format(query)
            url = quote(url, safe=string.printable)

            header = {
                "User-Agent": self.get_ua(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
                "Referer": url,
                "Connection": "keep-alive"
            }
            print(url)
            yield scrapy.Request(url=url, headers=header, callback=self.parse,meta={"conf_type":conf_type[i],"paper_name": paper[i],"conf":conf[i],
                                                                                    "author_link":author_link[i],"num":num[i],"year":year[i],
                                                                                    "author_list":author_list[i],'topic':topic[i]})

    def parse(self, response):
        print('reponse===========2')
        print(response)
        print('getting message')
        # paper_item = CitationItem()
        # cite_num：该paper被引用的次数 有的paper没有被引次数，赋值为0
        paper_name = ''.join(response.xpath('//*[@id="b_results"]/li[1]/h2/a/strong/text()').extract())
        num = 1
        paper2 = response.meta['paper_name']
        paper1, paper2 = self.dif_paper(paper_name, paper2)
        authorlist = response.meta['author_list']
        authors = ''.join([i.replace('-', '') for i in authorlist]).lower()
        print(authors)
        try:
            author= response.xpath('//*[@id="b_results"]/li[1]/div/div[1]/text()').extract_first().split(' ')[0].lower()
        except:
            author ='noauthor'
        print(author)
        if paper1 == paper2 or author in authors:
            num = 1
            try:
                cite_num = response.xpath('//*[@id="b_results"]/li[1]/div/div[2]/a[2]/text()').extract_first()
                print('citenum', cite_num)
                try:
                    number = filter(str.isdigit, cite_num)
                    cite_num = int(''.join(list(number)))
                except:
                    print('no cite num')
                    cite_num = 0
            except:
                print('paper1', paper1)
                cite_num = 0

        else:
            cite_num = 'null'


        timeStamp = time.time()
        timeArray = time.localtime(timeStamp)
        creat_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        print('citenum', cite_num)

        print({'paper_name': response.meta['paper_name'],'cite_num': cite_num, 'creat_time': creat_time, 'cite_from': 'bing'})


        collection.update_many({'paper_name': response.meta['paper_name']},
                               {'$set': {'cite_num': cite_num, 'creat_time': creat_time, 'cite_from': 'bing'}})





