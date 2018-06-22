#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 9:47
# @Author  : dongdong Zou
# @File    : test.py.py
# @license : Copyright(C), 安锋游戏

import requests
from bs4 import BeautifulSoup
from common_utils.common import convert_date_from_datetime
from common_utils.config import Config
from common_utils.database import mysql_client
from libs.MetaModel import Article_Meta_Data

headers = {'User-agent': 'Mozilla/5.0'}  # 模仿登录的设备user-Agent
media_content = 2  #雷锋网
start_url = "https://www.leiphone.com/news/201804/eqPWoX8XgM5x611d.html?uniqueCode=Us3eYIepc90lJKnE"


def get_content(url):
    # url = "https://www.leiphone.com/news/201804/" + str(unique_id) + ".html"
    # 做两手准备，可以读取或读取失败
    try:
        page = requests.get(url, headers=headers, timeout=5)

    except:
        return 'False', ''

    content = page.text  # 源码的内容
    soup = BeautifulSoup(content, 'lxml')  # 用'lxml'来进行解析

    # 提取时间
    if soup.find(attrs={"class": "time"}):
        url_time = soup.find(attrs={"class": "time"})
        time_content = str(url_time.text).strip()
    else:
        time_content = 0

    # 提取文章里面的标题，简要等内容
    url_content = soup.find(attrs={"class": "lphArticle-detail"})
    if url_content:

        article_seo_title = url_content["data-article_seo_title"].split("|")[0]
        article_seo_keywords = url_content["data-article_seo_keywords"]
        article_seo_description = url_content["data-article_seo_description"]
        author_name = url_content["data-author_name"]

        main_content_0 = soup.find_all(class_="lph-article-comView")
        main_content_0 = BeautifulSoup(str(main_content_0), 'lxml')
        tips = main_content_0.find_all("p")

        main_content = ""
        for tip in tips:
            if "br/" not in str(tip):
                if tip != []:  # 防止得到的tip为空
                    main_content += str(tip)

        content_list = {'title': article_seo_title, 'author': author_name, 'media': media_content,
                        'keywords': article_seo_keywords, 'summary': article_seo_description,
                        'content': main_content, 'time': time_content}

    return content_list

""" 
    获取每个页面包含文章标题列表的内容 
"""
def get_acticle_list_store(url):

    page = requests.get(url, headers=headers, timeout=5)
    content = page.text
    soup = BeautifulSoup(content, 'lxml')
    bodys = soup.find_all(class_="word")
    return bodys


if __name__ == '__main__':

    mysql = mysql_client(Config().get_config('mysql', 'host'),
                         Config().get_config('mysql', 'port'),
                         Config().get_config('mysql', 'database'),
                         Config().get_config('mysql', 'username'),
                         Config().get_config('mysql', 'password'))

    session = mysql.get_session()

    page_num = 5
    for i in range(1, page_num):
        url = "https://www.leiphone.com/page/" + str(i)
        print(url)
        bodys = get_acticle_list_store(url)

        for j in range(len(bodys)):
            body = BeautifulSoup(str(bodys[j]), 'lxml')
            tip = body.find(attrs={"class": "headTit"})
            url_i = tip["href"]

            try:
                page = requests.get(url_i, headers=headers, timeout=15)
            except:
                continue
            content = page.text  # 源码的内容
            soup = BeautifulSoup(content, 'lxml')  # 用'lxml'来进行解析
            if soup.find(attrs={"class": "lphArticle-detail"}):
                content_list = get_content(url_i)

                check_sql = """
                      select * from {table} where origin_url like '%{url}%'
                  """.format(table=Article_Meta_Data.__tablename__, url=url_i)

                exist_info = mysql.query(check_sql)
                if len(exist_info) == 0:
                    meta_data = Article_Meta_Data(origin_url=url_i,
                                                  title=content_list['title'],
                                                  author=content_list['author'],
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









































































































































































































































































































































































































































































        