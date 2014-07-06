# coding: utf-8
'''
Created on 2013/11/11

@author: RN-017
'''
import numpy as np
import math

class sgd_bin_train(object):
    def __init__(self, fname, feat_dim, loss_type):
        self.fname = fname # input file name
        self.weight = None # features weight
        self.feat_dim = 2**feat_dim # max size of feature vector 
        self.bitmask = 2**feat_dim - 1 # mapping dimension
        self.loss_type = loss_type # type of loss function

        self.eta = 10.0 # learning rate
        self.features = None
        self.G = np.zeros(self.feat_dim, dtype=np.float64)
        self.t = 1 # update times

        self.epsilon = 10**(-9)

        self.maxfeature = np.zeros(self.feat_dim, dtype=np.float64)
        self.N = 0
        
    def train(self,gamma,lambd):
        self.gamma = gamma
        self.lambd = lambd
        self.initialize()
        with open(self.fname,'r') as trainf:
            for line in trainf:
                #if self.t>=15: break
                y = line.strip().split(' ')[0]
                self.features = self.get_features(line.strip().split(' ')[1:])
                #y = int(-1) if int(y)<=0 else int(1)  # posi=1, nega=-1にといういつする
                y = int(-1) if int(y)<=1 else int(1)  # posi=1, nega=-1にといういつする
                
                # 数値の予測
                pred = self.predict(self.weight,self.features)                

                # weightの正規化
                self.NAG(y,y*pred) #self.NG(y,y*pred)
                                
                self.t += 1
        print self.weight
        return self.weight
    
    def initialize(self):
        self.weight = np.zeros(self.feat_dim,dtype=np.float64)
        
    def get_features(self,data):
        features = np.zeros(self.feat_dim,dtype=np.float64)
        for kv in data:
            k, v = kv.strip().split(':')
            features[int(k)&self.bitmask] += float(v)
        return features
        
    def NG(self,y,m):
        """ weightの正規化 """
        idx = np.where( (np.abs(self.features)-self.maxfeature)>0 )
        
        # weightの調整を行う
        self.weight[idx] *= self.maxfeature[idx]**2/(np.abs(self.features[idx])+self.epsilon)**2
        
        # max値の更新
        self.maxfeature[idx] = np.abs( self.features[idx] )
        
        # 係数の更新
        self.N += sum(self.features**2/(self.maxfeature+self.epsilon)**2)

        # weightの更新
        loss = self.calc_loss(m)
        if loss>0.0:
            grad = y*self.calc_dloss(m)*self.features
            self.weight -= self.eta*self.t/self.N*1/(self.maxfeature+self.epsilon)**2*grad

    def NAG(self,y,m):
        """ weightの正規化 """
        idx = np.where( (np.abs(self.features)-self.maxfeature)>0 )
        
        # weightの調整を行う
        self.weight[idx] *= self.maxfeature[idx]/(np.abs(self.features[idx])+self.epsilon)
        
        # max値の更新
        self.maxfeature[idx] = np.abs( self.features[idx] )
        
        # 係数の更新
        self.N += sum(self.features**2/(self.maxfeature+self.epsilon)**2)
        
        # weightの勾配の計算
        grad = y*self.calc_dloss(m)*self.features
        self.G += grad**2
        self.weight -= self.eta*math.sqrt(self.t/self.N)* \
                        1/(self.maxfeature+self.epsilon)/np.sqrt(self.G+self.epsilon)*grad
        """
        # weightの更新
        loss = self.calc_loss(m)

        if loss>0.0:
            # weightの勾配の計算
            grad = y*self.calc_dloss(m)*self.features
            self.G += grad**2
            self.weight -= self.eta*math.sqrt(self.t/self.N)* \
                            1/(self.maxfeature+self.epsilon)/np.sqrt(self.G+self.epsilon)*grad
        """

    def sNAG(self,y,m):
        """ weightの正規化 """
        idx = np.where( (np.abs(self.features)-self.maxfeature)>0 )

        s = np.sqrt( self.maxfeature/self.t )
        # weightの調整を行う
        #self.weight[idx] *= s[idx]/( np.abs(self.features[idx])+self.epsilon )
        self.weight *= s/( np.abs(self.features)+self.epsilon )
        
        # max値の更新
        #self.maxfeature[idx] += self.features[idx]**2
        self.maxfeature += self.features**2
        s = np.sqrt(self.maxfeature/self.t)
        
        # 係数の更新
        self.N += sum(self.features**2/(s+self.epsilon)**2)
        
        # weightの更新
        loss = self.calc_loss(m)
        if loss>0.0:
            # weightの勾配の計算
            grad = y*self.calc_dloss(m)*self.features
            self.G += grad**2
            self.weight -= self.eta*math.sqrt(self.t/self.N)* \
                            1/(s+self.epsilon)/np.sqrt(self.G+self.epsilon)*grad

    def predict(self,w,features):
        ez = np.dot(w,features)
        #return 1/(1+math.exp(-ez)) #logistic関数にはかけない
        return ez
        
    def calc_loss(self,m): # m=py=wxy
        if self.loss_type == 'hinge':
            return max(0,1-m)          
        elif self.loss_type == 'log':
            if m<=-700: m=-700
            return math.log(1+math.exp(-m))
    
    # gradient of loss function
    def calc_dloss(self,m): # m=py=wxy
        if self.loss_type == 'hinge':
            res = -1.0 if (1-m)>0 else 0.0 # lossが0を超えていなければloss=0.そうでなければ-mの微分で-1になる
            return res
        elif self.loss_type == 'log':
            if m < 0.0:
                return float(-1.0) / (math.exp(m) + 1.0) # yx-e^(-m)/(1+e^(-m))*yx
            else:
                ez = float( math.exp(-m) )
                return -ez / (ez + 1.0) # -yx+1/(1+e^(-m))*yx
    
    def update_weight(self,y,m):
        """ weightの更新（正規化の後に行う）
        lossによる場合分けは行わなくて良いのか？ 
        """
        loss = self.calc_loss(m)
        if loss>0.0:
            grad = y*self.calc_dloss(m)*self.features
            self.weight -= self.eta*self.t/self.N*1/(self.maxfeature+self.epsilon)**2*grad

    def save_model(self,ofname,w):
        with open(ofname,'w') as f:
            # loss関数のtypeの書き込み
            f.write(self.loss_type+'\n')
            
            # weightの書き込み
            weight = [str(x).encode('utf-8') for x in w]
            f.write(' '.join(weight)+'\n')
            
            # 特徴量の次元の書き込み
            f.write(str(self.feat_dim).encode('utf-8'))