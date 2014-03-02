# coding: utf-8
'''
Created on 2014/01/08

@author: RN-017
'''

import random
import numpy as np

class DataGen:
    age_seg = 10
    geo_seg = 200
    act_seg = 1000
    
    def __init__(self,seed):
        np.random.seed(seed)
    
    def generate_line(self):
        demogra = self.generate_demogra()
        geogra = self.generate_geogra()
        act = self.generate_act()
        
        line = np.hstack((demogra, geogra))
        line = np.hstack((line, act))
    
        return demogra
        #return line
    
    def generate_demogra(self): # {0,1}+{0,1}*10　択一
        gender = np.random.randint(2)
        #gender = np.random.randint(2,size=2)
        age_idx = np.random.randint(self.age_seg)
        age = np.zeros(self.age_seg, dtype=np.int)
        age[age_idx] = 1
        
        return gender
        #return np.hstack((gender, age))
    
    # {0,1}*200 択一
    def generate_geogra(self):
        geo_idx = np.random.randint(0,self.geo_seg)
        geo = np.zeros(self.geo_seg ,dtype=np.int)
        geo[geo_idx] = 1
        
        return geo
    
    def generate_act(self): # {0,1}*1000　複数
        return np.random.randint(2,size=self.act_seg)