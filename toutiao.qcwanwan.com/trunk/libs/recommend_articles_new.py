# -*- coding: utf-8 -*-
"""
Created on Wed May  2 16:18:32 2018

@author: h2
"""

import gensim
import numpy as np
import math
import random, os
import pandas as pd


def get_dict(item):
    """ 将中间文件转化为文章想和url对应的字典，keys值为url，对应的values为该文章的向量 """

    articel_url_df = pd.read_csv(os.getcwd() + '/article__array_url.csv')
    article__array_url_dict = {}
    article_url_df = pd.read_csv(item)

    url_list = list(article_url_df["id"])

    for i in range(len(article_url_df)):
        article_array_list = []
        for j in range(articel_url_df.shape[1] - 2):
            article_array_list.append(articel_url_df.iloc[i][j + 1])

        article__array_url_dict[url_list[i]] = article_array_list

    return article__array_url_dict


def cos_dist(a, b):
    if len(a) != len(b):
        return None
    part_up = 0.0
    a_sq = 0.0
    b_sq = 0.0
    for a1, b1 in zip(a, b):
        part_up += a1 * b1
        a_sq += a1 ** 2
        b_sq += b1 ** 2
    part_down = math.sqrt(a_sq * b_sq)
    if part_down == 0.0:
        return 0
    else:
        return part_up / part_down


def get_model(item):
    model = gensim.models.KeyedVectors.load_word2vec_format(item)
    return model


def get_user_array(item):
    # 将用户的兴趣标签词组，转化为一个向量
    model = get_model(os.getcwd() + "/huxiu_0.model5.bin")  # 删除 binary=True
    size = 80
    array_item = np.zeros(size)
    for j in range(len(item)):
        array_i_word = np.zeros(size)
        try:
            array_i_word = model.wv[item[j]]
        except KeyError as e:
            continue
        array_item += array_i_word
    return array_item


def get_articles_sim(item, len_aritcles):
    # 由中文相似性计算得到的推荐文章和相关文章的权重。
    article_array_url_dict = get_dict(os.getcwd() + '/article__array_url.csv')
    article_array_list = list(article_array_url_dict.values())
    article_url_list = list(article_array_url_dict.keys())
    array_item = get_user_array(item)
    keywords_articles_sim = {}
    for i in range(len(article_array_list)):
        # 用户的关键字可以参与相似度计算的词
        article_i_array = article_array_list[i]
        sim_i = cos_dist(article_i_array, array_item)
        keywords_articles_sim[str(article_url_list[i])] = sim_i  # key值是该文章向量，value是相似系数
    if keywords_articles_sim:
        sim_sorted = sorted(keywords_articles_sim.items(), key=lambda x: x[1], reverse=True)
        sim_n = sim_sorted[:len_aritcles]
    else:
        sim_n = []
    return sim_n


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


def main(user_keywords, len_aritcles):
    len_words = min(3, len(user_keywords))
    user_0_keywords = random.sample(user_keywords, len_words)
    # 通过词组得到的推荐
    sim_user = get_articles_sim(user_0_keywords, len_aritcles)
    # 通过第一个词得到的推荐
    for i in range(len(user_0_keywords)):
        list_i = [user_0_keywords[i]]
        sim_10_i = get_articles_sim(list_i, len_aritcles)
        sim_user += sim_10_i

    sim_user.sort(key=lambda x: (x[1], x[0]), reverse=True)

    sim_user_dict = {}
    for i in range(len(sim_user)):
        sim_user_dict[sim_user[i][0]] = sim_user[i][1]

    return user_0_keywords, sim_user_dict


if __name__ == '__main__':
    # user_keywords = ["腾讯","美国","共享","互联网","比特币"]
    user_keywords = ["微信"]
    len_aritcles = 20  # 默认为10篇文章
    user_0_keywords, sim_user_dict = main(user_keywords, len_aritcles)
    user_url_list = list(sim_user_dict.keys())
    print(user_url_list)