# coding: utf-8
'''
Created on 2014/01/15

@author: RN-017
'''

import numpy as np
from numpy.random import multivariate_normal, randint
import scipy as sp
from math import pi, sqrt, exp, log, pow

featdim = 100
eps = 10**(-6)


# generate data
def generate_data():
    sz = 100
    mu1 = randint(1,1000,size=sz)
    mu2 = randint(1000,2000,size=sz)
    mu3 = randint(3000,4000,size=sz)
    
    cov = np.eye(sz)
    
    x1 = multivariate_normal(mu1, cov, 100)
    x2 = multivariate_normal(mu2, cov, 20)
    x3 = multivariate_normal(mu3, cov, 50)
    
    return np.vstack((x1,x2,x3))

# 初期化
def init_param(cluster_num,featdim):
    mu = np.zeros((cluster_num,featdim),dtype=np.float64)
    sig = np.ones((cluster_num,featdim),dtype=np.float64) # 対角成分のみを保存し、多変量正規分布の計算をするときだけnp.eye(cluster_num)との積をする
    mix = np.array([float(1)/cluster_num]*cluster_num, dtype=np.float64)
    
    return mu, sig, mix, 

def init_alph(cluster_num, mu, sig):
    alph1 = []
    for k in cluster_num:
        alph1.append(1/cluster_num*dmnorm(mu[k], sig[k]))
    return np.array(alph1 ,dtype=np.float64)

def dmnorm(x, mu, sig): # π*Φ=gを出すためのΦ。このコードではπ=mix
    D = len(mu)
    
    if np.dot( -(x-mu)*(x-mu), float(1)/sig )*0.5 > 700:
        e = 700
    elif np.dot( -(x-mu)*(x-mu), float(1)/sig )*0.5 < -700:
        e = -700
    else:
        e = np.dot( -(x-mu)*(x-mu), float(1)/sig )*0.5
        
    return 1/((2 * pi)**D * sqrt(sum(sig*sig))) * exp(e)


def mv_norm(x, mu, sig):
    norm1 = 1 / (pow(2 * pi, len(x)/2.0) * pow(sqrt(sum(sig**2)), 0.5))
    x_mu = x-mu
    norm2 = np.exp( sum(-0.5 * x_mu * sig* x_mu) )
    return float(norm1 * norm2)

def Likelihood(xx, mu, sig, mix):
    K = len(mu)
    res = []
    for x in xx:
        res.append(
            #sum([log(mix[k]*dmnorm(x, mu[k],sig[k]*np.eye(featdim))) for k in xrange(K)])
            sum([log( mix[k]*dmnorm(x, mu[k],sig[k])+eps ) for k in xrange(K)]) # π*Φ
            )
    return sum(res)

def OnlineEM(xx,m,mu,sig,mix,gamma):
    N = len(xx) #データ点数
    K = len(mu)
    
    new_gamma = np.array([mix[k]*dmnorm(xx[m],mu[k],sig[k]) \
                           for k in xrange(K)],dtype=np.float64)

    new_gamma /= sum(new_gamma+eps)
    delta = new_gamma - gamma
    gamma = new_gamma
    
    mix = mix + delta/N
    N_k = mix*N
    for k in xrange(K):
        x = xx[m] - mu[k]
        d = delta[k]/N_k[k]
        mu[k] = mu[k]+d*x
        sig[k] = (1-d)*sig[k]+d*np.dot(x,x)
    return mix, mu, sig, gamma 

# Eステップ
def Estep():
    pass
    

# Mステップ
def Mstep():
    pass


# alphの算出
def get_alph( pxz,pre_alph, Ajk, clust_num):
    return [pxz*sum(pre_alph*Ajk) for k in clust_num]

# betaの算出
def get_beta():
    pass



# EM algorithm and Online EMA
if __name__ == '__main__':
    featdim = 100
    clustdim = 3
    
    xx = generate_data()
    gamma = np.ones(clustdim, dtype=np.float64)
    datanum = len(xx)
    
    for n in xrange(1):
        # 初期値
        mu, sig, mix = init_param(clustdim, len(xx[0]))
        
#         # 最初の一周は通常の EM
#         gamma_nk = Estep(xx, param)
#         param = Mstep(xx, gamma_nk)
#         gamma = gamma_nk

        # online EM
        likeli = -999999
        for j in xrange(1,100):
            for m in xrange(datanum):
                print m
                mix, mu, sig, gamma = OnlineEM(xx, m, mu, sig, mix, gamma)
            
            l = Likelihood(xx, mu, sig, mix)
            if l - likeli < 0.001: break
            likeli = l
    print mu