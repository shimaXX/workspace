# coding: utf-8
'''
Created on 2014/01/15

@author: RN-017
'''

import numpy as np
from numpy.random import multivariate_normal, randint, random, uniform
import scipy as sp
from math import pi, sqrt, exp, log, pow, isinf
from numpy.linalg import det


# generate data
def generate_data():
    np.random.seed(555)
    sz = 100
#    mu1 = uniform(0,1,size=sz)
#    mu2 = uniform(0,1,size=sz)
#    mu3 = uniform(0,1,size=sz)
    mu1 = uniform(0,20,size=sz)
    mu2 = uniform(20,40,size=sz)
    mu3 = uniform(40,60,size=sz)

    
    cov = np.eye(sz)
    
    x1 = multivariate_normal(mu1, cov, 10000)
    x2 = multivariate_normal(mu2, cov*0.2, 20000)
    x3 = multivariate_normal(mu3, cov*0.3, 10000)
    
#     return np.vstack((mu1,mu2,mu3))
    return np.vstack((x1,x2,x3))


class OnlineEM:
    def __init__(self,cluster_num,featdim,alpha):
        self.cluster_num = cluster_num
        self.alpha = alpha

        self.mu = np.zeros((cluster_num,featdim),dtype=np.float64)
        self.sig = np.ones((cluster_num,featdim),dtype=np.float64) # 対角成分のみを保存し、多変量正規分布の計算をするときだけnp.eye(cluster_num)との積をする
        
        #self.omega = np.array([float(1)/cluster_num]*cluster_num, dtype=np.float64) 
        self.omega = np.ones(cluster_num)
        
        self.sx = np.ones((cluster_num,featdim), dtype=np.float64)
        self.sx2 = np.ones((cluster_num,featdim), dtype=np.float64)
        
        # 学習係数の初期化
        self.gamma = 0.5
        
        # 更新回数
        self.t=1
        
        # ゼロ割回避の係数
        self.eps = 10**(-9)


    def init_beta(self,x):
        if self.t == 1:
            self.sx = np.array( [x]*self.cluster_num )
            self.sx2 = np.array( [np.power(x,2)]*self.cluster_num )
    
            for i in xrange(len(self.sx)):
                self.sx[i] *= uniform(0,1,len(x))
                self.sx2[i] *= uniform(0,1,len(x))
    
    def caluc_gamma(self):
        k = self.t-1        
        self.gamma = pow(k+2,-self.alpha) 
    
    def dmnorm(self, x, mu, sig): # π*Φ=gを出すためのΦ。このコードではπ=mix
        D = len(mu)
        
        tmp = np.dot( -(x-mu)*(x-mu), float(1)/sig )*0.5
        
        if tmp > 700:
            e = 700
        elif tmp < -700:
            e = -700
        else:
            e = tmp
        
        return 1/((2 * pi)**(0.5*D) * sqrt(sum(sig*sig))) * exp(e)

    def mv_norm(self, x, mu, sig):
        det_sig = float(1.0)
        for i in xrange(len(sig)):
            det_sig *= sig[i]

        norm1 = float(1) / (pow(2*pi, 0.5*len(x)) * pow(abs(det_sig), 0.5))
#        print "norm1:",norm1
        x_mu = x-mu
#        print "e1:",-0.5 * np.power(sig,-1).dot(x_mu*x_mu)
        norm2 = np.exp( -0.5 * np.power(sig,-1).dot(x_mu*x_mu) )
        norm1 = norm1 if norm1!=0 else pow(10,-9)
        norm2 = norm2 if norm2!=0 else pow(10,-9)
#        print "norm2:",norm2
        
        return float(1.0) if isinf(norm1) or isinf(norm2) else float(norm1 * norm2)
    
    
    def Likelihood(self, xx, mu, sig, mix):
        K = len(mu)
        res = []
        for x in xx:
            res.append(
                #sum([log(mix[k]*dmnorm(x, mu[k],sig[k]*np.eye(featdim))) for k in xrange(K)])
                sum([log( mix[k]*self.mv_norm(x, mu[k],sig[k])+self.eps ) for k in xrange(K)]) # π*Φ
                )
        return sum(res)
    
    
    def EMstep(self,x):
        """ クラスへの所属確率の算出と統計量の更新 """
        self.init_beta(x)
        self.caluc_gamma()
        self.mv_norm(x, self.mu[0], self.sig[0])
        psum = sum([self.omega[k]*self.mv_norm(x, self.mu[k], self.sig[k]) 
                    for k in xrange(self.cluster_num)])
