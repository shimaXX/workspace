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

dates_ls = []    #list of date
output = {}   #dictionary of mid-data
uNames = [] #list of uid
result = {}   #dictionary of result

raw_text = 'C:/HadoopPig/workspace/HadoopPig/works/output/Mining/GalsterCPM_D_20130328/part-m-'
input_filenames = []
for i in xrange(123):
    text = raw_text + ("00000" + str(i))[-5:]
    input_filenames.append(text)

# create DB
def get_db_conn(db_filename):
    if os.path.exists(db_filename):
        os.unlink(db_filename)
    
    db = sqlite3.connect(db_filename)
    db.text_factory=str
    return db


def import_data(db):
    db.execute("""create table seg_datas
       (uid varchar(20),
        AvgDate varchar(200),
        AvgBuyDate varchar(200),
        AvePayment varchar(200),
        ave_session_time varchar(200),
        CntArt varchar(200),
        CntSrch varchar(200),
        AvgSess varchar(200))""")
    
    for fname in input_filenames:
        with open(fname, 'r') as f:
            for line in f:
                uid, AvgDate, AvgBuyDate , AvePayment, ave_session_time, CntArt, CntSrch ,AvgSess = line.strip().split('\t')
                db.execute("insert into seg_datas values (?, ?, ?, ?, ?, ?, ?, ?)",
                            (uid, AvgDate, AvgBuyDate , AvePayment, ave_session_time, CntArt, CntSrch, AvgSess))
    db.commit()


class create_data(object):
    db = None
    
    def __init__(self, db):
        self.db = db

    def create_D_data(self):
        datas = self.db.execute("select * from  seg_datas")
        print("input done")
#       
#        for d in datas:
#            uid = d[0]; AvgVisitDate = d[1]; AvePayment = d[2]
#            AveSessionTime = d[3]; AveViewArt = d[4]
#
        outfp = open('C:/Users/n_shimada/Desktop/Galster_D_CRM.csv','w')
        for d in datas:
            nums = [str(d[i+1]) for i in xrange(len(d[1:]))]
            outfp.write( (",".join(nums))+"\n" )    
        print("mid done")     
#
        outfp.close()
#        
    def close(self):
        self.db.close()