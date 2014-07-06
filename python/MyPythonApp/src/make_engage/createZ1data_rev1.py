# coding: utf8
#'''
#Created on 2013/02/22
#
#@author: n_shimada
#'''
from __future__ import with_statement
import sqlite3
import os

dates_ls = []    #list of date
output = {}   #dictionary of mid-data
uNames = [] #list of uid
result = {}   #dictionary of result

#with open('C:/HadoopPig/workspace/HadoopPig/works/output/Mining/GalsterCPM_Z_20130205/Part-r-00000') as f:

# create DB
def get_db_conn(db_filename):
    if os.path.exists(db_filename):
        os.unlink(db_filename)
    
    db = sqlite3.connect(db_filename)
    db.text_factory=str
    return db


def import_data(db, inpt_filenames):
#    db.execute("""create table days
#       (uid  varchar(20),
#        date char(10),
#        pym varchar(200))""")

    db.execute("""create table days
       (uid  varchar(20),
        date char(10),
        pym varchar(200))""")

    for i in xrange(len(inpt_filenames)):    
        with open(inpt_filenames[i], 'r') as f:
            for line in f:
                uid,date,pym = line.strip().split('\t')
                db.execute("insert into days values (?, ?, ?)",
                            (uid, date, pym))
    db.commit()


class create_data(object):
    db = None
    
    def __init__(self, db):
        self.db = db

    def create_Z_data(self):
        usrNames = self.db.execute("select distinct uid from days order by uid asc").fetchall()
        dates = self.db.execute("select distinct date from days where date != 'none' order by date asc").fetchall()
        datas = self.db.execute("select * from days ")
        print("input done")
#       
        for date in dates:
            dates_ls.append(str(date[0]))
        for d in datas:
            uid = d[0]
            date = d[1]
            pym = d[2]
            if uid not in result:
                result[uid]={}
            if date != 'none':
                result[uid][date] = pym
        outfp = open('C:/Users/n_shimada/Desktop/Galster_CRM_pymData.csv','w')
        outfp.write(",".join(dates_ls)+"\n")
        for rname in usrNames:
            nums = [str(result.get(rname[0], {}).get(x, 0)) for x in dates_ls]
            outfp.write(rname[0] +","+ (",".join(nums))+"\n")    
        print("mid done")     
#
        outfp.close()

        
    def cnt_date(self):
        inpt=[]
        result=[]
        cnt_lp = 0
        with open('C:/Users/n_shimada/Desktop/Galster_CRM.csv', 'r') as f:
            for line in f:
                inpt = line.strip().split('\t')[1:]
                result.append(inpt)
                fvisit_flag = 0
                cnt = 0      
                for d in xrange(len(input)):
                    if fvisit_flag == 0 and inpt[d] > 0:
                        fvisit_flag=1
                        result[cnt_lp][d] = 0
                    if fvisit_flag == 1:
                        if result[cnt_lp][d] == 0:
                            cnt += 1
                        else:
                            cnt = 0
                    result[cnt_lp][d] = cnt
                cnt_lp+=1
    #
        print("count done")
    #
        outfp = open('C:/Users/n_shimada/Desktop/Galster_CRM_manuf.csv','w')
        for r in result:
            outfp.write((",".join(r))+"\n")
#
        outfp.close()
    
    def close(self):
        self.db.close()