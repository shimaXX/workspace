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
        self.lambd = None # regularization
        self.gamma = None # learning rate
        self.x = np.zeros(self.feat_dim)
        self.t = 1 # update times
        self.t_select = 1 # times of　select sample
        self.gradbar = np.zeros(self.feat_dim)
        self.grad2bar = np.zeros(self.feat_dim)
        self.tau = np.ones(self.feat_dim)*5 # parameter of updating learning rate 
        self.gbar = np.zeros(self.feat_dim) # parameter of updating learning rate
        self.vbar = np.zeros(self.feat_dim) # parameter of updating learning rate
#        self.l = np.zeros(self.bitmask) # parameter of updating learning rate
        self.hbar = np.zeros(self.feat_dim) # parameter of updating learning rate
        self.epsilon = 10**(-9)
        
        self.loss_weight = 10 # 不均衡率調整用のパラメタ 
        
        ## selective sampler用のパラメタ
        self.alpha=1000 # active samplingのためのパラメタ。大きい値であるほど採用サンプル数が多い
        self.Adiag=np.ones(self.feat_dim) # Aの対角成分
        self.r = np.zeros(self.feat_dim) # xA^(-1)x。Aは対角成分のみ計算
        
        ## weight scaling用のパラメタ
        self.maxfeatures = np.zeros(self.feat_dim, dtype=np.float64)
        self.N = 0
        self.G = np.zeros(self.feat_dim)
        
        self.update_t = 1
        
    def train(self,gamma,lambd):
        self.gamma = gamma
        self.lambd = lambd
        self.initialize()
        with open(self.fname,'r') as trainf:
            for line in trainf:
                #if self.t>=15: break
                y = line.strip().split(' ')[0]
                self.features = self.get_features(line.strip().split(' ')[1:])
                y = int(-1) if int(y)<=0 else int(1)  # posi=1, nega=-1にといういつする
                #y = int(-1) if int(y)<=1 else int(1)  # posi=1, nega=-1にといういつする
                
                # 入力データの正規化
                #self.NG()
                #self.features /= (self.N+self.epsilon)/self.t_select
                
                # 数値の予測
                pred = self.predict(self.weight,self.features)                
                #grad = y*self.calc_dloss(y*pred)*self.features/(self.maxfeatures+self.epsilon)
                grad = y*self.calc_dloss(y*pred)*self.features
                #self.G += grad**2
                #param = math.sqrt(self.t_select/self.N) \
                #            *1/(  np.sqrt( (self.maxfeatures+self.epsilon)/self.t_select )  )
                #param = self.t_select/self.N*1/(self.maxfeatures+self.epsilon)**2

                if True:#self.selective_sampler(pred): # True: # aouto sampling                
                    #self.gradbar = self.gradbar*(self.t-1) + grad
                    #self.gradbar = self.gradbar*(self.t-1) + grad*param
                    #self.gradbar /= self.t
                    self.gradbar = grad
                    
                    #self.grad2bar = self.grad2bar*(self.t-1) + grad**2
                    #self.grad2bar = self.grad2bar*(self.t-1) + (grad*param)**2
                    #self.grad2bar /= self.t
                    self.grad2bar = grad**2
                    
                    # update weight
                    self.update(pred,y)
                    
                    self.t += 1
                self.t_select += 1
        print self.weight
        print self.t_select
        print self.t
        return self.weight
    
    def initialize(self):
        self.weight = np.zeros(self.feat_dim)
        
    def get_features(self,data):
        features = np.zeros(self.feat_dim)
        for kv in data:
            k, v = kv.strip().split(':')
            features[int(k)&self.bitmask] += float(v)
        return features
        
    def predict(self,w,features): #margin
        ez = np.dot(w,features)
        """
        for feature in features:
            k,v = feature.strip().split(':')
            val += w[int(k) & self.bitmask] * float(v)
        """
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
#             ez = float( math.exp(-m) )
#             return -ez / (ez + 1.0) # -yx+1/(1+e^(-m))*yx    

    def update(self, pred, y):
        m = y*pred
        
        self.gbar *= (1 - self.tau**(-1))
        self.gbar += self.tau**(-1)*self.gradbar
        
        self.vbar *= (1 - self.tau**(-1))
        self.vbar += self.tau**(-1)*self.grad2bar + self.epsilon
                
        self.hbar *= (1 - self.tau**(-1))
        self.hbar += self.tau**(-1)*2*self.grad2bar + self.epsilon #

        tmp = self.gbar**2/self.vbar
        
        # update memory size
        self.tau = (1-tmp)*self.tau+1 + self.epsilon
        
        # update learning rate
        eta = tmp/self.hbar
        #eta = np.array([1/self.t]*self.feat_dim)
                
        # update weight
        self.update_weight(y, m, eta)

    def selective_sampler(self, pred):
        r = np.dot(self.Adiag**(-1), self.features**2)
        theta2 = self.alpha*r*math.log(1+self.t_select)
        if theta2 >= pred**2:
            self.Adiag += self.features**2
            return True
        else: 
            return False

    def update_weight(self,y,m,eta):
        loss = self.calc_loss(m)
        if loss>0.0: # paの場合
