#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/3 9:58
# @Author  : dongdong Zou
# @File    : etl_data1.py
# @license : Copyright(C), 安锋游戏
# 这是得到分词后，整理好的文章主要内容，
# 这个程序耗时，不用在线跑
import jieba
import xlrd,os, math
import gensim
from jieba import analyse
import numpy as np
import pandas as pd
from common_utils.common import get_recent_month, get_path
from common_utils.config import Config
from common_utils.database import mysql_client


def read_original_data(item):
    ExcelFile = xlrd.open_workbook(item)
    # 获取目标EXCEL文件sheet名
    sheet = ExcelFile.sheet_by_index(0)
    # 抽取文章摘要内容的数据
    return sheet


def get_model(item):
    model = gensim.models.KeyedVectors.load_word2vec_format(item)
    return model


def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False


def is_number(uchar):
    """判断一个unicode是否是数字"""
    if uchar >= u'\u0030' and uchar <= u'\u0039':
        return True
    else:
        return False


def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (uchar >= u'\u0041' and uchar <= u'\u005a') or (uchar >= u'\u0061' and uchar <= u'\u007a'):
        return True
    else:
        return False


def get_array_norm(list_0):
    a_sq = 0.0

    for a1 in list_0:
        a_sq += a1 ** 2

    norm = math.sqrt(a_sq)
    return norm

def format_str(content):
    content_str = ''
    for i in content:
        if is_chinese(i):
            content_str = content_str + i
    return content_str


# 构建去停用词
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding="utf-8").readlines()]
    return stopwords


def get_clear_articles(item):
    """ etl 文章的主要内容  """
    result_huxiu = []
    for it in item:
        data_article = format_str(it['content'])
        data = jieba.cut(data_article)
        data = " ".join(data)
        result_huxiu.append(data)

    result_huxiu_0 = []
    for i in range(len(result_huxiu)):

        stopwords_filepath = get_path() + "/stopword_1.txt"
        stopwords = stopwordslist(stopwords_filepath)  # 这里加载停用词的路径

        result_huxiu_i = result_huxiu[i].split(" ")
        result_huxiu_i_0 = str()
        for j in range(len(result_huxiu_i)):
            result_huxiu_ij = ''
            if result_huxiu_i[j] not in stopwords:
                result_huxiu_ij = str(result_huxiu_i[j]) + str(' ')
            result_huxiu_i_0 += result_huxiu_ij

        result_huxiu_0.append(result_huxiu_ij + result_huxiu_i_0)

    return result_huxiu_0


def get_article_array(item):
    # 引入TF-IDF关键词抽取接口
    # 采用对每篇文章用关键字表示的方法，即一篇文章用一个向量表示，提高计算中文相似性的速度。
    # url_dict = {}
    # 对应的加载方式，模型文件可以保持到线上的一个文件里面。

    model = get_model(get_path() + "/huxiu_0.model5.bin")  # 删除 binary=True
    size = 80

    result_huxiu_0 = get_clear_articles(item)
    articels_shuzu = np.zeros((size, len(result_huxiu_0)))
    tfidf = analyse.extract_tags
    for i in range(len(result_huxiu_0)):
        keyword = tfidf(str(result_huxiu_0[i]))
        article_i_array_0 = np.zeros(size)
        if len(keyword) == 20:
            for j in range(20):
                try:
                    article_i_array = model.wv[keyword[j]]
                except KeyError as e:
                    article_i_array = np.zeros(size)
                article_i_array_0 += article_i_array

            article_i_norm = get_array_norm(article_i_array_0)

            for l in range(size):
                articels_shuzu[l][i] = float(list(article_i_array_0)[l]) / article_i_norm
    return articels_shuzu


def get_articel_url_mysql(data_list):
    """ 将文章向量和url合并为df输出为csv文件 """

    data_ids = []  # 7 是表示sheet表中第7列是url的数据。

    for item in data_list:
        data_ids.append(item['id'])

    article_shuzu = get_article_array(data_list)

    articel_df = pd.DataFrame(article_shuzu)
    articel_df.columns = [str(data_ids[i]) for i in range(article_shuzu.shape[1])]
    # 输出的中间文件路径
    articel_df.to_csv(get_path() + '/article__array_url.csv')
    return articel_df


def get_data_list(mysql, where, select='*'):

    _where = 'where 1=1 %s' % where

    sql = "select %s from af_articles %s order by create_date desc" % (select, _where)
    res = mysql.query(sql)
    return res


if __name__ == '__main__':
    """ 对原始数据做处理，得到包含每篇文章向量和url对应的数据，作为中间文件 """
    mysql = mysql_client(Config().get_config('mysql', 'host'),
                         Config().get_config('mysql', 'port'),
                         Config().get_config('mysql', 'database'),
                         Config().get_config('mysql', 'username'),
                         Config().get_config('mysql', 'password'))

    t = get_recent_month()
    data_list = get_data_list(mysql, ' and create_date between %s and %s ' % (t['s_t'], t['e_t']), '*')
    articel_df = get_articel_url_mysql(data_list)