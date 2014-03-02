# coding: utf-8
'''
Created on 2013/11/28

@author: RN-017
'''

import numpy as np
import sqlite3 as sqlite
import hashing
import pickle
from multiprocessing import *

class MinHash(object):
    def __init__(self,train_dbname,teacher_dbname):
        self.train_db = sqlite.connect(train_dbname)
        self.teacher_db = sqlite.connect(teacher_dbname)
        self.hashing = hashing.Hashing() # default values are bbit=1, k=128
        
    def __del__(self):
        self.train_db.close()
        self.teacher_db.close()
        
    def db_commit(self):
        self.train_db.commit()
        
    def get_category(self):
        learner_urls = self.get_urls(self.train_db)
        teacher_urls = self.get_urls(self.teacher_db)
        for lrnr_url in learner_urls:
            print "computing hash vector:", lrnr_url[0]
            learner_hash =  self.calculate_hashvecotr( lrnr_url[0] )
            
            print "calculating similarity:", lrnr_url[0]
            learner_words =  self.get_wordslist( self.train_db,lrnr_url[0] )
            
            pool = Pool(processes=8)
            sim = pool.map(  similarity_value,
                        ( (learner_words, self.get_wordslist( self.teacher_db,tchr_url[0] ),
                             learner_hash, self.get_hash_vector(tchr_url[0]))
                                                for tchr_url in teacher_urls )  )  # 類似度の算出
            pool.close()
            pool.join()
            
            sim = np.array(sim)
            print "sim: ",sim
            idx = np.where(sim==max(sim))[0][0]
            sim_url = teacher_urls[idx][0]
            
            category = self.get_similer_category( sim_url )
            print "similar category of this URL is: ", category
            self.update_category(category, sim_url)

    def calculate_hashvecotr(self, url):
        """ hashベクトルを作りつつ、元のDBをupdate """
        hash_vector = self.hashing.get_min_vector( 
                            self.get_wordslist(self.train_db, url) )
        self.train_db.execute( "update wordvector set hash_vector=? where url=?" , 
                                    (url, pickle.dumps(hash_vector), ) ) # pickleで保存する
        self.db_commit()
        return hash_vector
    
    def update_category(self,category,url):
        self.train_db.execute( "update wordvector set category=? where url=?" ,(category, url, ) )
        self.db_commit()
    
    def get_wordslist(self,db,url):
        wordlist = db.execute( "select words from wordvector where url=?" , (url,) ).fetchone()[0]
        return pickle.loads(wordlist)
        
    def get_urls(self,db):
        return db.execute("select url from wordvector").fetchall()
    
    def get_similer_category(self,url):
        return self.teacher_db.execute( "select category from wordvector where url=?" ,(url, ) ).fetchone()[0]

    def get_hash_vector(self,url):
        hash_v = self.teacher_db.execute( "select hash_vector from wordvector where url=?" , (url, ) ).fetchone()[0]
        return pickle.loads(hash_v)

def similarity_value( (lrnr_words, teacher_words, lrnr_hash, teacher_hash) ):
    try:
        feat_dim = 1 << len(lrnr_hash)
        C1, C2 = calculate_distribusion(lrnr_words, teacher_words, feat_dim)
        
        jaccard = float( sum( np.array(lrnr_hash)==np.array(teacher_hash) ) ) \
                                                    /len(lrnr_hash) # 類似度の算出
        #return C1+(1-C2)*jaccard
        return (jaccard-C1)/(1-C2)
    
    except Exception, e:
        import sys
        import traceback
        sys.stderr.write(traceback.format_exc())

def calculate_distribusion(lrnr_words, teacher_words, feat_dim):
    all_words = lrnr_words | teacher_words
    D = len(all_words); f1 = len(lrnr_words); f2 = len(teacher_words)
    r1 = float(f1)/D; r2 = float(f2)/D; sum_r = r1 + r2
        
    A1 = calc_A(r1, feat_dim); A2 = calc_A(r2,feat_dim)

    C1 = A1*r2/sum_r + A2*r1/sum_r
    C2 = A1*r1/sum_r + A2*r2/sum_r
    
    return C1, C2
    
def calc_A(r, feat_dim):
    A_num = r*(1-r)**(feat_dim-1)
    A_denom = 1-(1-r)**feat_dim
    return A_num/A_denom
    
if __name__=='__main__':
    traindbname = 'learner.db'
    teacherdbname = 'teacher.db'
     
    minhash = MinHash(traindbname,teacherdbname)
    minhash.get_category()