#           alpha = self.loss_weight if y==1 else 1
            delta = self.calc_dloss(m)*self.features
            #delta = self.calc_dloss(m)*self.features/(self.maxfeatures+self.epsilon)
            #self.weight -= alpha*eta*y*delta
            self.weight -= eta*y*delta
            #self.weight -= eta*self.t_select/self.N*1/(self.maxfeatures+self.epsilon)**2*delta
            #self.weight -= eta*1/(self.maxfeatures+self.epsilon)*delta
            self.update_t += 1
            """
            self.weight -= eta*math.sqrt(self.t_select/self.N)* \
                                1/(  np.sqrt( (self.maxfeatures+self.epsilon)/self.t_select ) *  (self.G+self.epsilon))* \
                                y*delta
            """

    def NG(self):
        """ weightの正規化 """

        idx = np.where( (np.abs(self.features)-self.maxfeatures)>0 )
        
        # weightの調整を行う
        self.weight[idx] *= self.maxfeatures[idx]**2/(np.abs(self.features[idx])+self.epsilon)**2
        
        # max値の更新
        self.maxfeatures[idx] = np.abs( self.features[idx] )

        
        #self.maxfeatures = self.maxfeatures*(self.t_select-1)+self.features
        #self.maxfeatures /= self.t_select
        
        #self.weight *= self.maxfeatures**2/(np.abs(self.features)+self.epsilon)**2
        
        # 係数の更新
        self.N += sum(self.features**2/(self.maxfeatures+self.epsilon)**2)


    def sNAG(self):
        """ weightの正規化 """
        #idx = np.where( (np.abs(self.features)-self.maxfeature)>0 )

        s = np.sqrt( self.maxfeatures/self.t_select )
        # weightの調整を行う
        #self.weight[idx] *= s[idx]/( np.abs(self.features[idx])+self.epsilon )
        self.weight *= s/( np.abs(self.features)+self.epsilon )
        
        # max値の更新
        #self.maxfeature[idx] += self.features[idx]**2
        self.maxfeatures += self.features**2
        s = np.sqrt(self.maxfeatures/self.t_select)
        
        # 係数の更新
        self.N += sum(self.features**2/(s+self.epsilon)**2)        
        
    def scale_weight_array(self):
        #self.weight = self.
        return

    def update_hessian(self):
        
        """
        def _df(self, xs): # grad
            tmp = xs + self._noise(xs.shape)
            return tmp * (exp(-tmp ** 2 / 2)) * self.curvature   
            
        def _ddf(self, xs): # hessian
            tmp = xs + self._noise(xs.shape)
            return (1 - tmp ** 2) * exp(-tmp ** 2 / 2) * self.curvature  
    
        def expectedLoss(self, xs): loss
            a = 1. / sqrt(self.noiseLevel ** 2 + 1)
            return(1 - exp(-xs ** 2 / 2 * (a ** 2)) * a) * self.curvature   
        """
        return

    def save_model(self,ofname,w):
        with open(ofname,'w') as f:
            # loss関数のtypeの書き込み
            f.write(self.loss_type+'\n')
            
            # weightの書き込み
            weight = [str(x).encode('utf-8') for x in w]
            f.write(' '.join(weight)+'\n')
            
            # 特徴量の次元の書き込み
            f.write(str(self.feat_dim).encode('utf-8'))