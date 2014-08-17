# coding: utf-8

import numpy as np
from numpy.random import uniform, multivariate_normal
from math import pi, sqrt, exp, log, pow, isinf
from numpy.linalg import det, eig, inv
from scipy.sparse.linalg import svds
from numpy import kron

# generate data
def generate_data(featdim,row_size):
    np.random.seed(555)
    sz = featdim

    mu1 = uniform(0,20,size=sz)
    mu2 = uniform(20,40,size=sz)
    mu3 = uniform(40,60,size=sz)
    
    cov = np.eye(sz)
    
    x1 = multivariate_normal(mu1, cov*5, size=row_size)
    x2 = multivariate_normal(mu2, cov*50, size=row_size)
    x3 = multivariate_normal(mu3, cov*200, size=row_size)

    x1 = np.hstack( (np.zeros((row_size, 1)),x1) )
    x2 = np.hstack( (np.ones((row_size, 1)),x2) )
    x3 = np.hstack( (np.ones((row_size, 1))*2,x3) )
#     return np.vstack((mu1,mu2,mu3))
    return np.vstack((x1,x2,x3))


class OnlineEM:
    # 学習係数の初期化
    gamma = 1
    # 更新回数
    t=1
    # ゼロ割回避の係数
    eps = 10e-6
    
    def __init__(self,cluster_num,featdim,alpha=0.5):
        self.cluster_num = cluster_num
        self.alpha = alpha

        self.mu = np.zeros((cluster_num,featdim),dtype=np.float64)
        self.sig = np.array( [np.eye(featdim) for _ in xrange(cluster_num)])  # 対角成分のみを保存し、多変量正規分布の計算をするときだけnp.eye(cluster_num)との積をする
        
        self.omega = np.ones(cluster_num)/cluster_num
        
        self.sx0 = np.ones((cluster_num,featdim), dtype=np.float64)
        self.sx1 = np.ones((cluster_num,featdim), dtype=np.float64)
        self.sx2 = np.array( [np.eye(featdim) for _ in xrange(cluster_num)] )

    def init_beta(self,x):
        if self.t == 1:
            #self.sx1 = np.array( [x]*self.cluster_num )
            #self.sx2 = np.array( [np.power(x,2)]*self.cluster_num )
    
            for i in xrange(len(self.sx1)):
                self.sx0[i] *= uniform(0,1,len(x))
                self.sx1[i] *= uniform(0,1,len(x))
                for j in xrange(len(x)):
                    self.sx2[i,j] *= uniform(0,1,len(x))
    
    def caluc_gamma(self):
        k = self.t-1        
        self.gamma = pow(k+2,-self.alpha)  

    def mv_norm(self, x, mu, sig):
        #cov = np.eye(len(sig))
        lam, v = eig(sig)
        lam[lam<0] = self.eps
        print lam.shape, v.shape
        
        _lam = np.eye(len(x))
        for i in xrange(len(lam)):
            _lam[i,i] = lam[i]
        
        _sig = v.dot(_lam).dot(v.T)
        
        print det(_sig), _sig
        norm1 = (float(1)+self.eps) / ( pow(2*pi, 0.5*len(x)) * pow(det(_sig), 0.5) + self.eps )
        x_mu = x - mu
        norm2 = np.exp( -0.5 * x_mu.dot( inv(_sig) ).dot(x_mu) )
        norm1 = norm1 if norm1!=0 else self.eps
        norm2 = norm2 if norm2!=0 else self.eps
        return float(1.0) if isinf(norm1) or isinf(norm2) else float(norm1 * norm2)
    
    def calculate_det(self,_lambda):
        det = float(1.0)
        for l in _lambda:
            det *= l
        return det
    
    def Likelihood(self, xx, mu, sig, mix):
        K = len(mu)
        res = []
        for x in xx:
            res.append(
                sum([log( mix[k]*self.mv_norm(x, mu[k],sig[k])+self.eps ) for k in xrange(K)]) # π*Φ
                )
        return sum(res)
    
    def EMstep(self,x):
        """ クラスへの所属確率の算出と統計量の更新 """
        self.init_beta(x)
        self.caluc_gamma()
        psum = sum([self.omega[k]*self.mv_norm(x, self.mu[k], self.sig[k]) 
                    for k in xrange(self.cluster_num)])
        for k in xrange(self.cluster_num):
            print "clus", k
            ptheta = self.omega[k]*self.mv_norm(x, self.mu[k], self.sig[k])/psum
            
            # 混合割合の算出(右辺がEstep, 右辺から左辺がMstep)
            self.omega[k] = (1-self.gamma)*self.omega[k] + self.gamma*ptheta
            print "omega",self.omega[k]
            
            self.M_step(x,k,ptheta)
            self.E_step(k)
            #print "sig:",self.sig[k]
        self.t += 1
        self.gamma /= self.t

    def M_step(self,x,k,ptheta):
        # 十分統計量の算出
        ## 正規分布の十分統計量：Σx
        self.sx0[k] = (1-self.gamma)*self.sx0[k] + self.gamma*ptheta
        self.sx1[k] = (1-self.gamma)*self.sx1[k] + self.gamma*x*ptheta
        ## 正規分布の十分統計量：Σx^2
        self.sx2[k] = (1-self.gamma)*self.sx2[k] + self.gamma*x.dot(x.reshape((len(x),1)))*ptheta 
        
    def E_step(self,k):
        self.mu[k] = self.sx1[k]/self.sx0[k]
        self.sig[k] = self.sx2[k]/self.sx0[k] - self.mu[k].dot( self.mu[k].reshape((len(self.mu[k]),1)) )

    def get_param(self):
        return self.omega, self.mu, self.sig

