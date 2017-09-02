# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import time


class ArticlePipeline(object):
    def process_item(self, item, spider):
        return item


class WriteToMysql(object):
    def __init__(self):
        """
        实例化同时就配置好数据库，就不用每次写入都打开数据库，浪费资源
        """
        self.con = pymysql.connect(host='127.0.0.1',
                                   port=3306,
                                   user='root',
                                   password='0805',
                                   db='mysql',
                                   charset='utf8')
        self.cur = self.con.cursor()
        self.cur.execute('USE zhihu')
        self.count = 0

    def process_item(self, item, spider):
        nick_name = item.get('nick_name')
        head = item.get('head')
        url_need = item.get('url_need')
        try:
            self.cur.execute("insert into more_info(nick_name,head,url_need) values('{}','{}','{}')".format(nick_name[0],head[0],url_need[0]))
            self.count += 1

        except Exception as e:
            with open('ext.txt','a+') as f:
                print(e,file=f)

        # 每抓取1000条数据插入一次，并重新连接数据库
        if self.count == 1000:
            self.cur.close()
            self.con.commit()
            print("提交数据成功")
            self.__init__()
        return item

    def close_spider(self, spider):
        """
        当爬虫意外关闭时提交保存数据
        :return:
        """
        self.cur.close()
        self.con.commit()
