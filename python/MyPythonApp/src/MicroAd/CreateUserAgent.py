# coding:utf-8
'''
Created on 2013/12/20

@author: RN-017
'''

from math import sin, cos, pi
from random import random


class bid_agent():
    pi2 = 2*pi
    #random.seed(3)
    PHI = 2*pi/8 # 位相のずれを表現
    TBit = 10000000.0
    minbit = 1000
    
    def __init__(self, period):
        self.PERIOD = period
        self.OMEGA = self.pi2/self.PERIOD

    def getvalue(self,t):
        """
                    サイトに来る確率を算出するもの
        sin(theta) = sin(OMEGA*t + phi)
        T = 2*pai/OMEGA
        60*60*24=86400sec
        OMEGA = 2pai/86400
        """
        icos = 0.0
        for tt in xrange(self.PERIOD):
            icos += -cos(self.pi2/self.PERIOD*tt - self.PHI)
        print icos
        icos = self.OMEGA/self.pi2*icos
        E = float(self.TBit- self.minbit*self.PERIOD)/icos
        print E
        return E * sin(self.OMEGA*t - self.PHI) + E*sin(0.5*pi) # predの算出, max=-1.69318570908e+23     
        
if __name__=='__main__':
    period = 86400
    agent = bid_agent(period)
    for t in xrange(period):
        val = agent.getvalue(t)
        print "t=",t
        print "pred=",val