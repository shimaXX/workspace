# coding: utf-8
'''
Created on 2013/12/21

@author: nahki
'''

import random

class Agent:
    def __init__(self,num):
        random.seed(num) # random seedの発生
        self.ctr = random.uniform(0,1)
        
    def get_ctr(self):
        return self.ctr
    
    def get_visiter_ctr(self, pred):
        if random.uniform(0,1) > (1-pred):
            return self.get_ctr()
        else: return False