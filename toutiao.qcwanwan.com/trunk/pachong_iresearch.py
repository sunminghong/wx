#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/28 9:47
# @Author  : dongdong Zou
# @File    : test.py.py
# @license : Copyright(C), 安锋游戏
import requests
from bs4 import BeautifulSoup
import re

from common_utils.common import convert_date_from_datetime, string2timestamp, timestamp2string
from common_utils.config import Config
from common_utils.database import mysql_client
from libs.MetaModel import Article_Meta_Data

start_url = "http://www.iresearch.cn"
headers = {'User-agent': 'Mozilla/5.0'}
media = 5 # "艾瑞网"


def get_data_list():
    page = requests.get(start_url, headers=headers, timeout=5)
    content = page.content   # 源码的内容
    soup = BeautifulSoup(content, 'lxml')   # 用'lxml'来进行解析

    data_urls = []
    data_list_1 = soup.find_all(href=re.compile(r'content/(.*)?/(\d+).shtml'))
    data_list_2 = soup.find_all(href=re.compile(r'cn/b/(.*)?/(\d+).shtml'))
    
    for item in data_list_1:
        data_urls.append(item['href'])
    for item in data_list_2:
        data_urls.append(item['href'])    

    return data_urls


def get_clear_author_name(item):
    str_item = str(item)
    clear_item = str_item.replace("\xa0", " ")
    author_name = "佚名"
    if 'class="name"' in clear_item:
        pattern_1 = re.compile(r'class="name">(.*?)<')
        author_name = pattern_1.findall(clear_item)[0]
    elif '作者' in clear_item:
        pattern_2 = re.compile(r'作者：(.*?)</span>')
        print(pattern_2.findall(clear_item))
        if pattern_2.findall(clear_item) != [] and pattern_2.findall(clear_item) != ['']:
            author_name = pattern_2.findall(clear_item)[0]

    return author_name


def get_content(url):
    try:
        page = requests.get(url, headers=headers, timeout=5)
    except:
        return None
    content = page.content
    try: 
        content = str(content, 'utf-8')
    except:
        pass
    soup = BeautifulSoup(content, 'lxml')   # 用'lxml'来进行解析

    author_name = "佚名"
    if soup.find(attrs={"class": "origin"}):
        author_content = soup.find(attrs={"class": "origin"})
        author_name = get_clear_author_name(author_content)

    # 提取时间
    time_content = '1970/01/01 08:00:00'
    if soup.find(attrs={"class": "origin"}):
        url_time = soup.find(attrs={"class": "origin"})
        if url_time.em:
            if url_time.em.text:
                time_content = url_time.em.text
            else:
                time_content = '1970/01/01 08:00:00'
        else:
            pattern = re.compile(r'(\d{4}/\d{0,2}/\d{0,2} \d{0,2}:\d{0,2}:\d{0,2})')
            time_content = pattern.findall(str(url_time))[0]

    url_content = soup.head

    title_content = ""
    if url_content.title:
        if url_content.title.text:          
            title_content = url_content.title.text
    
    article_keywords = ""
    if url_content.find(attrs={"name": "keywords"}):
        article_keywords_content = url_content.find(attrs={"name":"keywords"})["content"]
        article_keywords = article_keywords_content
    
    article_description = "" 
    if url_content.find(attrs={"name": "description"}):
        article_description_content = url_content.find(attrs={"name":"description"})["content"]
        article_description = article_description_content
            
    main_content_1 = soup.find(attrs={"class": "m-article"})
    main_content_0 = BeautifulSoup(str(main_content_1), 'lxml')
    tips = main_content_0.find_all("p")

    main_content = ""

    for tip in tips:
        if "br/" not in str(tip):
            if tip != []:    # 防止得到的tip为空            
                main_content += str(tip)

    content_list = {'title': title_content, 'author': author_name, 'media': media,
                    'keywords': article_keywords, 'summary': article_description,
                    'content': main_content, 'time': time_content}
    return content_list


if __name__ == '__main__':

    mysql = mysql_client(Config().get_config('mysql', 'host'),
                         Config().get_config('mysql', 'port'),
                         Config().get_config('mysql', 'database'),
                         Config().get_config('mysql', 'username'),
                         Config().get_config('mysql', 'password'))

    session = mysql.get_session()

    data_urls = get_data_list()
    data_urls_clear = set(data_urls)
    for url in data_urls_clear:
        content_list = get_content(url)
        print(url)
        if content_list is not None:

            check_sql = """
                select * from {table} where origin_url like '%{url}%'
            """.format(table=Article_Meta_Data.__tablename__, url=url)

            exist_info = mysql.query(check_sql)
            if len(exist_info) == 0:

                c_time = str(content_list['time']).replace('/', '-')
                dt = string2timestamp(c_time)

                meta_data = Article_Meta_Data(origin_url=url,
                                              title=content_list['title'],
                                              author=content_list['author'],
                                              summary=content_list['summary'],
                                              keywords=content_list['keywords'],
                                              media=content_list['media'],
                                              content=content_list['content'],
                                              create_date=timestamp2string(dt, '%Y%m%d'),
                                              create_time=c_time
                                              )
                session.begin()
                session.add(meta_data)
                session.commit()







































































































































































































































































































































































































































        