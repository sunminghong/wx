#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/5/4 10:12
# @Author  : dongdong Zou
# @File    : MetaModel.py
# @license : Copyright(C), 安锋游戏
from sqlalchemy import Column, String,Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
table_name = 'af_articles'


class Article_Meta_Data(Base):

    __tablename__ = table_name
    id = Column(Integer, primary_key=True, autoincrement=True)
    origin_url = Column(String, primary_key=True)
    title = Column(String)
    author = Column(String)
    summary = Column(String)
    keywords = Column(String)
    media = Column(String)
    content = Column(String)
    create_date = Column(Integer)
    create_time = Column(String)

    def __repr__(self):
        return '<af_articles %s - %s>' % (self.id, self.origin_url)
