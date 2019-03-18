#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
因为同一篇论文可能包含于多个概念节点中，所以需根据拟定的合并规则将其合并

author: zhuzi   version: 1.0    date: 2019/03/18
"""

import xlrd
import sv_and_av_calc as svav
import xlsxwriter

# 获取概念词结构图矩阵
def get_structure(filepath):

    # 读取Excel文件
    data = xlrd.open_workbook(filepath)
    # 读取文件中的第1个工作簿
    sheet = data.sheets()[0]
    # 获取行数
    numrows = sheet.nrows

    graph = []
    for rowid in range(numrows):
        graph.append(sheet.row_values(rowid))

    return graph

# 合并论文集为dict，名称为key，值为SV和AV
def papers():

    (paper2conid_dict, keywords) = svav.get_conpaper()
    graph = get_structure('../data/graph_structure.xlsx')
    # 存放最终论文信息
    final_paper = {}

    for name in paper2conid_dict:
        for i in range(len(paper2conid_dict[name])):
            # 获取概念词ID
            conid1 = paper2conid_dict[name][i]
            if i == 0:
                # 第一次出现的论文直接进行赋值
                final_paper[name] = keywords[conid1][name]
            for j in range(i+1, len(paper2conid_dict[name])):
                conid2 = paper2conid_dict[name][j]
                # 判断概念词之间是否有直接连接
                if graph[conid1][conid2] == 1:
                    final_paper[name][0] = max(final_paper[name][0], keywords[conid1][name][0]+keywords[conid2][name][0])
                    final_paper[name][1] = max(final_paper[name][1], keywords[conid1][name][1]+keywords[conid2][name][1])
                else:
                    final_paper[name][0] = max(final_paper[name][0], keywords[conid2][name][0])
                    final_paper[name][1] = max(final_paper[name][1], keywords[conid2][name][1])

    return final_paper

if __name__=='__main__':

    final_paper = papers()
    # 创建一个Excel表
    book = xlsxwriter.Workbook('../data/result.xlsx')
    # 添加Sheet1
    sheet1 = book.add_worksheet('Sheet1')
    # 录入表头
    sheet1.write(0, 0, 'Title')
    sheet1.write(0, 1, 'SV')
    sheet1.write(0, 2, 'AV')
    sheet1.write(0, 3, 'RV')

    i = 1   # 行号
    for k in final_paper:
        sheet1.write(i, 0, k)
        sheet1.write(i, 1, final_paper[k][0])
        sheet1.write(i, 2, final_paper[k][1])
        sheet1.write(i, 3, final_paper[k][0] * final_paper[k][1])
        i += 1

    book.close()
