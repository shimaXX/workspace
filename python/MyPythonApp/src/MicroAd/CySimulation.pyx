# coding:utf-8
#cython: boundscheck=False
#cython: wraparound=False
'''
Created on 2013/12/20

@author: RN-017
'''

import pyximport; pyximport.install()

from math import sin, cos, pi, fmod, sqrt, floor
import random

import useragent
import bidagent

import numpy as np
cimport numpy as np
cimport cython

DTYPE = np.float64
INTTYPE = np.int64
ctypedef np.float64_t DTYPE_t
ctypedef np.int64_t INTTYPE_t

cdef extern from 'stdlib.h':
    ctypedef unsigned long size_t
    void *malloc(size_t size)
    void free(void *prt)

class CreatePredict:
    pi2 = 2*pi
    #random.seed(3)
    PHI = 2*pi/8 # 位相のずれを表現
#    TBit = 10000000.0
    
    def __init__(self, period, agent_num):
        self.minbit = 1000*agent_num/1000
        self.E = 1250*agent_num/1000

        self.PERIOD = period
        self.OMEGA = self.pi2/self.PERIOD
        self.AGENT_NUM = agent_num

    def getvalue(self,period):
        cdef sec
        cdef np.ndarray[np.double_t, ndim=1] tmp = np.zeros(period,dtype=np.double)
        """
                    サイトに来る確率を算出するもの
        sin(theta) = sin(OMEGA*t + phi)
        T = 2*pai/OMEGA
        60*60*24=86400sec
        OMEGA = 2pai/86400
        """
        for sec in xrange(period):
            tmp[sec] = self.E * ( sin(self.OMEGA*sec - self.PHI) + 1 ) + self.minbit
        return tmp/self.AGENT_NUM  # predの算出     


