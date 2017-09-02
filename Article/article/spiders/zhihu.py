# -*- coding: utf-8 -*-
"""
通过现有url获取各url的被关注列表信息
"""
import scrapy
import re
from scrapy.loader import ItemLoader
from article.items import ZhihuItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    # allowed_domains = ['www.zhihu.com/people/']
    LOG_LEVEL = 'ERROR'

    start_urls = 'from_mysql_get_url'  # 因为这里是类属性，不能通过self来参数，所以使用同名字符串

    def from_mysql_get_url(self):
        """
        从数据库获取数据
        :return:
        """
        import pymysql
        con = pymysql.connect(host='127.0.0.1',
                              port=3306,
                              user='root',
                              password='0805',
                              db='mysql',
                              charset='utf8')
        cur = con.cursor()
        cur.execute('USE zhihu')
        cur.execute('SELECT url_need FROM parent')
        url_need_list = cur.fetchall()
        url_list = ['https://www.zhihu.com/people/' + url_need[0] + '/followers?page=1' for url_need in url_need_list]
        return url_list

    def start_requests(self):

        for url in self.from_mysql_get_url():
            yield scrapy.Request(url=url,callback=self.parse)

    def parse(self, response):
        global head, nick_name, url_need

        infos = re.compile(r'\]\,\&quot\;isFollowing\&quot(.*?)badge\&quot\;\:\[', re.S).findall(response.body.decode('utf-8'))
        next_page = re.search(
                'class="Button PaginationButton PaginationButton-next Button--plain" type="button">下一页</button>', response.body.decode('utf-8'))

        for info in infos:
            url_need = re.compile('urlToken&quot\;\:&quot\;(.+?)\&quot\;').findall(info)[0]
            nick_name = re.compile(r'name\&quot\;\:\&quot\;(.+?)\&quot\;').findall(info)[0]
            head = re.compile('headline&quot\;\:\&quot\;(.+?)\&quot\;').findall(info)[0]
            i = ItemLoader(item=ZhihuItem(), response=response)
            i.add_value('nick_name', nick_name)
            i.add_value('head', head)
            i.add_value('url_need', url_need)
            print(url_need, nick_name, head)
            yield i.load_item()

        if next_page is not None:
            # 在这里需要构造next—page的url连接
            # response的url就是类似这种https://www.zhihu.com/people/fei-zhi-hong/following?page=1
            # 如果有下一页那么在下次请求的时候就需要在后面改后缀？page=2.。。。
            url = response.url
            # url的最后一位就是页码数量，但是刚开始是str所以改为int然后+1，最后改为str，记得截取掉原先的最后一位
            yield scrapy.Request(url[:-1] + str(int(url[-1])+1), callback=self.parse)

