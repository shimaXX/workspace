# coding: utf-8
'''
Created on 2013/11/28

@author: RN-017
'''

import numpy as np
import mmh3
from multiprocessing import *


class Hashing(object):
    ''' 
            各urlで取得した単語集合に対して、hashingをかけて、最小値を取得
      url毎にk次元のベクトルを取得する
            このk次元ベクトルを比較することによって類似度を判定する
    '''
    def __init__(self,bbit=1,k=128):
        self.bbit = bbit
        self.hash_cnt = k
    
    def get_min_vector(self,feat_names):
        ''' この関数はurl分回すことになる '''
        hash_vec = []
        # 単語集合のhashの最小値のみをk回取得
        for seed in xrange(self.hash_cnt): # self.hash_cnt分のseedを発生させる
            pool = Pool(processes=8)
            hash_val = pool.map( get_hash_value, ((feat_name, seed) for feat_name in feat_names) ) # k個のseedを使ってk個のhash関数を発生
            pool.close()
            pool.join()
            min_val = int( str( min(hash_val) )[-self.bbit] ) 
            hash_vec.append(min_val) # 最小値の1桁目のみ取得する
        return hash_vec
        
def get_hash_value((feat_name,seed)):
    return mmh3.hash(feat_name,seed)
    
if __name__=='__main__':
    feat="aaa\tbbb\tccc\t"
    hashing = Hashing()
    print hashing.get_min_vector(feat)