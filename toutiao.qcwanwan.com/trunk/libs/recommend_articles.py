#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/28 17:49
# @Author  : dongdong Zou
# @File    : recommend_articles_new.py
# @license : Copyright(C), 安锋游戏
import gensim
import jieba
import numpy as np
import random
import pandas as pd
import time, math
from common_utils.common import get_path
from collections import Counter

size = 80


# 找出相似词语,对应的加载方式，模型文件可以保持到线上的一个文件里面。
def get_similar_model():
    jieba.load_userdict(get_path() + '/new_words.txt')
    filePath = get_path() + '/huxiu_0.model5.bin'

    # 删除 binary=True
    model = gensim.models.KeyedVectors.load_word2vec_format(filePath)

    return model


def get_df():
    """ 将中间文件转化为文章想和url对应的字典，keys值为url，对应的values为该文章的向量 """

    articel_url_df = pd.read_csv(get_path() + '/article__array_url.csv')

    return articel_url_df


def get_array_norm(list_0):
    a_sq = 0.0

    for a1 in list_0:
        a_sq += a1 ** 2

    norm = math.sqrt(a_sq)
    return norm


def get_user_array(model, item):
    # 将用户的兴趣标签词组，转化为一个向量
    array_item = np.zeros(size)
    for j in range(len(item)):
        array_i_word = np.zeros(size)
        try:
            array_i_word = model.wv[item[j]]
        except KeyError as e:
            continue
        array_item += array_i_word
    return array_item


def get_articles_sim(model, articel_url_df, item):
    # 由中文相似性计算得到的推荐文章和相关文章的权重。

    columns_list = list(articel_url_df.columns)
    del articel_url_df[columns_list[0]]
    del articel_url_df[columns_list[1]]

    columns_list_new = list(articel_url_df.columns)

    articel_matrix = articel_url_df.values
    array_item = get_user_array(model, item)

    array_item_norm = get_array_norm(list(array_item))
    sim_artices_user = np.dot(array_item, articel_matrix)

    keywords_articles_sim = {}
    for i in range(articel_matrix.shape[1]):
        # 用户的关键字可以参与相似度计算的词
        sim_i = sim_artices_user[i] / ((array_item_norm + 0.0001))

        keywords_articles_sim[columns_list_new[i]] = sim_i  # key值是该文章向量，value是相似系数
    # if keywords_articles_sim:
    #     sim_sorted = sorted(keywords_articles_sim.items(), key=lambda x: x[1], reverse=True)
    #     sim_n = sim_sorted[:len_aritcles]
    # else:
    #     sim_n = []
    return keywords_articles_sim


def random_weight(weight_data):
    _total = sum(weight_data.values())  # 权重求和
    _random = random.uniform(0, _total)  # 在0与权重和之前获取一个随机数
    _curr_sum = 0
    _ret = None
    _keys = weight_data.keys()
    for _k in _keys:
        _curr_sum += weight_data[_k]  # 在遍历中，累加当前权重值
        if _random <= _curr_sum:  # 当随机数<=当前权重和时，返回权重key
            _ret = _k
            break
    return _ret


def get_article_merge(item):
    # 由权重系数随机抽取被推荐的文章。
    articles_list_merge = []
    for i in range(100):
        article_i = random_weight(item)
        if article_i not in articles_list_merge:
            articles_list_merge.append(article_i)
    return articles_list_merge


def main(model, user_keywords, len_aritcles):
    sim_csv = get_df()
    len_words = min(3, len(user_keywords))
    user_0_keywords = random.sample(user_keywords, len_words)
    # 通过词组得到的推荐
    sim_user = get_articles_sim(model, sim_csv, user_0_keywords)

    # 通过第一个词得到的推荐
    for i in range(len(user_0_keywords)):
        list_i = [user_0_keywords[i]]
        sim_10_i = get_articles_sim(model, sim_csv, list_i)
        sim_user = dict(Counter(sim_10_i) + Counter(sim_user))

    sim_user_sorted = sorted(sim_user.items(), key=lambda x: x[1], reverse=True)
    sim_user_n = sim_user_sorted[:len_aritcles]

    sim_user_dict = {}
    for i in range(len(sim_user_n)):
        sim_user_dict[sim_user_n[i][0]] = sim_user_n[i][1]

    return user_0_keywords, sim_user_dict


def get_keywords_jieba(user_keywords):
    keywords_jieba_list = []
    for keywords in user_keywords:
        keywords_jieba = jieba.cut(str(keywords))
        keywords_jieba_1 = ",".join(keywords_jieba)
        keywords_jieba_2 = keywords_jieba_1.split(",")
        for i in range(len(keywords_jieba_2)):
            keywords_jieba_list.append(keywords_jieba_2[i])

    return keywords_jieba_list


# 启动
def init(model, keywords=None, len_aritcles=30):

    begin_time = int(time.time() * 1000)
    keywords = get_keywords_jieba(keywords)
    user_0_keywords, sim_user_dict = main(model, keywords, len_aritcles)
    user_id_list = list(sim_user_dict.keys())

    end_time = int(time.time() * 1000)
    diff_time = end_time - begin_time
    print('总时长: %s毫秒' % (diff_time))

    return user_id_list