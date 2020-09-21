* 数据存储于链接: https://pan.baidu.com/s/1nudkCMEoiWg-gy8zRJURag  密码: g6ii

* 数据说明：

主要从dblp中爬取了三百多个期刊和会议（来源于Google matrics、ccf和清华计算机协会评定的a类计算机会议/期刊，列表存于“top_paper.xlsx”中），再从中获取dblp各期刊/会议有史以来录用的所有paper，以及从Google Scholar爬取若干计算机领域经典方向的前100名学者的列表，由学者的共同学者向下爬取相关的学者形成学者网络。这里存储了学者在Google Scholar中对应的profileid作为之后对应学者和论文的ID

1、all_author_scholarlink：dblp中论文的学者的相关信息，包含affiliation/主页/等信息，信息较少，rank表示该作者在论文的共同作者中的排名分位（0-1）

2、conf_chinese_scholar：主要包含高性能领域的会议相关论文的国内学者的相关信息，来源于ieeexplore

3、conf_info：top会议的会议相关信息

4、conf_paper：dblp中爬取的论文的相关作者信息，信息较少，后续根据这里的论文名称检索相应的citation

5、conf_paper_citation：对于爬取到的dblp上的会议论文在bing上进行关键词检索，得到该论文的citation及其他相关信息

6、journal_info/paper/paper_citation：同上

7、scholar_college：爬取国内高校计算机相关学院的官网中的教师个人信息

8、top_scholar_0：从Google Scholar中获取的学者的相关信息，step表示层级，第一层为各大计算机细分领域下引用量前100的学者信息，依次为各自合著学者的信息

9、top_scholar_paper：由上一步的学者主页得到的该学者所发表的所有论文的链接信息

10、top_scholar_paper_detail：由上一步的论文链接进一步爬取得到的论文详细信息数据

* 代码说明：

1、code: crawl_dblp_conf/ crawl_dblp_journal
按照top_paper中的title爬取dblp上的相应期刊/会议的论文，会议/期刊的相关信息存储于conf_info/journal_info中，相应的论文信息存储于conf_paper/journal_paper中

2、code：confauthor/journalauthor文件夹中 （scrapy框架）
按照1中得到的作者的dblp链接获取作者在dblp中的信息，存于all_author_scholarlink中

3、code: conf/journal文件夹中 （scrapy框架）
按照1中论文的名称爬取bing上该论文的citation次数，相应数据存储于conf_paper_citation/journal_paper_citation中

4、code：经测试google scholar的检索框搜索学者/论文会遇到反爬问题且较难解决，这里采取从学者的profile界面入手，爬取其论文和合著学者等相关信息，遇到反爬问题较少。
从Google scholar中搜索计算机领域相关的各细分方向下引用量前100的学者，然后从学者的profile界面爬取学者所发表的所有论文信息，以及学者的合著学者，循环往复，同时记录爬取的层级，按层级往下一层层爬取学者的合著学者及其论文信息。
