#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
将论文中语义相似词的TFIDF值相加，并据此进行论文排序

author: zhuzi   version: 1.0    date: 2019/03/18
"""

import xlrd
import tfidf
import xlsxwriter

# 获取语义相似词
def get_simwords(filepath):

    # 读取Excel文件
    data = xlrd.open_workbook(filepath)
    # 读取文件中的第1个工作簿
    sheet = data.sheets()[0]
    # 获取行数
    numrows = sheet.nrows

    simwords_list = []
    for rowid in range(numrows):
        simwords_list.append(sheet.row_values(rowid)[0])

    return simwords_list

if __name__=='__main__':

    simwords_list = get_simwords('../data/similar_words.xlsx')
    (paperlist, feature2index, weight) = tfidf.calc('../data/raw.xlsx')
    # 存放特征词的列索引
    feaid = []
    for each in simwords_list:
        if each in feature2index:
            print(each)
            feaid.append(feature2index[each])

    # 以论文名为key，存储特征词的权重和
    paperwei_dict = {}
    for count in range(len(paperlist)):
        name = paperlist[count]
        paperwei_dict[name] = 0
        for colindex in feaid:
            paperwei_dict[name] += weight[count][colindex]

    # 创建一个Excel表
    book = xlsxwriter.Workbook('../data/paper_weight.xlsx')
    # 添加Sheet1
    sheet1 = book.add_worksheet('Sheet1')
    # 录入表头
    sheet1.write(0, 0, 'Title')
    sheet1.write(0, 1, 'Weight')

    i = 1   # 行号
    for k in paperwei_dict:
        sheet1.write(i, 0, k)
        sheet1.write(i, 1, paperwei_dict[k])
        i += 1

    book.close()
