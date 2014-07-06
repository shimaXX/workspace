# coding: utf8
'''
Created on 2012/12/10

@author: n_shimada
'''
import os
import sqlite3
import csv

from __future__ import with_statement


input_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/TEST/EvaSeq1209/part-r-00000"
db_filename = "verb_data.db"

output = {}

with open(input_filename) as f:
    for line in f:
        cols = line.strip().split()
        uid = cols[0]
        num = cols[2]
        if uid not in output:
            output[uid] = []
        output[uid].append(num)

outfp = open('C:/Users/n_shimada/Desktop/EvaSeq1209.csv','w')
for rname in output.keys():
    nums = [str(x) for x in output[rname]]
    outfp.write(rname +","+ (",".join(nums))+"\n")

outfp.close()

