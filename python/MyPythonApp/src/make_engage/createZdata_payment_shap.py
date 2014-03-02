# coding: utf8
#'''
#Created on 2013/02/22
#
#@author: n_shimada
#'''
from __future__ import with_statement
import sqlite3
import os
import csv

inpt=[]
result=[]
cnt_lp = 0
flg_date = 0

inpt_Z1_filename = 'C:/Users/n_shimada/Desktop/Galster_CRM.csv'
inpt_payment_filename = 'C:/Users/n_shimada/Desktop/Galster_CRM_pymData.csv'

Z_usrs = []
pym_datas = []
with open(inpt_Z1_filename, 'r') as f:
    reader = csv.reader(f)
    for line in reader:
        if flg_date==0: 
            flg_date+=1
            continue
        Z_usrs.append(line[0])
    
flg_date = 0
pym_tmp = []
pym_usr = []
with open(inpt_payment_filename, 'r') as f:
    reader = csv.reader(f)
    for line in reader:
        if flg_date==0: 
            flg_date+=1
            continue
        pym_tmp.append(line)
        pym_usr.append(line[0])
#
print "getted data"
lng = len(pym_tmp[0])
lp_cnt = 0
for Zu in Z_usrs:
    tmp = []
    if Zu not in pym_usr:
        tmp = [0]*(lng - 1)
        tmp.insert(0,Zu)
        result.append(tmp)
    else: 
        result.append(pym_tmp[lp_cnt])
        lp_cnt += 1

print("count done")
#
outfp = open('C:/Users/n_shimada/Desktop/Galster_CRM_mod_pyament.csv','w')
for r in result:
    outfp.write((",".join(map(str,r)))+"\n")
#
outfp.close()
print("that's all")