# coding: utf8
'''
Created on 2013/09/03

@author: RN-017
'''

import numpy as np
import scipy as sp
from scipy.stats import poisson
import math

period = 10008
looptime = 24

def create_data():
    bidinfo = np.zeros((period,6)) #パラメタはリクエスト数, 入札数, 入札勝利数, 入札価格, 残り予算額, CTR
    tmp_req = []
    for i in xrange(looptime):
        if 0<=i<=5: tmp_req.append(1500)
        elif 6<=i<=8: tmp_req.append( 1500 - (1500-300)/(8-6+1)*(i-5) )
        elif 9<=i<=10: tmp_req.append( 300 )
        elif 11<=i<=12: tmp_req.append( 300+(1000-300)/(12-11+1)*(i-10) )
        elif 12<=i<=14: tmp_req.append( 1000 )
        elif 15<=i<=16: tmp_req.append( 1000 - (1000-300)/(16-15+1)*(i-14) )
        elif 17<=i<=18: tmp_req.append( 300 )
        elif 19<=i<=20: tmp_req.append( 300+(1500-300)/(20-19+1)*(i-18) )
        else: tmp_req.append( 1500 )
    bidinfo[:,0] = np.array( tmp_req*417 ) # request
    bidinfo[:,1] = np.array( [ bidinfo[i,0]*np.random.uniform(0,1,size=1)[0] for i in xrange(period)] ) # 入札回数
    bidinfo[:,2] = np.array( [ bidinfo[i,1]*np.random.uniform(0,1,size=1)[0] for i in xrange(period) ] ) #勝利数
    #bidinfo[:,3] = np.array( [ int(float(10)/(bidinfo[i,0]/1500*0.95)) for i in xrange(period) ] ) #入札価格
    bidinfo[:,3] = np.array( [ 10 for i in xrange(period) ] ) #入札価格
    
    #残予算
    for i in xrange(period/looptime):
        buget = 150000
        for j in xrange(looptime):
            buget -= bidinfo[i*looptime+j,2]*bidinfo[i*looptime+j,3]
            bidinfo[i*looptime+j,4] = buget
    bidinfo[:,5] = np.abs( np.random.normal(0.01, 0.005, period) ) #CTR
    
    return bidinfo


def calc_thresh(tau):
    d = 7 #統計量を計算するために使用したデータの日数
    gamma = 1.96
    mu, sig2 = calc_param(tau)
    mu = np.array(mu); sig2 = np.array(sig2)
    thresh1 = mu - gamma*np.sqrt(sig2)/math.sqrt(d) #入札をしないための閾値の上限値
    thresh2 = mu + gamma*np.sqrt(sig2)/math.sqrt(d) #入札を実施するための閾値の下限値
    
    tmp=thresh1[0]
    t1 = thresh1.tolist()
    t1.remove(tmp)
    thresh1 = np.array(t1)

    tmp=thresh2[0]
    t2 = thresh2.tolist()
    t2.remove(tmp)
    thresh2 = np.array(t2)
        
    return thresh1, thresh2

def calc_param(tau):
    mu = []
    sig2 = []
    mu.append(0.00001)
    sig2.append(0.0001) # 初期値は大きめに取っておかないとマイナスになる可能性がある 
    for t in xrange(1,len(tau)):
        mu.append( tau[t-1] + 1/t*(tau[t] - mu[t-1]) )
        sig2.append( np.round(float(t-1)/t*sig2[t-1]+1/t*(tau[t]-mu[t-1])*(tau[t]-mu[t]),5) )
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/mu.csv',mu,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/sig2.csv',sig2,delimiter=',')    
    return mu, sig2
        

if __name__=='__main__':
    bidinfo = create_data()
    
    c = 40
    s = bidinfo[:,2]*bidinfo[:,3] # 消費金額
    imps = s/c
    win_rate = bidinfo[:,2]/bidinfo[:,1]
    bids = imps/win_rate
    pacing_rate = bidinfo[:,1]/bidinfo[:,0]
    reqs = bids/pacing_rate
    
    qs = poisson.pmf(np.arange(100000), 100)*1500 #CTRは基本0.00001としてbinを0.00001とする。平均CTRは0.0001とするので平均は100
    
    tmp =0; sum = []
    for v in qs:
        tmp = tmp+v
        sum.append(tmp)
    sum = np.array(sum)
    #tmp = np.array([ np.abs(sum - bidinfo[i,0]) for i in xrange(bidinfo.shape[0]) ])
    tau = []
    for i in xrange(bidinfo.shape[0]):
        tmp = np.abs(sum - reqs[i])
        tau.append( np.where( tmp==np.min(tmp) )[0][0]*0.00001 )
    thresh1, thresh2 = calc_thresh(tau)
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/tau.csv',tau[1:],delimiter=',')
    
    sub1 = tau[1:] - thresh1
    sub2 = tau[1:] - thresh2
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/sub1.csv',sub1,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/sub2.csv',sub2,delimiter=',')
    nbid = (sub1<0)*1
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/nbid.csv',nbid,delimiter=',')
    bid = (sub2>0)*1
    rbid = (sub1>=0)*(sub2<=0)*1
    
    pacing_rate = pacing_rate[1:]
    for i in xrange(len(rbid)): 
        if rbid[i] == 1:
            #if pacing_rate[i] > np.random.uniform(0,1,size=1):
            if 1 >= np.random.uniform(0,1,size=1):
                rbid[i] = 1
            else: rbid[i] = 0
    
    fbid = bid+rbid
    
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/bidinfo.csv',bidinfo,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/fbid.csv',fbid,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/rbid.csv',rbid,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/bid/bid.csv',bid,delimiter=',')    