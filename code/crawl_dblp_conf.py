import requests
import pymongo
import re
import pandas as pd
from lxml import etree
client = pymongo.MongoClient(host='localhost',port=27017)
db=client.top_conference
collection=db.conf_paper
collection1 = db.conf_info

def get_html(url):
    '''
    :param url: 爬取的链接
    :return: 返回解析的页面
    '''
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
                   # 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'}
    response = requests.get(url, headers=headers).content
    html = etree.HTML(response)
    return html

def insert_paper(conf,year,num,conf_type,conf_html,collection):
    '''
    :param conf: 会议的名称
    :param year: 会议的年份
    :param num: 属于当前会议的第几个链接，会议的具体信息和会议中的论文是分开存储的，方便后续对比查看会议具体信息
    :param conf_type: 会议是否属于workshop/conference
    :param conf_html: 某会议页面的html源码
    :param collection: 插入的数据库表
    :return: null
    '''
    ul_list = conf_html.xpath('//ul[@class="publ-list"]')
    # 除去会议的大标题，取出所有小标题作为论文的topic(topic位于每个ul标签的上一个header标签)
    # 有的会议没有分topic
    if len(ul_list)==1:
        paper_list = conf_html.xpath('//ul[@class="publ-list"][1]//li[@class="entry inproceedings"]')
        for i in range(len(paper_list)):
            paper_name = conf_html.xpath('//li[@class="entry inproceedings"][{}]//span[@class="title"]/text()'.format(i + 1))[0].replace('.', '')
            author_list = conf_html.xpath('//li[@class="entry inproceedings"][{}]//span[@itemprop="author"]/a/span/text()'.format(i + 1))
            author_link = conf_html.xpath('//li[@class="entry inproceedings"][{}]//span[@itemprop="author"]/a/@href'.format(i + 1))
            data = {
                'conf': conf, 'year': year,'num':num, 'conf_type': conf_type, 'topic': '', 'paper_name': paper_name,
                'author_list': author_list, 'author_link': author_link
            }
            print(data)
            collection.insert(data)
    # 分了topic的会议
    else:
        for i in range(len(ul_list)-1):
            topic = conf_html.xpath('//ul[@class="publ-list"][{}]/preceding-sibling::header[1]//text()'.format(i+2))[0].replace('\n','')
            print(topic)
            paper_list = conf_html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry inproceedings"]'.format(i+2))
            for j in range(len(paper_list)):
                paper_name = conf_html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry inproceedings"][{}]//span[@class="title"]/text()'.format(i+2,j+1))[0].replace('.','')
                author_list = conf_html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry inproceedings"][{}]//span[@itemprop="author"]/a/span/text()'.format(i+2,j + 1))
                author_link = conf_html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry inproceedings"][{}]//span[@itemprop="author"]/a/@href'.format(i+2,j + 1))
                data = {
                    'conf': conf, 'year': year,'num':num, 'conf_type': conf_type, 'topic':topic, 'paper_name': paper_name,
                    'author_list': author_list, 'author_link': author_link
                }
                print(data)
                collection.insert(data)

def get_confinfo(html,conf):
    '''
    :param html: 某会议页面的html源码
    :return: 字典形式的 {会议链接:会议所对应的id}，如aaai会议下有三个子会议，则三个子会议的id分别为0,1,2
    '''
    dic={}
    ul_list = html.xpath('//ul[@class="publ-list"]')
    for i in range(len(ul_list)):
        conf_title = ''.join(html.xpath('//ul[@class="publ-list"][{}]/preceding-sibling::header[1]//text()'.format(i+1))).replace('\n','')
        conf_list = html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry editor toc"]'.format(i+1))
        print(conf_title)
        try:
            match_obj = re.match(".*?(\d{4}).*?", conf_title)
            year = match_obj.group(1)
        except:
            year = ''


        for j in range(len(conf_list)):
            try:
                link_title = html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry editor toc"][{}]/article/a[@class="toc-link"]/text()'.format(i+1,j+1))[0]
                print(link_title)
                if link_title == '[contents]':
                    conf_link = html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry editor toc"][{}]//a/@href'.format(i+1,j+1))[0]
                    conf_info = html.xpath('//ul[@class="publ-list"][{}]//li[@class="entry editor toc"][{}]//span[@class="title"]/text()'.format(i+1,j+1))[0]
                    dic[conf_link]=j

                    conf_data={
                        'conf':conf,
                        'year':year,
                        'conf_title':conf_title,
                        'num':j,
                        'conf_info':conf_info
                    }
                    print(conf_data)
                    collection1.insert(conf_data)
            except:
                continue
    return dic


