#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
根据关键词匹配论文集并计算每篇论文的SV与AV值（不经比较，即最初的SV与AV）

author: zhuzi   version: 1.0    date: 2019/03/17
"""

import xlrd
import tfidf
import numpy

# 获取概念词及其相关属性
def get_concept(filepath):

    # 读取Excel文件
    data = xlrd.open_workbook(filepath)
    # 读取文件中的第1个工作簿
    sheet = data.sheets()[0]
    # 获取行数
    numrows = sheet.nrows

    concept = []
    for rowid in range(1, numrows): # 不读取表头
        concept.append(sheet.row_values(rowid))

    return concept

# 获取论文相关信息，返回以论文名为key的字典
def get_paperinfo(filepath):

    # 读取Excel文件
    data = xlrd.open_workbook(filepath)
    # 读取文件中的工作簿
    sheet = data.sheets()[0]
    # 获取行数
    numrows = sheet.nrows
    
    paper_dict = {}
    for rowid in range(1, numrows):    # 忽略表头
        row = sheet.row_values(rowid)
        # 分别存放论文类型、Q值
        paper_dict[row[0]] = [row[1], row[6]]

    return paper_dict

# 1.返回论文及其所属的概念词ID；2.返回概念词list，元素为以论文名为key的论文集dict，值为概论文的SV与AV
def get_conpaper():

    (paperlist, feature2index, weight) = tfidf.calc('../data/raw.xlsx')
    concept = get_concept('../data/concept_attributions.xlsx')
    # 存放用户对节点的认知能力
    ua_list = []
    for each in (range(len(concept))):
        ua_list.append(concept[each][1])
    # 取得用户认知能力的Q1和Q3值
    (q1, q3) = numpy.percentile(ua_list, [25, 75])
    paper_dict = get_paperinfo('../data/paper_information.xlsx')
    # 以论文名称为key存放包含该论文的关键词ID
    paper2conid_dict = {}
    # 存放每个关键词的论文集合
    keywords = []

    for con_id in range(len(concept)):
        # 为每个概念词构造一个字典用来存放论文集
        keywords.append({})
        try:
            # 根据概念词获取列索引
            col = feature2index[concept[con_id][0]]
            for paper_id in range(len(weight)):
                # 易知，TFIDF值不为0就代表该词在文档中出现过
                if weight[paper_id][col] != 0:
                    # sv = weight*CW*Interest
                    sv = weight[paper_id][col]*concept[con_id][2]*concept[con_id][3]
                    ua = concept[con_id][1]
                    paper_name = paperlist[paper_id]
                    # 1表示研究型论文，0表示综述
                    paper_type = paper_dict[paper_name][0]
                    # 匹配G(p, c)
                    if ua<=q1 and paper_type==1:
                        g = 0.1
                    elif ua<= q1 and paper_type==0:
                        g = 0.9
                    elif ua>=q3 and paper_type==1:
                        g = 0.9
                    elif ua>=q3 and paper_type==0:
                        g = 0.1
                    else:
                        g = 0.5
                    # av = Q*G(p, c)
                    av = paper_dict[paper_name][1] * g
                    # 列表内存放字典，字典的key为论文名，值为包含SV与AV的list
                    keywords[con_id][paper_name] = [sv, av]
                    # 记录该论文所属的关键词ID
                    try:
                        paper2conid_dict[paper_name].append(con_id)
                    except KeyError:
                        paper2conid_dict[paper_name] = [con_id]
        except KeyError as k:
            print('KeyError:', k)

    return (paper2conid_dict, keywords)
            
if __name__=='__main__':

    (paper2conid_dict, keywords) = get_conpaper()
    print(paper2conid_dict)
    print(keywords)
