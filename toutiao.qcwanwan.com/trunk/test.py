#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/4 11:13
# @Author  : dongdong Zou
# @File    : test.py
# @license : Copyright(C), 安锋游戏
import requests
from bs4 import BeautifulSoup
import graphene

from common_utils.config import Config
from common_utils.database import mysql_client

if __name__ == '__main__':
    mysql = mysql_client(Config().get_config('mysql', 'host'),
                         Config().get_config('mysql', 'port'),
                         Config().get_config('mysql', 'database'),
                         Config().get_config('mysql', 'username'),
                         Config().get_config('mysql', 'password'))


    sql = "SELECT COUNT(*), origin_url , MIN(id) as id FROM af_articles " \
          "WHERE media = 2 GROUP BY origin_url HAVING COUNT(*) > 2"

    data_list = mysql.query(sql)
    for item in data_list:
        del_sql = "DELETE FROM af_articles " \
                  "WHERE origin_url LIKE '%{url}%' AND id > {id}".format(url=item['origin_url'], id=item['id'])
        mysql.execute(del_sql)


