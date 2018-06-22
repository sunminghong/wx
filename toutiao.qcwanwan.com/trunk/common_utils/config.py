# _*_ coding: utf-8 _*_
# @Time    : 2017/11/2 上午11:37
# @Author  : 杨楚杰
# @File    : config.py.py
# @license : Copyright(C), 安锋游戏
import configparser
import os


class Config:

    @staticmethod
    def get_config(section, key, conf='database'):
        config = configparser.ConfigParser()
        file_root = os.path.dirname(__file__)
        path = os.path.join(file_root, '../conf/' + conf + '.conf')
        config.read(path)
        return config.get(section, key)

    @staticmethod
    def set_config(section, key, value, conf='source'):
        config = configparser.ConfigParser()
        file_root = os.path.dirname(__file__)
        path = os.path.join(file_root, '../conf/' + conf + '.conf')
        config.read(path)
        config.set(section, key, str(value))
        fh = open(path, 'w')
        config.write(fh)  # 把要修改的节点的内容写到文件中
        fh.close()
