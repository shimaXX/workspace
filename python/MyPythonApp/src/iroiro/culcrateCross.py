# coding: utf8
'''
Created on 2012/10/25

@author: n_shimada
'''
import os
import sqlite3
import csv

from __future__ import with_statement


csv_filename = "C:/HadoopPig/workspace/HadoopPig/works/output/Ci-Labo/Ci-LaboTrack1203/part-m-00000.csv"
db_filename = "verb_data.db"

verbs = []

if os.path.exists(db_filename):
  os.unlink(db_filename)

db = sqlite3.connect(db_filename)
db.text_factory=str

db.execute("""create table verb
    (last_verb varchar(50),
    post_verb varchar(50),
    cnt int)""")
   
for last_veb, post_veb, cnt in csv.reader(open(csv_filename), delimiter = '\t'):
    db.execute("insert into verb values (?, ?, ?)",
               (last_veb, post_veb, cnt))

db.commit()

node = db.execute("select distinct disverb  from (select distinct last_verb as disverb from verb UNION ALL select distinct post_verb as disverb from verb)")
for row in node:
    verbs.append(row[0])

        
#verbs = ['a_favorite','article','buy','cart','category','comment','customer_del','customer_reg','entry','eva_movie','inquiry_article','login','mail_magazine_del','mail_magazine_reg','mypage','order_list','re_mail','realstore','search','top','w_favorite','fes_bardiel','fes_past_movie','fes_past_plan','fes_photo','fes_shinkei','fes_yurusito']
#ColVerbs = ['top','comment','search','new','category','article','cart','login','buy','w_review','a_review','w_favorite','a_favorite','ranking','mypage','order_list','customer_reg','mail_reg','inquiry_article','entry','re_mail','article','mail_del','customer_del','inquiry']

output = {}

with open('C:/HadoopPig/workspace/HadoopPig/works/output/Ci-Labo/Ci-LaboTrack1203/part-m-00000') as f:
    for line in f:
        cols = line.strip().split()
        verb_from = cols[0]
        verb_to = cols[1]
        num = cols[2]
        if verb_from not in output:
            output[verb_from] = {}
        output[verb_from][verb_to] = num

outfp = open('C:/Users/n_shimada/Desktop/Ci-LaboTrack1203.csv','w')
outfp.write(",".join(verbs)+"\n")
for rname in verbs:
    nums = [str(output.get(rname, {}).get(x, 0)) for x in verbs]
    outfp.write(rname +","+ (",".join(nums))+"\n")

outfp.close()
db.close()        

