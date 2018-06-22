#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/28 13:35
# @Author  : dongdong Zou
# @File    : recommend.py
# @license : Copyright(C), 安锋游戏
import time, sys
from libs.recommend_articles import init, get_similar_model

if __name__ == '__main__':
    start_time = int(time.time() * 1000)

    len_aritcles = 20  # 默认为10篇文章

    model = get_similar_model()

    args = sys.argv
    user_keywords = ["微信"]
    if len(args) > 1:
        user_keywords = str(sys.argv[1]).split(',')

    user_id_list = init(model, user_keywords,10)
    print(user_id_list)

    end_time = int(time.time() * 1000)
    diff_time = end_time - start_time
    print('耗时 %s 秒' % (diff_time / 1000))

