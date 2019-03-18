#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
构建给定文本的向量空间模型，计算各词的TFIDF值。

author: zhuzi   version: 1.0    date: 2019/03/16
"""

import xlrd
import jieba
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import re

# 预编译百分数判断正则表达式
re_percent = re.compile(r'^(\d+|\d+\.\d+)%$')

# 判断字符串是否为非数字，是返回True，否则返回False
def not_numbers(s):
    
    try:
        float(s)
        return False
    except ValueError:
        pass

    # 判断百分数字符串
    if re_percent.match(s):
        return False

    return True

# 计算TF-IDF，返回论文列表、特征词的列索引字典和TF-IDF矩阵
def calc(filepath):

    # 读取Excel文件
    data = xlrd.open_workbook(filepath)
    # 读取文件中的第1个工作簿
    sheet = data.sheets()[0]
    # 获取行数
    numrows = sheet.nrows
    # 加载自定义分词词典
    jieba.load_userdict('../dicts/custom.txt')
    # 加载停用词
    stopwords = [line.strip() for line in open('../dicts/哈工大停用词表.txt', 'r').readlines()]
    # 存放分词、去停用词后的最终待计算数据
    corpus = []
    # 存储论文名
    paperlist = []

    for rowid in range(numrows):
        # 根据行号获取整行内容
        row = sheet.row_values(rowid)
        paperlist.append(row[0])
        # 将title, keywords和summary拼接为一个文档
        text = row[0] + ';' + row[4] + ';' + row[5]
        # 调用jieba分词，采用精确模式
        seg_list = jieba.cut(text, cut_all = False)
        record = []
        # 去停用词
        for word in seg_list:
            if not_numbers(word) and (word not in stopwords): # 过滤数字并去停用词
                record.append(word)
        # 词之间以空格间隔
        corpus.append(' '.join(record))

    vectorizer = CountVectorizer()
    # 统计单词出现频数
    X = vectorizer.fit_transform(corpus)
    # 存储从feature名称到column index（列索引）的逆映射
    feature2index = {}
    # 遍历词袋模型中的特征词
    for feature in vectorizer.get_feature_names():
        feature2index[feature] = vectorizer.vocabulary_.get(feature)    # 逆映射存储在vocabulary_属性中
    transformer = TfidfTransformer()
    # 计算TF-IDF值
    tfidf = transformer.fit_transform(X)

    # 返回论文列表、列索引和TF-IDF矩阵
    return (paperlist, feature2index, tfidf.toarray())

if __name__=='__main__':

    (paperlist, feature2index, weight) = calc('../data/raw.xlsx')
    print(paperlist)
    print(feature2index)
    print(weight)
