# coding: utf-8
'''
Created on 2013/11/11

@author: RN-017
'''
import numpy as np
import math
from scipy.stats import norm

sigmaf = 'C:/workspace/python/MyPython/works/output/sigma_res'

class scw_bin_train(object):
    def __init__(self, fname, feat_dim, loss_type, eta, C):
        self.fname = fname # input file name
        self.feat_dim = 2**feat_dim # max size of feature vector 
        self.bitmask = 2**feat_dim - 1 # mapping dimension
        self.loss_type = loss_type # type of loss function
        self.lambd = None # regularization
        self.gamma = None # learning rate
        self.t = 1 # update times
        self.features = np.zeros(self.feat_dim,dtype=np.float64)
        self.mean_weight = np.zeros(self.feat_dim,dtype=np.float64)
        self.sigma_weight = np.eye(self.feat_dim,dtype=np.float64)
        self.alpha = 0
        self.beta = 0
        self.sai = None
        self.pusai = None
        self.u = None
        self.v = None
        self.eta = eta
        self.phai = float( norm.cdf(eta)**(-1) ) # phaiは固定(?)
        self.C = C
        
    def train(self):
        with open(self.fname,'r') as trainf:
            for line in trainf:
                y = line.strip().split(' ')[0]
                features = line.strip().split(' ')[1:]
                y = int(-1) if int(y)<=0 else int(1)  # posi=1, nega=-1�ɂƂ���������
                #y = int(-1) if int(y)<=1 else int(1)  # posi=1, nega=-1�ɂƂ���������
                
                # yの予測
                pred = self.predict(self.mean_weight,features)
                
                # vtの計算
                vt = self.calc_v()
                
                if self.calc_loss(y)>0:
                    # update weight
                    self.update_param(y,y*pred,vt)
                    """
                    with open(sigmaf, 'a') as f:
                        num = [str(x).encode('utf-8') for x in self.sigma_weight]
                        f.write(' '.join(num)+'\n') 
                    """                    
        print self.mean_weight
        return self.mean_weight
    
    def initialize(self):
        w_init = np.zeros(self.feat_dim, dtype=np.float64)
        return w_init

    def update_param(self,y,m,v):
#         teta = 1.0+self.phai**2
#         sai = 1.0+0.5*self.phai**2
        nt = v+float(0.5)/self.C
        gmt = self.phai*math.sqrt( (self.phai*m*v)**2+4.0*nt*v*(nt+v*self.phai**2) )

        #self.alpha = max(0 , 1/v*teta*(-m*sai + (m**2 * self.phai**4 + v*self.phai**2*teta)**0.5 ))
        self.alpha = max( 0.0 , (-(2.0*m*nt+self.phai**2*m*v)+gmt)/(2.0*(nt**2+nt*v*self.phai**2)) )
        u = 0.25*( -self.alpha*v*self.phai+((self.alpha*v*self.phai)**2 + 4.0*v)**0.5 )**2
        self.beta = self.alpha*self.phai/(u**0.5 + v*self.alpha*self.phai)
        
        self.mean_weight += self.alpha*y*np.dot( self.sigma_weight, self.features )
        self.sigma_weight -= self.beta*np.dot( np.dot( np.dot(self.sigma_weight, self.features), self.features), self.sigma_weight) 
       
        self.t += 1
        
    def predict(self,w,features):
        val = 0.0
        if w != None:
            for feature in features:
                k,v = feature.strip().split(':')
                val += w[int(k) & self.bitmask] * float(v)
                self.features[int(k) & self.bitmask] += float(v)
                #val += w[int(k)-1] * float(v)
                #self.features[int(k)-1] += float(v)
        return val

    def calc_v(self):
        return np.dot( self.features , np.dot(self.sigma_weight, self.features.T) )
        
    def calc_loss(self,y): # m=py=wxy
        """ 損失関数 """
        res = self.phai * math.sqrt( np.dot(self.features , np.dot(self.sigma_weight, self.features.T)) ) \
                - y * np.dot(self.features, self.mean_weight) # sigmaは対角成分のみ保存
        return res              
                      
    def save_model(self,ofname,w):
        with open(ofname,'w') as f:
            # loss�֐���type�̏�������
            f.write(self.loss_type+'\n')
            
            # weight�̏�������
            weight = [str(x).encode('utf-8') for x in w]
            f.write(' '.join(weight)+'\n')
            
            # �����ʂ̎����̏�������
            f.write(str(self.feat_dim).encode('utf-8'))