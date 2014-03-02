# coding: utf-8
'''
Created on 2014/01/07

@author: RN-017
'''

import numpy as np
import scipy as sp
import random
from math import sqrt

# 各腕はコンテンツ
class Arm:
    # 属性
    A = None
    b = None
    alph = None
    sum_r = 0
    
    def __init__(self,name,alph,featdim):
        self.alph = alph # 学習係数.0.2くらいでちょうどいい?
        self.A = np.ones(featdim)
        self.b = np.zeros(featdim)
        self.name = name
        random.seed(name)
    
    def calculate_theta(self): # リッジ回帰のweightを算出
        return 1/self.A*self.b
    
    def calculate_prediction(self,features): # featuresはnumpy形式を想定
        theta = self.calculate_theta()
        pred = self.alph*sqrt( sum(features*features/self.A) )
        pred += np.dot(theta, features)
        return pred
    
    def update_param(self,features): # featuresはnumpy形式を想定. rは0,1
        r = self.gen_r(features)
        #r = self.gen_r2(features)
        self.sum_r += r                                
        self.A += features*features
        self.b += r*features
        
    def gen_r(self, features):
        r = 0
        if self.name == 0:
            if features==0: # 男性の時にCTR 10%
                if random.uniform(0,1)<= 0.1:
                    r = 1
                else: r = 0
            elif features==1: # 女性の時にCTR 1%
                if random.uniform(0,1)<= 0.01:
                    r = 1
                else: r = 0

        elif self.name == 1:
            if features==0: # 男性の時にCTR 5%
                if random.uniform(0,1)<= 0.05:
                    r = 1
                else: r = 0
            elif features==1: # 女性の時にCTR 5%
                if random.uniform(0,1)<= 0.05:
                    r = 1
                else: r = 0
        return r
    
    def gen_r2(self,features):
        r = 0
        if self.name == 0:
            if features[0]==0 and features[1]==0: # 男性かつseg=0の時にCTR 10%
                if random.uniform(0,1)<= 0.1:
                    r = 1
                else: r = 0
            elif features[0]==0 and features[1]==1: # 男性かつseg=1の時にCTR 1%
                if random.uniform(0,1)<= 0.01:
                    r = 1
                else: r = 0
            elif features[0]==1 and features[1]==0: # 女性かつseg=0の時にCTR 1%
                if random.uniform(0,1)<= 0.01:
                    r = 1
                else: r = 0
            elif features[0]==1 and features[1]==1: # 女性かつseg=0の時にCTR 1%
                if random.uniform(0,1)<= 0.01:
                    r = 1
                else: r = 0

        elif self.name == 1:
            if features[0]==0 and features[1]==0: # 男性かつseg=0の時にCTR 1%
                if random.uniform(0,1)<= 0.01:
                    r = 1
                else: r = 0
            elif features[0]==0 and features[1]==1: # 男性かつseg=1の時にCTR 4%
                if random.uniform(0,1)<= 0.04:
                    r = 1
                else: r = 0
            elif features[0]==1 and features[1]==0: # 女性かつseg=0の時にCTR 4%
                if random.uniform(0,1)<= 0.04:
                    r = 1
                else: r = 0
            elif features[0]==1 and features[1]==1: # 女性かつseg=0の時にCTR 4%
                if random.uniform(0,1)<= 0.04:
                    r = 1
                else: r = 0
        return r        
    
    def get_r(self):
        return float(self.sum_r)