import requests
import pymongo
import re
import pandas as pd
from lxml import etree
client = pymongo.MongoClient(host='localhost',port=27017)
db=client.top_journal
collection=db.journal_paper
collection1 = db.journal_info

# mongodbUri = 'mongodb://sensetalent:Goodsense8@172.30.1.74:3711/admin'
# client = pymongo.MongoClient(mongodbUri)
# db=client.sensetalent
# collection=db.journal_paper
# collection1 = db.journal_info


def get_html(url):
    '''
    :param url: 爬取的链接
    :return: 返回解析的页面
    '''
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0'}
    response = requests.get(url, headers=headers).content
    html = etree.HTML(response)
    return html


def get_journalnfo(html,journal):
    '''
    :param html: 某期刊页面的html源码
    :return: 字典形式的 {期刊volume链接:期刊对应的volume}
    '''
    dic={}
    ul_list = html.xpath('//div[@id="main"]/ul')
    journal_name = html.xpath('//h1/text()')[0]
    volumes = html.xpath('//*[@id="main"]/ul/li/a/text()')

    journal_data = {
        'journal': journal,
        'journal_name': journal_name,
        'volumes': volumes,
    }
    print(journal_data)
    collection1.insert(journal_data)

    for i in range(len(ul_list)):
        journal_list = html.xpath('//*[@id="main"]/ul[{}]/li'.format(i+1))
        for j in range(len(journal_list)):
            volume_name = html.xpath('//*[@id="main"]/ul[{}]/li[{}]//text()'.format(i+1,j+1))[0]
            print(volume_name)
            if volume_name!='...':
                link_title = html.xpath('//*[@id="main"]/ul[{}]/li[{}]/a/text()'.format(i+1,j+1))
                print(link_title)
                journal_link = html.xpath('//*[@id="main"]/ul[{}]/li[{}]/a/@href'.format(i+1,j+1))
                for k in range(len(journal_link)):
                    dic[journal_link[k]]=link_title[k]

    return dic



def insert_journal(html,journal):
    '''
    :param html: 某期刊页面的html源码
    :param journal: 某期刊的名字
    :return: 无 将论文数据插入数据库
    '''
    journallist = get_journalnfo(html,journal)
    # lst = list(conflist.keys())
    # index = lst.index('https://dblp.uni-trier.de/db/conf/mm/mm2000w.html')
    # conflist = dict(zip(list(conflist.keys())[index:],list(conflist.values())[index:]))
    for journal_url in journallist:
        print(journal_url)
        volume = journallist.get(journal_url)
        volume_html = get_html(journal_url)
        journal_title = volume_html.xpath('//h2/text()')[0]

        try:
            match_obj = re.match(".*?(\d{4}).*?", journal_title)
            year = match_obj.group(1)
        except:
            year = ''
        ul_list = volume_html.xpath('//ul[@class="publ-list"]')
        for i in range(len(ul_list)):
            paper_list = volume_html.xpath('//ul[@class="publ-list"][{}]/li[@class="entry article"]'.format(i+1))
            for j in range(len(paper_list)):
                paper_name = volume_html.xpath('//ul[@class="publ-list"][{}]/li[@class="entry article"][{}]//span[@class="title"]/text()'.format(i + 1,j+1))[0].replace('.', '')
                author_list = volume_html.xpath('//ul[@class="publ-list"][{}]/li[@class="entry article"][{}]//span[@itemprop="author"]/a/span/text()'.format(i + 1,j+1))
                author_link = volume_html.xpath('//ul[@class="publ-list"][{}]/li[@class="entry article"][{}]//span[@itemprop="author"]/a/@href'.format(i + 1,j+1))
                data = {
                    'journal': journal, 'year': year, 'volume': volume, 'type': 'journal',
                    'paper_name': paper_name,
                    'author_list': author_list, 'author_link': author_link
                }
                print(data)
                collection.insert(data)



