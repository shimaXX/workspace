# coding:utf-8
'''
Created on 2013/12/20

@author: RN-017
'''

from math import sin, cos, pi, fmod
import random

import useragent
import bidagent


class CreatePredict:
    pi2 = 2*pi
    #random.seed(3)
    PHI = 2*pi/8 # 位相のずれを表現
    TBit = 10000000.0
    minbit = 1000
    E = 1250
    
    def __init__(self, period, agent_num):
        self.PERIOD = period
        self.OMEGA = self.pi2/self.PERIOD
        self.AGENT_NUM = agent_num

    def getvalue(self,t):
        """
                    サイトに来る確率を算出するもの
        sin(theta) = sin(OMEGA*t + phi)
        T = 2*pai/OMEGA
        60*60*24=86400sec
        OMEGA = 2pai/86400
        """
        tmp = self.E * ( sin(self.OMEGA*t - self.PHI) + 1 ) + self.minbit
        return tmp/self.AGENT_NUM  # predの算出     
        
if __name__=='__main__':
    period = 86400 # second of a day
    days = 2
    user_agent_num = 10000
    bid_agent_num = 100
        
    # visit prediction の算出
    pred_creater = CreatePredict(period, user_agent_num)

    # user agentの発生
    user_agent = [useragent.Agent(n) for n in xrange(user_agent_num)]
    
    # bid agentの発生
    bid_agent = [bidagent.Agent(n) for n in xrange(bid_agent_num)]
    
    with open('sin','a') as f:
        for t in xrange(period*days):
            print t
            pred = pred_creater.getvalue(fmod(t,period)) # visit predictionの算出
            # 訪問者のctrを取得
            ctr = [ u.get_visiter_ctr(pred) for u in user_agent]
            
            # 各agentの入札額の算出
            bidp = []
            for c in ctr:
                if c == False: continue
                bidp.append( max([b.get_bid_price(c, pred) for b in bid_agent]) )
            
            num = [str(b) for b in bidp if b!=False]
            
            f.write(','.join(num)+u'\n')