cdef class ComputeBid:
    cdef int time, day
    gamma = 1.96 # 信頼区間の算出に使用(95%信頼区間を想定)
    beta1=0.3
    beta2=0.8
    
    theta_bin = 100

    cdef np.ndarray \
        bid_num,win_num,cmsp_bag,theta,ctr_hist,mu,sigma
    cdef int period, daybuget, gcpc, bidcap, bin_n
    cdef double ctrbin, avgprice
    
    def __init__(self,period,daybuget,gcpc,bidcap,ctrbin):
        self.period = period
        self.ctrbin = ctrbin
        
        self.daybuget = daybuget
        self.gcpc = gcpc
        self.bidcap = bidcap

        self.bid_num = np.zeros(period, dtype=np.int64)
        self.theta = np.zeros(self.theta_bin, dtype=np.float64)

        # ctrのhistグラムの格納
        self.bin_n = int( float(1.0)/ctrbin )
        self.ctr_hist = np.zeros((period,self.bin_n), dtype=np.int64)
        
        self.mu = np.zeros(period, dtype=np.float64) # 入札閾値のtauの各slot毎の平均値
        self.sigma = np.zeros(period, dtype=np.float64) #入札閾値のtauの各slot毎の分散
        self.avgprice = 0.0
    
    def __dealloc__(self):
        pass
    
    def output(self, file,user_agent_num,bid_agent_num,days):
        cdef int t,n,i,c,b
        
        # visit prediction の算出
        pred_creater = CreatePredict(self.period, user_agent_num)
    
        # user agentの発生
        user_agent = [ useragent.Agent(n) for n in xrange(user_agent_num) ]
        
        # bid agentの発生
        bid_agent = [ bidagent.Agent(n) for n in xrange(bid_agent_num) ]
           
        for t in xrange(self.period*days):
            self.time = fmod(t,self.period)
            if fmod(t,self.period)==0:
                if self.day!=0: self.avgprice /= sum(self.win_num)
                self.bid_num = np.zeros(self.period, dtype=np.int64)
                self.win_num = np.zeros(self.period, dtype=np.int64)
                self.cmsp_bag = np.zeros(self.period, dtype=np.float64)
                self.day+=1
                
            print "progress:",t
    
            # visit predictionの算出
            pred = pred_creater.getvalue(self.period)  
            # 各slotの予算配分の計算
            slot_bag = self.calc_slot_bag(pred)            
            
            # 訪問者のctrを取得
            ctr = []
            bidp = []
            visit = 0.0
            dbidprice = {}
            for i in xrange(user_agent_num):
                ctr.append( user_agent[i].get_visiter_ctr(pred[self.time]) )
            
                # 各agentの入札額の算出
                if ctr[i] == False: continue
                visit += 1.0
                
                """ ctrのヒストグラムを作成 """
                if self.day==1: self.get_hist(ctr[i])
                    
                maxprice = 0.0
                for b in xrange(bid_agent_num):
                    price = bid_agent[b].get_bid_price(ctr[i], pred[self.time])
                    if price > maxprice:
                        maxprice = price
                bidp.append(maxprice)

                """ 応札回数のカウントと入札額の決定 """
                # 応札価格設定に使用するpacing_rateを算出
                if self.bid_num[self.time]==0:
                    pacing_rate = 0.0
                else:
                    pacing_rate = self.bid_num[self.time]/float(visit)
                
                # 応札価格の決定
                bidprice = self.calc_bidprice(self.day, ctr[i], pacing_rate)
                print 'price',bidprice
                
                # 応札するかしないかの判断
                if bidprice == False: continue
                
                """ 算出された入札金額確認用の辞書作成 """
                if str(floor(bidprice)) not in dbidprice: dbidprice[str(floor(bidprice))] = 1
                else: dbidprice[str(floor(bidprice))] += 1
                
                # 応札額がcapを超えていればcapの値とする
                if bidprice>self.bidcap: bidprice = self.bidcap
                # 応札するのであれば応札回数をインクリ
                self.bid_num[self.time] += 1
                
                # 入札に勝利したかの判定
                if bidprice > maxprice:
                    # 応札するかどうかの判定
                    if slot_bag[self.time] - self.cmsp_bag[self.time] - bidprice > 0:
                        self.cmsp_bag[self.time] += bidprice
                        print 'cmsp=',self.cmsp_bag[self.time]
                        self.calc_theta(bidprice,maxprice)
                        self.win_num[self.time] += 1
                        # 1bid辺りの平均コストの計算
                        if self.day==1: self.avgprice += bidprice
        print dbidprice
        print np.float64(self.win_num)/self.bid_num
        num1 = []
        num2 = []
        for i in xrange(self.period):
            num1.append( str(slot_bag[i]) )
            num2.append( str(self.cmsp_bag[i]) )
        file.write(u'slot bags\n'+u','.join(num1)+u'\n')    
        file.write(u'comsumption bags\n'+u','.join(num2)+u'\n')
    
    def get_hist(self,ctr):
        """ ctrのヒストグラムを作成 """
        cdef int bin
        for bin in xrange(self.bin_n):
            if bin*self.ctrbin<=ctr<(bin+1)*self.ctrbin:
                self.ctr_hist[self.time,bin] += 1
                break
    
    def calc_bidprice(self, day, ctr, pacing_rate): #ctr[i]
        cdef int i
        tau = 0.0
        if day<2: 
            if ctr>=0.2:
                return random.randint(20,80)
            else: return False
        else:
            if self.cmsp_bag[self.time]!=0.0:
                # 予測impの算
                imps = float(self.cmsp_bag[self.time])/self.avgprice
                print 'imps',imps
                # 予測応札数の算出
                #win_rate = bid_num[self.time]/win_num[self.time]
                bids = float(imps*self.bid_num[self.time])/self.win_num[self.time]
                print 'bids',bids
                # 予測リクエスト数の算出
                print 'pacing_rate',pacing_rate
                reqs = bids/pacing_rate
            else:
                reqs=0.0
            
            print 'reqs',reqs
            # 入札の閾値の取得
            for i in xrange(len(self.ctr_hist[self.time,:])):
                if sum(self.ctr_hist[self.time,-(i+1):]) - reqs >0.0:
                    tau = float((self.theta_bin-1)-i)/self.theta_bin
                    break

            # 平均値の計算
            if self.time == 0: t = self.period - 1
            else: t = self.time-1 # ここでいうtはt-1とする
            div_t = float(1)/(self.time+1)
            self.mu[self.time] = self.mu[t]+ div_t*(tau-self.mu[t]) # muは現在のslotと過去のslot分の保存が必要かも
            # 分散の計算
            self.sigma[self.time] = div_t*t*self.sigma[t] \
                                + div_t*(tau-self.mu[t])*(tau-self.mu[self.time])
            
            # 暫定的な価格の決定
            u = ctr*self.gcpc # Ui = AR*G(予測CTR×目標CPC)
            
            # 応札率に応じて価格を決める
            # beta1=0.3, beta2=0.8と設定する
            price = self.get_price(pacing_rate,u)
            print 'price1',price
            
            # 応札するかの判定
            return self.judge_bid(pacing_rate,price,tau)

    def calc_theta(self,bidprice,secprice):
        cdef int b
        theta = float(secprice)/bidprice
        for b in xrange(100):
            if 0.01*b<=theta<=0.01*(b+1):
                self.theta[b] += 1
                break
    
    def calc_slot_bag(self,pred):
        s = sum(pred)
        prop = np.array(pred, dtype=DTYPE)/s
        return prop*self.daybuget
    
    def get_price(self,pacing_rate,u):
        price = 0.0
        if pacing_rate<=self.beta1:
            s_theta = sum(self.theta)
            s = 0.0
            for i in xrange(len(self.theta)):
                s += self.theta[i]
                if float(s)/s_theta>0.01:
                    return i*(float(3.0)/(2*self.theta_bin))*u #price = self.theta[i]*u
        elif pacing_rate>=self.beta2: # pacing_rageの予測を行わなければうまく動作しない
            lo =1.0 + (self.bidcap/self.avgprice-1.0)/(1.0-self.beta2) \
                                                        *(pacing_rate-self.beta2)
            return lo*u
        else:
            return u

    def judge_bid(self, pacing_rate, price, tau):
        term2 = self.gamma*self.sigma[self.time]/sqrt(self.day)
        print 'tau',tau

        if tau<self.mu[self.time]-term2: # 応札不採択上限
            return False
        elif tau>=self.mu[self.time]+term2: # 応札採択下限
            return price
        else:
            if pacing_rate>random.uniform(0,1):
                return price
            else: return False
        
    
""" 
if __name__=='__main__':
    period = 86400 # second of a day
    days = 2
    user_agent_num = 10000
    bid_agent_num = 100
    
    with open('sin','a') as f:
        output(f,user_agent_num,bid_agent_num,period,days)
"""