# -*- coding: utf-8 -*-
'''
Created on 2013/04/18

@author: n_shimada
'''
import math
import random
import numpy as np
 
 
class plsa(object):
 
    def __init__(self,n,nz=2):
        """ n:DW行列 nz:潜在変数の数"""
        self.n = n
        self.nz = nz
        # num of the docs
        self.nd = len(n)
        # num of the words
        self.nw = len(n[0])
         
        # initialize the probability
        self.pdwz = self.arr([ self.nd, self.nw, self.nz ]) # P(z|d,w)
        self.pzw = self.arr([ self.nz, self.nw ]) # P(w|z)
        self.pzd = self.arr([ self.nz, self.nd ]) # P(d|z)
        self.pz = self.arr([ self.nz ]) # P(z)
        self.pdw = self.arr([ self.nd, self.nw ]) # P(d,w)

    def train(self,k=1000):
        # 収束するまで繰り返す
        tmp = 0
        for i in range(k):
            self.e_step()
            self.m_step()
            L = self.likelihood()
            # 収束したか
            if abs(L - tmp) < 1.0e-10:
                break
            else:
                tmp = L
        
    @staticmethod
    def normalized(list):
        """ 合計が1になるように正規化する """
        total = sum(list) + 1.0e-9
        return map(lambda a: a/total, list)
     
    @staticmethod
    def arr(list):
        """ 多次元配列の生成する
        list=[M,N...] としたら M x N x... で要素がランダムの配列を返す """
        if len(list) > 1:
            return [ plsa.arr(list[1:]) for i in xrange(list[0]) ]
        else:
            return plsa.normalized(np.random.uniform(low=0.1, high = 0.9, size=list[0]))
     
    def likelihood(self):
        """ log-liklihood """
        # P(d,w)
        for d in range(self.nd):
            for w in range(self.nw):
                self.pdw[d][w] = sum([ self.pz[z]*self.pzd[z][d]*self.pzw[z][w] for z in xrange(self.nz) ]) 
        # Σ n(d,w) log P(d,w)
        return sum([ self.n[d][w]*math.log(self.pdw[d][w] + 1.0e-9) for d in xrange(self.nd) for w in xrange(self.nw) ])
     
    def e_step(self):
        """ E-step """
        # P(z|d,w)
        for d in xrange(self.nd):
            for w in xrange(self.nw):
                for z in xrange(self.nz):
                    self.pdwz[d][w][z] = self.pz[z]*self.pzd[z][d]*self.pzw[z][w]
                self.pdwz[d][w] = self.normalized(self.pdwz[d][w])
     
    def m_step(self):
        """ M-step """
        # P(w|z)
        for z in xrange(self.nz):
            for w in xrange(self.nw):
                self.pzw[z][w] = sum([ self.n[d][w]*self.pdwz[d][w][z] for d in xrange(self.nd) ])
            self.pzw[z] = self.normalized(self.pzw[z])
        # P(d|z)
        for z in xrange(self.nz):
            for d in xrange(self.nd):
                self.pzd[z][d] = sum([ self.n[d][w]*self.pdwz[d][w][z] for w in xrange(self.nw) ])
            self.pzd[z] = self.normalized(self.pzd[z])
        # P(z)
        for z in xrange(self.nz):
            self.pz[z] = sum([ self.n[d][w]*self.pdwz[d][w][z] for d in xrange(self.nd) for w in xrange(self.nw) ])
        self.pz = self.normalized(self.pz)

    """
    def caluc_prob_class(self):
        ''' calculate class probability '''
        pz = 
        for z in xrange(self.nz):
            p_cl = sum(self.pzd[z])
            p_non_cl = sum( (1 - self.pzd[z])/(self.nz-1) )
        return 
    """
 
if __name__ == '__main__':
    n = [[1,0,1,0],
        [0,1,0,1],
        [1,0,1,0]]
    p = plsa(n)
    p.train()
    print p.pz
    print p.pzd
    print p.pzw
    print np.array(p.pdwz)