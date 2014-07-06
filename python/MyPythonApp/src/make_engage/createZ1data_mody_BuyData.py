
# coding: utf8
#'''
#Created on 2013/02/22
#
#@author: n_shimada
#'''
from __future__ import with_statement
import sqlite3
import os

inpt=[]
result=[]
result_span = []
cnt_buy = []
cnt_lp = 0
flg_date = 0
flg_sec = 0

inpt_filename = 'C:/Users/n_shimada/Desktop/Galster_CRM_pymData.csv'
    
with open(inpt_filename, 'r') as f:
    for line in f:
        if flg_date==0: 
            flg_date+=1
            continue
        inpt = line.strip().split(',')[1:]
        result.append(inpt)

        fvisit_flag = 0
        flg_sec = 0

        cnt = 0
        cnt_buy.append(0)
        result_span.append( float(0) )       
        for d in xrange(len(inpt)):
            d_sub_1 = d-1
            if fvisit_flag == 0:
                if int(inpt[d]) > 0:
                    fvisit_flag=1
                    result[cnt_lp][d] = 0
                    old_data = int(inpt[d])
                    cnt_buy[cnt_lp]
                elif int(inpt[d]) == 0:
                    result[cnt_lp][d] = 999
            elif fvisit_flag == 1:
                if old_data > 0:
                    flg_sec = 1
                    result_span[cnt_lp] += cnt
                    cnt = 1
                    old_data = int(inpt[d])
                    cnt_buy[cnt_lp] += 1
                else:
                    cnt += 1
                    old_data = int(inpt[d])     
                result[cnt_lp][d] = cnt
        if flg_sec == 1:
            result_span[cnt_lp] = str(result_span[cnt_lp]/cnt_buy[cnt_lp])
        elif flg_sec == 0 and fvisit_flag == 1: result_span[cnt_lp] = str(cnt)
        elif fvisit_flag == 0: result_span[cnt_lp] = '999'
        cnt_lp+=1
#
print("count done")
#
with open('C:/Users/n_shimada/Desktop/Galster_CRM_payment_date.csv','w') as outfp:
    for r in result:
        outfp.write((",".join(map(str,r)))+"\n")

with open('C:/Users/n_shimada/Desktop/Galster_CRM_payment_date_AveSpan.csv','w') as outfp:
    for r in result_span:
        outfp.write(r+"\n")      
#
print("that's all")