# coding: utf-8
'''
Created on 2013/11/24

@author: nahki
'''

import sqlite3 as sqlite
import pickle


class checkDB:
    def __init__(self,dbname):
        self.con = sqlite.connect(dbname)
        
    def __del__(self):
        self.con.close()
        
    def check(self):
        tablename = 'wordvector' #'wordvector'
        word = self.con.execute( \
            "select * from %s limit 10" % (tablename)).fetchall()
        return word
    
if __name__=='__main__':
    dbname='spyder.db' #spyder.db
    c = checkDB(dbname)
    res = c.check()
    for r in res:
        print r[0]
        print "カテゴリ = ",r[1]
        print "hash= ",pickle.loads(r[3])