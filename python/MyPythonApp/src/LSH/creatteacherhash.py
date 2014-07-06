# coding: utf-8
'''
Created on 2013/11/29

@author: RN-017
'''

import sqlite3 as sqlite
import pickle
import hashing

class CreateDB(object):
    def __init__(self,dbname):
        self.db = sqlite.connect(dbname)
        self.db.text_factory = str # utf-8を使用するためにstrを指定
        self.hashing = hashing.Hashing()
    
    def __del__(self):
        self.db.close()
        
    def db_commit(self):
        self.db.commit()
        
    def create_hashtable(self, url, wordlist):
        hash_v = self.hashing.get_min_vector(wordlist)
        self.update_vector(url, pickle.dumps(hash_v))
        self.db_commit()

    def update_vector(self,url,vector):
        self.db.execute("update wordvector set hash_vector=? where url=?" , \
                         (vector, url))

if __name__=='__main__':
    dbname = 'teachre.db'
        
    c_db = CreateDB(dbname)
    
    con = sqlite.connect(dbname) # wordベクトルが格納されたDBを呼ぶ
    
    itr = 1
    while True:
        sql = "select * from wordvector where rowid=='%d'"        
        res = con.execute(sql % itr).fetchone()
        print res

        if res is None:break
        
        url = res[0]; category = res[1]; wordlist = res[2]
        c_db.create_hashtable(url, wordlist)
        
        itr += 1
    con.close()