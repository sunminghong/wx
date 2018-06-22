#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 9:47
# @Author  : dongdong Zou
# @File    : test.py.py
# @license : Copyright(C), 安锋游戏
import requests
from bs4 import BeautifulSoup
import re
from common_utils.common import convert_date_from_datetime
from common_utils.config import Config
from common_utils.database import mysql_client
from libs.MetaModel import Article_Meta_Data

media_content = 1  # 虎嗅网
start_url = "https://www.huxiu.com"
headers = {'User-agent': 'Mozilla/5.0'}  # 模仿登录的设备user-Agent


def get_data_list():
    page = requests.get(start_url, headers=headers, timeout=5)
    content = page.text   # 源码的内容
    soup = BeautifulSoup(content,'lxml')   # 用'lxml'来进行解析

    data_urls = []
    data_list = soup.find_all(href=re.compile(r'/article/(\d+).html'))
    for item in data_list:
        data_urls.append(item['href'])

    return data_urls


def get_content(hupu_url):
    try:
        page=requests.get(hupu_url,headers=headers,timeout=5)

        content = page.text   # 源码的内容
        soup = BeautifulSoup(content,'lxml')   # 用'lxml'来进行解析
        # 这是原代码里面的内容，soup.title就是要读取的标题牛肉
        title=soup.title
        title_0 = title.contents[0].split("-")[0]

        # 获取关键字描叙
        keywords = soup.find(attrs={"name":"keywords"})
        if keywords:
            keywords_content = keywords["content"]
            if keywords_content:
                keywords_content = keywords_content
            else:
                keywords_content = 0
        else:
            keywords_content = 0

        # 获取文章内容简要介绍
        description = soup.find(attrs={"name":"description"})
        if description:
            description_content = description["content"]
            if description_content:
                description_content = description_content
            else:
                description_content = 0
        else:
            description_content = 0

        # 提取文章主要内容
        bodys = soup.find_all(class_="article-content-wrap")
        body = BeautifulSoup(str(bodys[0]),'lxml')
        tips = body.find_all("p")

        main_content=""
        for tip in tips:
            if "br/" not in str(tip):
                if tip != []:    # 防止得到的tip为空
                    main_content += str(tip)

        times = soup.find(class_="article-time")
        if times:
            times_content = times.text
        else:
            times_content = '1970-01-01 08:00:00'

        content_list = {'title': title_0, 'media': media_content, 'keywords': keywords_content,
                        'summary': description_content, 'content': main_content, 'time': times_content}
        return content_list
    except:
        return None


if __name__ == '__main__':
    mysql = mysql_client(Config().get_config('mysql', 'host'),
                         Config().get_config('mysql', 'port'),
                         Config().get_config('mysql', 'database'),
                         Config().get_config('mysql', 'username'),
                         Config().get_config('mysql', 'password'))

    session = mysql.get_session()

    data_urls = get_data_list()

    for url in data_urls:   # 168971
        hupu_url_i = 'https://www.huxiu.com' + url
        try:
            page = requests.get(hupu_url_i, headers=headers, timeout=15)
        except:
            continue
        print(hupu_url_i)
        content = page.text   # 源码的内容
        soup = BeautifulSoup(content, 'lxml')   # 用'lxml'来进行解析
        # 这是原代码里面的内容，soup.title就是要读取的标题牛肉
        title = soup.title
        author = soup.find_all(class_="author-name")
        if author:
            author_name = re.findall(r'>(.*?)<', str(author))[0]
        else:
            author_name = '未知'

        # 调用爬取结构化数据的函数
        content_list = get_content(hupu_url_i)

        if content_list is not None:

            check_sql = """
                select * from {table} where origin_url like '%{url}%'
            """.format(table=Article_Meta_Data.__tablename__, url=hupu_url_i)
            exist_info = mysql.query(check_sql)

            if len(exist_info) == 0:
                meta_data = Article_Meta_Data(origin_url=hupu_url_i,
                                            title=content_list['title'],
                                            author=author_name,
                                            summary=content_list['summary'],
                                            keywords=content_list['keywords'],
                                            media=content_list['media'],
                                            content=content_list['content'],
                                            create_date=convert_date_from_datetime(content_list['time']),
                                            create_time=content_list['time']
                                    )
                session.begin()
                session.add(meta_data)
                session.commit()















































































































































































































































































































































































































































































        