#        psum = psum if psum!=0.0 else self.eps # zero割回避
        
        for k in xrange(self.cluster_num):
            ptheta = self.omega[k]*self.mv_norm(x, self.mu[k], self.sig[k])/psum
            
#             print "omega",self.omega
#             print "ptheta:",ptheta
#             print "ue",self.omega[k]*self.mv_norm(x, self.mu[k], self.sig[k])
#             print "psum:",psum
            # 混合割合の算出(右辺がEstep, 右辺から左辺がMstep)
            self.omega[k] = (1-self.gamma)*self.omega[k] + self.gamma*ptheta
            print "omega",self.omega[k]
        
            # 十分統計量の算出
            ## 正規分布の十分統計量：Σx
#            print "x:",x
#            print "sx:",self.sx[k]
            self.sx[k] = (1-self.gamma)*self.sx[k] + self.gamma*x*ptheta

            ## 正規分布の十分統計量：Σx^2
            self.sx2[k] = (1-self.gamma)*self.sx2[k] + self.gamma*np.power(x,2)*ptheta 
    
            mean = self.sx[k]
            sig2 = self.sx2[k] - np.power(self.sx[k],2)            
#             mean = self.sx[k]
#             sig2 = self.sx2[k]/self.omega[k] - np.power(self.sx[k]/self.omega[k],2)            
    
    
    
#             print "mean:",mean
#             print "sig2:",sig2
            self.mu[k] = mean/self.omega[k]
            self.sig[k] = sig2/self.omega[k]
#             self.mu[k] = mean
#            self.sig[k] = sig2
            
#             print "mu:",self.mu[k]
            print "sig:",self.sig[k]
        self.t += 1

    def get_param(self):
        return self.omega, self.mu, self.sig

class Test:
    def __init__(self, cluster_num):
        self.clust = []
        self.cluster_num = cluster_num
    
    def get_cluster(self):
        return self.clust
    
    def test(self,omega,x,mu,sig):
        s_prob = sum([omega[k]*self.mv_norm(x,mu[k],sig[k]) for k in xrange(self.cluster_num)])
        s_prob = s_prob if s_prob!=0.0 else pow(10,-9) 
        self.clust.append( self.caluc_clust(omega,x,mu,sig,s_prob) )        

    def caluc_clust(self,omega,x,mu,sig,s_prob):
        maxp = -1000
        max_k = -1000
        for k in xrange(self.cluster_num):
            print "omega:", omega
            prob = omega[k]*self.mv_norm(x,mu[k],sig[k])/s_prob
            if prob > maxp:
                max_k = k
        return max_k

    def dmnorm(self, x, mu, sig): # π*Φ=gを出すためのΦ。このコードではπ=mix
        D = len(mu)
        
        if np.dot( -(x-mu)*(x-mu), float(1)/sig )*0.5 > 700:
            e = 700
        elif np.dot( -(x-mu)*(x-mu), float(1)/sig )*0.5 < -700:
            e = -700
        else:
            e = np.dot( -(x-mu)*(x-mu), float(1)/sig )*0.5
            
        return 1/((2 * pi)**D * sqrt(sum(sig*sig))) * exp(e)

    def mv_norm(self, x, mu, sig):
        norm1 = 1 / (pow(2*pi, 0.5*len(x)) * pow(sqrt(sum(sig**2)), 0.5))
        x_mu = x-mu
        norm2 = np.exp( sum(-0.5 * x_mu * sig* x_mu) )
        return float(norm1 * norm2)

# EM algorithm and Online EMA
if __name__ == '__main__':
    featdim = 100
    clustdim = 3
    alpha = 0.5
    
    data = generate_data()
    
    em = OnlineEM(clustdim,featdim,alpha)
    
    for n in xrange(2):
        # online EM
#        likeli = -999999
        for x in data:
            em.EMstep(x)
        
#         l = Likelihood(xx, mu, sig, mix)
#         if l - likeli < 0.001: break
#         likeli = l
    omega, mu, sig = em.get_param()
    print mu
    print sig
    print omega
    
    """
    test = Test(clustdim)
    for x in data:    
        test.test(omega, x, mu, sig)
        clus = test.get_cluster()
    print clus
    """