class Test:
    eps = 10e-6
    
    def __init__(self, cluster_num):
        self.clust = []
        self.cluster_num = cluster_num
    
    def get_cluster(self):
        return self.clust
    
    def test(self,omega,x,mu,sig):
        s_prob = sum([omega[k]*self.mv_norm(x,mu[k],sig[k]) for k in xrange(self.cluster_num)])
        self.clust.append( self.caluc_clust(omega,x,mu,sig,s_prob) )        

    def caluc_clust(self,omega,x,mu,sig,s_prob):
        maxp = -1000
        max_k = -1000
        for k in xrange(self.cluster_num):
            prob = omega[k]*self.mv_norm(x,mu[k],sig[k])/s_prob
            if prob > maxp:
                max_k = k
                maxp = prob
        return max_k

    def mv_norm(self, x, mu, sig):
        det_sig = float(1.0)
        for i in xrange(len(sig)):
            det_sig *= sig[i]

        norm1 = (float(1)+self.eps) / ( pow(2*pi, 0.5*len(x)) * pow(det_sig, 0.5) + self.eps )
        x_mu = x - mu
        norm2 = np.exp( -0.5 * np.power(sig,-1).dot(x_mu*x_mu) )
        norm1 = norm1 if norm1!=0 else self.eps
        norm2 = norm2 if norm2!=0 else self.eps
        return float(1.0) if isinf(norm1) or isinf(norm2) else float(norm1 * norm2)

if __name__ == '__main__':
    featdim = 50
    clustdim = 3
    row_size = 1000
    
    data = generate_data(featdim,row_size)
    np.random.shuffle( data )

    em = OnlineEM(clustdim,featdim)
     
    # doing online EM
    [ em.EMstep(x[1:]) for x in data for _ in xrange(2) ] # number of iteration multiply instance number.
          
    # get parameters          
    omega, mu, sig = em.get_param()
    print mu
    print sig
    print omega
    
    test = Test(clustdim)
    for x in data:    
        test.test(omega, x[1:], mu, sig)
        #print clus
    clus = test.get_cluster()
    
    of = open('test.csv','w')
    for i in xrange(len(clus)):
        flag = '1' if data[i,0]==clus[i] else '0'
        of.write(str(data[i,0])+','+str(clus[i])+','+flag+'\n')