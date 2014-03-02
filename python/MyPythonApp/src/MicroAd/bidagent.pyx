# coding: utf-8
'''
Created on 2013/12/21

@author: nahki
'''

import random
from math import ceil

class Agent:
    def __init__(self,n):
        random.seed(n) # random seedの発生
        self.ctr = random.uniform(0,1)
        self.maxprice = random.randint(40,90)

    def get_maxprice(self):
        return self.maxprice
        
    def get_bid_price(self, ctr, pred):
        price = self.maxprice*ctr*pred
        
        if random.uniform(0,1) > 0.35 :
            return ceil(price) + random.randint(0,5)
        else: 
            return False