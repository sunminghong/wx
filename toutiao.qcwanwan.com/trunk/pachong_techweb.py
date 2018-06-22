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

start_url = "http://www.techweb.com.cn"
headers = {'User-agent': 'Mozilla/5.0'}
media = 4 # 'TechWeb'


def get_data_list():
    page = requests.get(start_url, headers=headers, timeout=5)
    content = page.text   # 源码的内容
    soup = BeautifulSoup(content, 'lxml')   # 用'lxml'来进行解析

    data_urls = []
    data_list = soup.find_all(href=re.compile(r'com.cn/(.*)?/(\d+).shtml'))
    for item in data_list:
        data_urls.append(item['href'])

    return data_urls

    
def get_content(url):
    try:
        page = requests.get(url,headers=headers,timeout=5)
    
    except:
        return None
    content = page.content
    try: 
        content = str(content, 'utf-8')
    except:
        pass
    soup = BeautifulSoup(content,'lxml')   # 用'lxml'来进行解析
   
    # 提取时间
    if soup.find(attrs={"class": "time"}):
        url_time = soup.find(attrs={"class": "time"})
        time_content = str(url_time.text).strip()
    else:
        time_content = '1970.01.01 08:00:00'
           
    url_content = soup.head

    title_content = url_content.title.text
    
    if url_content.find(attrs={"name":"keywords"}): 
        article_keywords_content = url_content.find(attrs={"name":"keywords"})["content"]
        article_keywords = article_keywords_content
    else:
        article_keywords = ""
        
    if url_content.find(attrs={"name":"description"}):
        article_description_content = url_content.find(attrs={"name":"description"})["content"]
        article_description = article_description_content
    else:
        article_description = ""
    
    if soup.find(attrs={"class":"author"}): 
        author_content = soup.find(attrs={"class":"author"})
        author_name = str(author_content.text).replace('作者:', '')
    else:
        author_name = ""

    main_content_1 = soup.find(attrs={"id":"content"}) 
    main_content_0 = BeautifulSoup(str(main_content_1), 'lxml')
    tips = main_content_0.find_all("p")
    main_content=""
    for tip in tips:
        if "br/" not in str(tip):
            if tip != []:    # 防止得到的tip为空            
                main_content += str(tip)

    content_list = {'title': str(title_content).replace('_TechWeb', ''), 'author': author_name, 'media': media,
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

                c_time = str(content_list['time']).replace('.', '-')
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















































































































































































































































































































































































































































































        