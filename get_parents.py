#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 17-9-1 下午2:23
# @Author  : xiaofang
# @Site    : 
# @File    : get_parents.py
# @Software: PyCharm
"""
通过入口网址：https://www.zhihu.com/people/lxzd/following
获取其关注列表的详细信息
有个小问题：知乎搜狗api关注列表每页只显示前三个，后面以js加载所以更改原计划，在每一页的页面源代码中通过正则表达式
可以获取当页所有用户的用户名从而可以拼接出完整url
"""

import requests
import pymysql
import re
from fake_useragent import UserAgent
import time


class Get_info():
    """
    这是一个解析url的类
    """
    ua = UserAgent()
    header = {'User-agent': ua.random}

    def __init__(self):
        """
        在类被实例化的同时家完成数据库的配置
        """
        self.i = 1
        self._con = pymysql.connect(host='127.0.0.1',
                                    port=3306,
                                    user='root',
                                    password='0805',
                                    db='mysql', charset="utf8")
        self.cur = self._con.cursor()

    def get_info(self):

        url = 'https://www.zhihu.com/people/fei-zhi-hong/following?page='
        full_url = url + str(self.i)
        time.sleep(1)
        body = requests.get(full_url, headers=self.header)
        code = body.status_code
        if code == 200:
            html = body.text

            # 从网页源代码中利用正则表达式提取用户信息
            infos = re.compile(r'\]\,\&quot\;isFollowing\&quot(.*?)badge\&quot\;\:\[', re.S).findall(html)
            next_page = re.search(
                'class="Button PaginationButton PaginationButton-next Button--plain" type="button">下一页</button>', html)

            for info in infos:
                url_need = re.compile('urlToken&quot\;\:&quot\;(.+?)\&quot\;').findall(info)
                nick_name = re.compile(r'name\&quot\;\:\&quot\;(.+?)\&quot\;').findall(info)
                head = re.compile('headline&quot\;\:\&quot\;(.+?)\&quot\;').findall(info)

                if url_need is not None:
                    # 拼接完整url（拼接所有关注者的关注列表url与被关注者url）
                    # followers_url = 'https://www.zhihu.com/people/'+url_need[0]+'/followers'
                    # following_url = 'https://www.zhihu.com/people/'+url_need[0]+'/following'
                    # print(followers_url, following_url,  nick_name, head)
                    # 写入mysql数据库

                    try:
                        self.cur.execute(
                            "INSERT INTO zhihu.parents(nick_name,head,url_need)VALUES('{}','{}','{}')".format(nick_name[0], head[0],
                                                                                                        url_need[0]))
                        print('数据采集中。。。')
                        print(nick_name, head, url_need)
                    except Exception as e:
                        print(e)

                else:
                    # 有可能因为随机情况导致解析失败，所以给一次重试的机会
                    for i in range(1):
                        self.get_info(full_url)

            if next_page is not None:
                self.i += 1
                self.get_info()
            else:
                # 说明所有数据抓取完毕
                self.cur.close()
                self._con.commit()
        else:
            print('服务器错误')


if __name__ == "__main__":
    all_info = Get_info()
    all_info.get_info()
