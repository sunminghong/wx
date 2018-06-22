# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 17:19:50 2018

@author: Administrator
"""

#from gensim.models import word2vec
import gensim
import jieba
from jieba import analyse
import xlrd
import pandas as pd
import numpy as np
import math
from numpy import mat
from xlrd import xldate_as_tuple
import time

"""文章推荐后面添加事件追踪这个小功能块。
   原理：得到每一篇推荐文章后，就通过计算中文相似性，得到和它最相关的5篇文章（同时达到一定的阈值），
        即事件追踪的文章要和被显示的文章相似性大于一定的阈值，但上限为5篇文章。
   在哪里计算？
      由于它的计算量还是很大的，我们在哪一步进行计算呢。得到文章矩阵的那一步最好。文章的矩阵应该
      是列相加的，即一列80维的数值即构成了该文章的向量表示，即我们不设限媒体。同时事件是要严格按
      照时间顺序排列的。而这一步可以独立一个程序去跑，我们得到文章的摘要，文章链接，事件追踪文章
      的标题和链接，当用户点进了具体的一篇文章，这些计算的内容就会展示出来。
      
"""
#文件位置
# r'C:/Users/Administrator/Desktop/huxiu_4_6.xlsm'

def read_original_data(item):
    ExcelFile=xlrd.open_workbook(item)
    #获取目标EXCEL文件sheet名
    sheet=ExcelFile.sheet_by_index(0)
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

def format_str(content):
    #content = unicode(content,'utf-8')
    content_str = ''
    for i in content:
        if is_chinese(i):
            content_str = content_str+i
    return content_str

#构建去停用词
def stopwordslist(filepath):  
    stopwords = [line.strip() for line in open(filepath, 'r').readlines()]  
    return stopwords

def get_clear_articles(item):
    """ etl 文章的主要内容  """
    sheet = read_original_data(item)
    data_articles =  sheet.col_values(4)  # 这列数据为文章的主要内容。
    
    result_huxiu = []
    #先遍历文件名  
    for data_article in data_articles:  
        data_article = format_str(data_article) 
        data = jieba.cut(data_article)
        data = " ".join(data)
        result_huxiu.append(data)

    result_huxiu_0 = []
    for i in range(len(result_huxiu)):
    
        stopwords_filepath = "C:/Users/Administrator/Desktop/stopword_1.txt"
        stopwords = stopwordslist(stopwords_filepath)  # 这里加载停用词的路径      
    
        result_huxiu_i = result_huxiu[i].split(" ")
        result_huxiu_i_0 = str()
        #result_huxiu_i_1 = str()
        for j in range(len(result_huxiu_i)):
            result_huxiu_ij = ''
            if result_huxiu_i[j] not in stopwords:
                #result_huxiu_i[j] = " ".join(result_huxiu_i[j])
                result_huxiu_ij = str(result_huxiu_i[j]) + str(' ')
            result_huxiu_i_0 += result_huxiu_ij    
            
        result_huxiu_0.append(result_huxiu_ij+result_huxiu_i_0)                    

    return result_huxiu_0

def get_array_norm(list_0):

    a_sq = 0.0
 
    for a1 in list_0:        
        a_sq += a1**2

    norm = math.sqrt(a_sq)
    return norm

""" 1 """          
def get_article_array(item):    
    # 引入TF-IDF关键词抽取接口
    # 采用对每篇文章用关键字表示的方法，即一篇文章用一个向量表示，提高计算中文相似性的速度。
    #url_dict = {}
    # 对应的加载方式，模型文件可以保持到线上的一个文件里面。
    model = get_model("D:/jiaoben/huxiu_0.model2.bin")  # 删除 binary=True
    size = 80
    
    result_huxiu_0 = get_clear_articles(item)
    articels_shuzu = np.zeros((size,len(result_huxiu_0)))
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
                articels_shuzu[l][i] = float(list(article_i_array_0)[l])/(article_i_norm+0.00001)  
    return articels_shuzu

def get_article_url_df(item):
    """ 将文章向量和url合并为df输出为csv文件 """
    
    sheet = read_original_data(item)
    data_urls =  sheet.col_values(8)  # 8是表示sheet表中第8列是url的数据。    
    article_shuzu = get_article_array(item)
    
    articel_df = pd.DataFrame(article_shuzu)    
    articel_df.columns = [str(data_urls[i]) for i in range(article_shuzu.shape[1])] 
    # 输出的中间文件路径    
    return articel_df

###############################################################################
# ******下面是实现文章的事件追踪功能的模块                               
###############################################################################
    
def get_matrix_and_columns(article_path):
    """ 获取文章的向量矩阵和对应的索引，我这里还是用url作为索引
    params
    ------
    article_path: 文件路径，由此获取文章的文本内容和索引(这里是url)
    columns_list： 返回的索引(这里是url)
    articel_matrix： 多篇文章向量组成的矩阵，用来计算后面文章的相似性系数
    """
    
    articel_df = get_article_url_df(article_path)
    columns_list_0 = list(articel_df.columns)
    print(columns_list_0)
    del articel_df[columns_list_0[0]]  # 这里第一列数据没有用，所以删除
    columns_list = list(articel_df.columns)
    articel_matrix = mat(articel_df.values)
    return columns_list,articel_matrix

# 下面的几个数据计算耗时，后面多次用到，所以单独拿出来 
# columns_list_now: 待推荐文章的索引
# columns_list_former: 获取事件追踪文章池子的索引 
# now_articel_matrix: 待推荐文章池子的向量矩阵 
# former_articel_matrix: 事件追踪文章池子的向量矩阵      
columns_list_now,now_articel_matrix = get_matrix_and_columns(r'C:/Users/Administrator/Desktop/huxiu_4_6.xlsm')       
columns_list_former,former_articel_matrix = get_matrix_and_columns(r'C:/Users/Administrator/Desktop/huxiu_former.xlsm')

def get_most_related_articels(related_articels_num=5,yz_num=0.5):
    """ 获取被推荐的文章池子的这部分文章，它们每一篇文章对应的事件追踪文章的索引列表(这里是url)
    params
    ------
    former_and_now_sims: 矩阵形式,记录待推荐文章池子和事件追踪文章池子的相似性系数的矩阵,行数
        为时间追踪文章池子的文章数，列数为待推荐文章数。
    related_articels_num: 选取事件追踪的文章数，默认为5
    most_related_articels： 待推荐文章的索引和其对应与若干篇事件追踪文章相似性系数，我们选择了一定的
        阈值，即每篇文章和其事件追踪文章的相似性系数要大于0.5，上限默认为5篇。    
    """    
    # 计算文章的相似性系数的矩阵
    former_and_now_sims = (former_articel_matrix.T * now_articel_matrix).T  # T 表示矩阵的转置
    # 得到文章相似性的矩阵
    former_and_now_sims_shuzu = np.array(former_and_now_sims)
    # 获取相似性系数大于一定阈值的，且不超过n篇事件追踪的文章
    #related_articels_num = 5
    most_related_articels = []
    for i in range(former_and_now_sims_shuzu.shape[0]):
        list_sim_i = former_and_now_sims_shuzu[i]
        list_sim_i_dict = {}
        for j in range(len(list_sim_i)):
            list_sim_i_dict[j] = list_sim_i[j] 
        if len(list_sim_i_dict) >= related_articels_num:
            list_sim_i_dict_sorted = sorted(list_sim_i_dict.items(), key=lambda x: x[1], reverse=True)[:related_articels_num] # 选取最相似的5篇
            most_related_dict = {k: v for k, v in dict(list_sim_i_dict_sorted).items() if v > yz_num}
        else:  # 字典的长度小于设定的数值
            list_sim_i_dict_sorted = list_sim_i_dict 
            most_related_dict = {k: v for k, v in list_sim_i_dict_sorted.items() if v > yz_num}
    
        most_related_articels.append(most_related_dict)
    return most_related_articels

def get_related_articles_df():
    """ 获取每篇文章的事件追踪文章的索引(这里是url)
    params
    ------
    most_related_articels: 每篇文章和对应的事件追踪文章列表。
    df_related: DataFrame数据格式，列表名是待推荐文章的索引(这里是url)，每列只有一个数据，数据
        里面包含若干个字典。
    """
    # 获取事件追踪的文章的url和标题.
    most_related_articels = get_most_related_articels() 
    df_related = pd.DataFrame(columns=columns_list_now) 
    for i in range(len(columns_list_now)):
        dict_i = most_related_articels[i]
        url_list = list(dict_i.keys())
        former_url_list = []
        if url_list != []:
            for num in url_list:
                former_url_list.append(columns_list_former[num])
                    
        df_related[columns_list_now[i]] = [former_url_list]
    #df_related.to_csv('C:/Users/Administrator/Desktop/now_former_related.csv')
    return df_related        

def get_articles_time_list(item):
    """ 将文章的发表时间转化为时间戳的格式，方便对文章按时间进行先后排序
    params
    ------
    item: 事件追踪文章池子的路径
    sheet: 数据源，这里第二列是文章时间数据列。
    articles_time_list: 文章发表时间转化为时间戳格式的数据列表    
    """     
    # 对于一篇文章相应的事件追踪的文章要按时间顺序进行排列
    sheet = read_original_data(item)
    articles_time = sheet.col_values(1)[1:]  # (1)里面的 1 表示第2列是时间数据列
    articles_time_0 = []
    for dt in articles_time:
        if dt !='':
            articles_time_0.append(xldate_as_tuple(dt,0))
        else:    
            articles_time_0.append((2018, 1, 1, 0, 0, 0))                

    articles_time_list = []
    for i in range(len(articles_time)):
        y_num = articles_time_0[i][0]
        m_num = articles_time_0[i][1]
        d_num = articles_time_0[i][2]
        
        m_num = str(0)+str(m_num) if m_num<10 else m_num
        d_num = str(0)+str(d_num) if d_num<10 else d_num
        dt = str(y_num)+'-'+str(m_num)+'-'+str(d_num)
        
        timeArray = time.strptime(dt, "%Y-%m-%d")
        timestamp = time.mktime(timeArray)
        articles_time_list.append(timestamp)
    
    return articles_time_list     

def get_date(timestamp):
    """ 时间戳转化为时间，格式为"%Y-%m-%d" """
    time_local = time.localtime(timestamp)
    dt = time.strftime("%Y-%m-%d",time_local)    
    return dt

def get_date_of_articles(item):
    """ 列表里面的时间戳进行转化 """
    item_transform = {}
    for i in range(len(item)):
        dt = get_date(item[i][1])
        item_transform[item[i][0]] = dt
    return item_transform

def get_time_sorted_articles(item):
    """ 获取按时间先后的事件追踪文章的字典数据
    params
    ------
    item: 事件追踪文章池子的路径
    sheet: excel表格形式的数据源，这里第九列是url数据列。
    articles_url: 事件追踪文章池子的索引(这里是url)
    columns_list_now: 待推荐文章池子的索引(这里是url)
    former_url_time: 获取事件追踪文章池子，保存对应的索引和时间的列表
    url_date_dict: 字典，keys为索引(这里是url),values为对应的文章发表日期，用来对事件追踪文章    
        按时间排序。                  
    df_related_articles: DataFrame格式，每列数据列名为待推荐文章的索引(这里是url)，每列只有
        一个数据，数据里面是字典，keys为事件追踪文章的索引(这里是url)，values为对应的时间，方便
        展示，下面是一个实例  {'241012.0': '2018-04-20', '240709.0': '2018-04-19', 
        '240715.0': '2018-04-19', '240728.0': '2018-04-19', '240758.0': '2018-04-19'}
    """
    # 得到事件追踪文章池子的索引(这里是url)
    sheet = read_original_data(item)
    articles_url = sheet.col_values(8)[1:]   # 8 代表第9列数据是url数据列                   
    
    df_related = get_related_articles_df()
    
    articles_time_list = get_articles_time_list(item)                                                                    
    
    former_url_time = []
    df_related_articles = pd.DataFrame(columns=columns_list_now)
    for i in range(len(columns_list_now)):   
        former_url_list = list(df_related[columns_list_now[i]])
        url_date_dict = {}
        if former_url_list != []:
            for url in former_url_list[0]:
                for j in range(len(articles_time_list)):
                    if str(articles_url[j]) == url:  # 通过索引关联数据
                        url_date_dict[url] = int(articles_time_list[j])
            
            url_date_dict_sorted = sorted(url_date_dict.items(), key=lambda x: x[1], reverse=True) # , reverse=True        
            former_url_time.append(url_date_dict_sorted)
            url_date_dict_transform = get_date_of_articles(url_date_dict_sorted)
            df_related_articles[columns_list_now[i]] = [url_date_dict_transform]              
        else:
            former_url_time.append([])
            df_related_articles[columns_list_now[i]] = []

    return df_related_articles


if __name__=='__main__':
    """ 对原始数据做处理，得到包含每篇文章向量和url对应的数据，作为中间文件 """
    # 获取待推荐文章向量组成的矩阵
    articel_df = get_article_url_df(r'C:/Users/Administrator/Desktop/huxiu_4_6.xlsm')    
    # 得到事件追踪文章池子的路径    
    item = r'C:/Users/Administrator/Desktop/huxiu_former.xlsm'
    df_related_articles = get_time_sorted_articles(item)
    df_related_articles.to_csv('C:/Users/Administrator/Desktop/now_former_related_articles.csv')











  

































































































































































































                