def get_conf(html,conf):
    conflist = get_confinfo(html,conf)
    # lst = list(conflist.keys())
    # index = lst.index('https://dblp.uni-trier.de/db/conf/icra/icra2018.html')
    # conflist = dict(zip(list(conflist.keys())[index:],list(conflist.values())[index:]))
    for conf_url in conflist:
        print(conf_url)
        num = conflist.get(conf_url)
        # 取出会议的头部信息
        conf_html = get_html(conf_url)
        conf_title = conf_html.xpath('//h1/text()')[0].replace('\n', '')
        # 不同的会议网站的title结构可能有差别
        try:
            conf_info = conf_html.xpath('//article/span[1]/text()')[0]
        except:
            conf_infohtml = conf_html.xpath('//li[@class="entry editor"]//span[@class="title"]/text()')
            if conf_infohtml:
                conf_info = conf_infohtml[0]
            else:
                conf_info = ''

        if 'Workshop' in conf_info:
            conf_type = 'workshop'
        else:
            conf_type = 'conference'

        match_obj = re.match(".*?(\d{4}).*?", conf_title)
        if match_obj:
            year = match_obj.group(1)

        print(conf_title)

        # 取出会议论文列表
        # 有的会议首页分成volume的链接，如果首页是volume1，volume2...
        volume_list = conf_html.xpath('//*[@id="main"]/ul[2]/li/a/@href')
        if volume_list:
            print('there are {} volumes'.format(len(volume_list)))
            for volume_url in volume_list:
                volume_html = get_html(volume_url)
                insert_paper(conf, year,num, conf_type, volume_html, collection)

        else:
            print('getting paper list')
            insert_paper(conf, year,num, conf_type, conf_html, collection)


