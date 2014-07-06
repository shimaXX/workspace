# coding: utf-8
'''
Created on 2013/11/24

@author: nahki
'''

import sqlite3 as sqlite
import pickle
import dis

class checkDB:
    def __init__(self,dbname):
        self.con = sqlite.connect(dbname)
        
    def __del__(self):
        self.con.close()
        
    def check(self):
        tablename = 'tweet_master' #'wordvector'
        word = self.con.execute( \
            "select * from %s" % (tablename))#.fetchall()
        return word
    
def while_loop(res):
    while 1:
        r = res.fetchone()
        if r == None: break
        print r[0]
#         print r[2]
#         print r[3]
#         for w in pickle.loads(r[1]):
#             print "words= ", w        

def for_loop(res):
    for r in res:
        print r[0]
#         print r[2]
#         print r[3]
#         for w in pickle.loads(r[1]):
#             print "words= ", w        

    
if __name__=='__main__':
    dbname='asumama_bf_classify.db' #spyder.db
    c = checkDB(dbname)
    res = c.check()
    dis.dis(while_loop)

    """
#    for r in res:
    while True:
        r = res.fetchone()
        if r == None: break
        print r[0]
        print r[2]
        print r[3]
#        print "word=", r[1]
 
        for w in pickle.loads(r[1]):
            print "words= ", w
    """