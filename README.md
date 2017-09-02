<h3>项目目的：抓取知乎用户信息</h3>
算法：通过知乎用户间的关注关系（关注与被关注），首先通过某一可以查看关注列表的大V帐号，获取其关注列表
例如https://www.zhihu.com/people/dongweiming/following?page=1 这是随机打开的某个大v的帐号，
通过查看比较符合我们的期望条件（有差不多13页关注列表，且对外公开，而且他的关注列表也比较优质，有众多粉丝）

1：获取部分大v帐号存入数据库(使用requests）
    程序：get_parents.py
    表：parent （id，nick_name,head, url_need)

2:以之前通过get_parents.py新获取的168个知乎大v信息，构造url，（每个大v平均10000位关注者）使用scrapy库
进行信息抓取。（采用抓取后去重）
    
    