if __name__ == '__main__':
    # 计算机体系结构/并行与分布计算/存储系统 a类会议
    conflist1 = ['ppopp','fast','dac','hpca','micro','sc','asplos','isca','usenix']
    # 计算机网络 a类会议
    conflist2 = ['sigcomm','mobicom','infocom','nsdi']
    # 网络与信息安全 a类会议 sp-s&p  uss-usenix security
    conflist3 = ['ccs','eurocrypt','sp','crypto','uss']
    # 软件工程/系统软件/程序设计语言 a类会议
    conflist4 = ['pldi', 'popl', 'sigsoft','sosp','oopsla','kbse','icse','issta','osdi']
    # 数据库/数据挖掘/内容检索 a类会议
    conflist5 = ['sigmod', 'kdd', 'sigir', 'vldb']
    # 计算机科学理论 a类会议
    conflist6 = ['stoc', 'soda', 'cav','focs','lics']
    # 计算机图形学与多媒体 a类会议 mm-acm mm
    conflist7 = ['mm', 'siggraph','vr','visualization']
    # 人工智能 a类会议
    conflist8 = ['aaai', 'nips', 'acl', 'cvpr','iccv','icml','ijcai']
    # 人机交互与普适计算 a类会议
    conflist9 = ['cscw', 'chi','huc']
    # 人机交互与普适计算 a类会议
    conflist10 = ['www', 'rtss']

    # 清华大学计算机学科推荐学术a类会议列表
    # 高性能计算
    qhconf1 = ['isca', 'fast', 'asplos', 'eurosys', 'hpca','sigmetrics','fpga','usenix','micro','sc','ppopp','dac']
    # 计算机网络
    qhconf2 = ['sigcomm','nsdi','mobicom','mobisys','imc','ipsn','sensys','infocom','conext','icnp']
    # 网络与信息安全 uss-usenix security
    qhconf3 = ['sp','ndss','uss','ccs','eurocrypt','crypto','ches','asiacrypt']
    # 系统软件与软件工程
    qhconf4 = ['osdi','icse','sosp','popl','pldi','fse','esec','issta','oopsla','ase']
    # 数据库与数据挖掘
    qhconf5 = ['sigmod', 'sigkdd', 'sigir', 'wsdm', 'vldb', 'icde', 'pods']
    # 理论计算机科学
    qhconf6 = ['stoc','focs','soda','cav','lics','ccc','icalp']
    # 计算机图形学与多媒体
    qhconf7 = ['siggraph','visualization','mm','vr']
    # 人工智能与模式识别
    qhconf8 = ['cvpr','iccv','icml','acl','eccv','colt','nips','aaai','emnlp','icra','iclr','rss']
    # 人际交互与普适计算 huc-ubicomp
    qhconf9 = ['cscw','huc','uist','chi']
    # 综合与交叉 sigecom-acm conference on economics and computation
    qhconf10 = ['recomb','ismb','www','sigecom']



    conflist = conflist1+conflist2+conflist3+conflist4+conflist5+conflist6+conflist7+conflist8+conflist9+conflist10
    # conflist = conflist[conflist.index('mm')+1:]
    qhconflist = qhconf1 + qhconf2 + qhconf3 + qhconf4 + qhconf5 + qhconf6 + qhconf7 + qhconf8 + qhconf9 + qhconf10
    # conflist2 = [a for a in qhconflist if a not in conflist]
    # conflist2 = conflist2[conflist2.index('icra')+1:]
    # conflist2 = ['sigecom']
    data = pd.DataFrame(collection1.find())
    existconf = list(set(list(data['conf'])))
    # existconf = [a for a in list(set(list(data['conf']))) if a!='icvtcra']
    print(existconf)
    # conflist2 = ['kbse', 'kdd', 'nips', 'iclr', 'icml', 'aaai', 'ijcai', 'aistats', 'cdc', 'amcc', 'naacl', 'semeval', 'lrec', 'coling', 'eacl', 'conll', 'wmt', 'slt', 'semco', 'wassa', 'si3d', 'eurographics', 'vda', 'dac', 'isscc', 'micro', 'vlsic', 'iscas', 'fpga', 'aspdac', 'iccad', 'icccn', 'sigcomm', 'icc', 'globecom', 'uss', 'sp', 'ndss', 'crypto', 'pkc', 'ches', 'icse', 'esorics', 'acsac', 'eccv', 'bmvc', 'wacv', 'icip', 'accv', 'icpr', 'isca', 'hpca', 'osdi', 'micro', 'ipps', 'aistats', 'recsys', 'sdm', '', 'pakdd', 'dsaa', 'cikm', 'www', 'sigmod', 'icse', 'cikm', 'icwsm', 'recsys', 'icwsm', 'semweb', '', 'cec', 'gecco', 'ssci', 'icse', 'bracis', 'emo', 'icnc', 'icnc', 'is', 'acfie', 'ccscw', 'uist', 'hri', 'ACMdis', 'icmi', 'hci', 'iui', 'assets', 'mm', 'icip', 'mir', 'ismir', 'mmsys', 'icmcs', 'qomex', 'icassp', 'interspeech', 'icip', 'vtc', 'cisse', 'pldi', 'kbse', 'msr', 'ispw', 'issta', 'oopsla', 'icsm',
    #   https://dblp.uni-trier.de/db/conf/icsm/icsme2016.html
    # conflist2 = ['ppopp', 'wcre', 'focs', 'soda', 'icalp', 'esa']
    # conflist2 = ['icsm','cec', 'bmvc', 'icccn', 'globecom', 2014-
    # conflist2 = ['dsaa', 'slt', 'conll', 'isscc', 2017-
    # conflist2 = ['wacv', 'vlsic', 'wassa', 'accv', 'sdm', 'si3d', 'pkc', 'ipps', 'recsys', 'pakdd', 'icwsm', 'semco', 'acsac', 'aspdac',-1995
    conflist2 = ['cikm', 'iscas']


    for conf in conflist2:
        if conf not in existconf:
            confurl = 'https://dblp.uni-trier.de/db/conf/{}/'.format(conf)
            html = get_html(confurl)
            get_conf(html,conf)

