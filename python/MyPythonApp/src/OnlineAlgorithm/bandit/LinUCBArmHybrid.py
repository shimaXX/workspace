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
    Aa = None
    Ba = None
    ba = None
    alph = None
    
    def __init__(self,name,alph,featdim,arms_num):
        self.alph = alph
        self.Aa = np.ones(featdim)
        self.Ba = np.zeros((featdim, arms_num))
        self.ba = np.zeros(featdim)
        self.invAa = np.ones(featdim)
        self.z = np.zeros(arms_num)
        self.z[name] = 1.0
    
    def calculate_theta(self,betahat): # リッジ回帰のweightを算出
        return self.invAa*(self.ba - np.dot(self.Ba,betahat) )
    
    def calculate_prediction(self,features,betahat,A0): # featuresはnumpy形式を想定
        self.invAa = 1/self.Aa
        theta = self.calculate_theta()
        s = np.dot(1/A0, self.z*self.z) 
        s -= 2*np.dot( np.dot(self.z/A0, self.Ba.T), self.invAa*features )
        s += np.dot( self.invAa,features*features )
        s += sum( np.dot(features*self.Aa, self.Ba) 
                  *1/A0* np.dot(self.Ba, self.Aa*features) )
        
        pred = self.alph*sqrt(s)
        pred += np.dot(self.z, betahat) + np.dot(features, theta)
        return pred
    
    def update_param(self,features,r,A0, b0): # featuresはnumpy形式を想定. rは0,1
        A0 += np.dot(self.Ba.T, np.dot(self.invAa,self.Ba))
        b0 += np.dot(self.Ba,self.invAa*self.ba) # self.Baを転置する必要がある？
        
        self.Aa += features*features
        self.Ba += features*features
        self.ba +- r*features
        
        A0 += self.z*self.z - np.dot( self.Ba.T, np.dot(self.invAa, self.Ba) )
        b0 += r*self.z - np.dot(self.Ba,self.invAa*self.ba)