if __name__ == '__main__':
     # 计算机体系结构/并行与分布计算/存储系统 a类期刊
    journallist1 = ['tocs','tos','tcad','tc','tpds']
    # 计算机网络 a类期刊
    journallist2 = ['jsac','tmc','ton']
    # 网络与信息安全 a类期刊
    journallist3 = ['tdsc','tifs','joc']
    # 软件工程/系统软件/程序设计语言 a类期刊
    journallist4 = ['toplas','tosem','tse']
    # 数据库/数据挖掘/内容检索 a类期刊
    journallist5 = ['tods','tois','tkde','vldb']
    # 计算机科学理论 a类期刊
    journallist6 = ['tit','iandc','siamcomp']
    # 计算机图形学与多媒体 a类期刊
    journallist7 = ['tog','tip','tvcg']
    # 人工智能 a类期刊
    journallist8 = ['ai', 'pami', 'ijcv','jmlr']
    # 人机交互与普适计算 a类期刊
    journallist9 = ['tochi','ijmms']
    # 交叉/综合/新兴 a类期刊
    journallist10 = ['jacm', 'pieee']

    # 清华大学计算机学科推荐学术a类期刊列表
    # 高性能计算
    qhjournal1 = ['tocs','tpds','tc','tcad','tos']
    # 计算机网络
    qhjournal2 = ['jsac','tmc','ton','tcom']
    # 网络与信息安全 joc-journal of cryptology
    qhjournal3 = ['tifs','tdsc','joc']
    # 系统软件与软件工程
    qhjournal4 = ['tse','tosem','toplas']
    # 数据库与数据挖掘
    qhjournal5 = ['tkde','vldbj','tods','tois']
    # 理论计算机科学
    qhjournal6 = ['sicomp','tit','talg','iandc']
    # 计算机图形学与多媒体
    qhjournal7 = ['tip','tog','tmm','tvcg','cad']
    # 人工智能与模式识别
    qhjournal8 = ['tpami','ijcv','jmlr','tr','ai','taslp']
    # 人际交互与普适计算
    qhjournal9 = ['ijhcs','tochi']
    # 综合与交叉 pieee-proceedings of the ieee  chinaf-science china
    qhjournal10 = ['jacm','pieee','chinaf']

    journallist = journallist1 + journallist2 + journallist3 + journallist4 + journallist5 + journallist6 + journallist7 + journallist8 + journallist9 + journallist10
    qhjournallist = qhjournal1 + qhjournal2 + qhjournal3 + qhjournal4 + qhjournal5 + qhjournal6 + qhjournal7 + qhjournal8 + qhjournal9 + qhjournal10

    # journallist2 = [a for a in qhjournallist if a not in journallist]
    # journallist = journallist[journallist.index('ijmms') + 1:]

    # 取出已爬取的期刊名称
    data = pd.DataFrame(collection1.find())
    existconf = list(set(list(data['journal'])))
    # existconf = [a for a in list(set(list(data['journal']))) if a!='ijmms']
    # print(existconf)
    # journallist2 = ['ijmms', 'siamcomp', 'pami', 'vldb', 'eswa', 'tsmc', 'tnn', 'asc', 'ijon', 'jmlr', 'tfs', 'kbs', 'nca', 'nn', 'jifs', 'eaai', 'ras',
    #  https://dblp.uni-trier.de/db/journals/ras/ras56.html
    #  ras 2009-
    #  https://dblp.uni-trier.de/db/journals/scl/scl43.html
    # journallist2 = ['tac', 'tfs', 'tsmc', 'tcst', 'jirs', 'scl',
    #  https://dblp.uni-trier.de/db/journals/csl/csl27.html  2014-
    # journallist2 = ['tcns', 'ijsysc', 'ijcon', 'jrm', 'tacl', 'csl',
    #  https://dblp.uni-trier.de/db/journals/tcas/tcasI56.html
    # journallist2 = ['coling', 'nle', 'tvcg', 'vc', 'cagd', 'cvgip', 'jssc', 'tcas', 'tvlsi', 'tcad', 'tcas',
    #  https://dblp.uni-trier.de/db/journals/jnca/jnca27.html
    # journallist2 = ['cm', 'tcom', 'jnca',
    # journallist2 = [ 'tmc', 'icl', 'sj', 'cn', 'ton']
    # journallist2 = ['tifs', 'compsec', 'tdsc', 'scn', 'dcc', 'tip', 'pr', 'ijcv', 'mia', 'prl', 'cviu', 'jvcir', 'ivc', 'tcc']
     # , 'tsc', 'tjs', 'ijdsn', 'sigmetrics', 'tkde', 'datamine', 'kais', 'tist', 'jbd', 'tkdd', 'snam', 'adac', 'ipm', 'kais', 'tist', 'cce', 'isci', 'sensors', 'access', 'tit', 'tii', 'csur', 'pieee', 'cphysics', 'misq', 'cacm', 'soco', 'swevo', 'ec', 'ijbic', 'nc', 'memetic', 'alife', 'gpem', 'tfs', 'kbs', 'jifs', 'soco', 'fss', 'ijar', 'ijfs', 'ijgs', 'ijitdm', 'fodm', 'ijufks', 'mvl', 'taffco', 'ijmms', 'thms', 'behaviourIT', 'ijhci', 'tochi', 'toh', 'tcsv', 'mta', 'jvcir', 'spic', 'iet-ipr', 'ieeemm', 'ejivp', 'mms', 'tip', 'tsp', 'spm', 'tcsv', 'spl', 'sigpro', 'jstsp', 'taslp', 'wcl', 'jvcir', 'siamis', 'dsp', 'spic', 'jss', 'ese', 'tse', 'software', 'scp', 'jacm', 'siamcomp', 'tcs', 'jcss', 'algorithmica', 'iandc', 'lmcs', 'fuin', 'logcom', 'rsa', 'talg', 'tplp', 'ipl']
    journallist2 = ['tcs']
    for journal in journallist2:
        if journal not in existconf:
            journalurl = 'https://dblp.uni-trier.de/db/journals/{}/'.format(journal)
            html = get_html(journalurl)
            insert_journal(html,journal)
