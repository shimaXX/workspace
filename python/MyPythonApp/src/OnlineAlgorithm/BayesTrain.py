# coding: utf-8
'''
Created on 2013/11/11

@author: RN-017
'''
import numpy as np
import math

class BF(object):
    def __init__(self, fname, feat_dim):
        self.fname = fname # input file name
        self.feat_dim = 2**feat_dim # max size of feature vector 
        self.bitmask = 2**feat_dim - 1 # mapping dimension
        self.t = 1 # update times
        self.t_select = 1 # times of�@select sample
        self.epsilon = 10**(-9)
                
        self.N=0.0 # 事例の数の総数
        self.Ny = np.zeros(2, dtype=np.float64) # y=-1, y=1のホルダー（総和のカウント）
        self.Nxy = np.zeros((2,2**feat_dim), dtype=np.float64) # yとxベクトルの組み合わせの出現数の総和
                
        self.propy = None
        self.propxy = None
                
    def train(self):
        with open(self.fname,'r') as trainf:
            for line in trainf:
                y = line.strip().split(' ')[0]
                self.features = self.get_features(line.strip().split(' ')[1:])
                #y = int(-1) if int(y)<=0 else int(1)
                y = int(-1) if int(y)<=1 else int(1)  # posi=1, nega=-1にといういつする
                # 事例数をカウント
                self.N += 1
                
                # yの数をカウントする
                self.incliment_y(y)
                
                # xとyの組み合わせ数のカウント
                self.incliment_xy(y)
                
            # 予測に使用する確率値の算出
            self.propy = np.log(self.pred_y()+self.epsilon)
            self.propxy = np.log(self.pred_xy()+self.epsilon)
            
            for i in xrange(len(self.propy)):
                print self.propxy[i]
                
#        return self.propy, self.propxy 

    def test(self, ifname):
        with open(ifname,'r') as testf:
            ans = np.zeros(4,dtype=np.int64)
            for line in testf:
                y = line.strip().split(' ')[0]
                features = self.get_features(line.strip().split(' ')[1:])
                #y = int(-1) if int(y)<=0 else int(1)
                y = int(-1) if int(y)<=1 else int(1)  # posi=1, nega=-1にといういつする
                
                res = self.test_pred(features)
                
                # 結果の表の計算
                ans = self.get_ans(ans, y, res)
            print ans
            
    def get_features(self,data):
        features = np.zeros(self.feat_dim)
        for kv in data:
            k, v = kv.strip().split(':')
            features[int(k)&self.bitmask] += float(v)
        return features
        
    def incliment_y(self,y):
        if y==-1: self.Ny[0] += 1.0
        else: self.Ny[1] += 1.0  
        
    def incliment_xy(self,y):
        if y==-1:
            self.Nxy[0] += (self.features!=0)*1.0
        else:        
            self.Nxy[1] += (self.features!=0)*1.0
        
    def test_pred(self,features):
        res = np.zeros(2,dtype=np.float64)
        for i in xrange(len(self.Ny)):
            res[i] = self.propy[i] \
                    + sum( self.propxy[i]*((features!=0)*1.0) )
        if res[0]>res[1]:
            return -1
        else:
            return 1
        
    def predict(self):
        res = np.zeros(2,dtype=np.float64)
        predy = np.log(self.pred_y()) # yの確率値の算出
        predx = np.log(self.predxy()) # yの条件付きxの確率値の算出

        res = np.zeros(2,dtype=np.float64)
        for i in xrange(len(self.Ny)):
            res[i] = predy[i]+sum(predx[i])
        if res[0]>res[1]:
            return -1
        else:
            return 1
    
    def pred_y(self):
        return self.Ny/self.N
        
    def pred_xy(self):
        res = np.zeros((2,self.feat_dim),dtype=np.float64)
        for i in xrange(len(self.Ny)):
            if self.Ny[i]==0.0:
                res[i] = 0.0
            else:
                res[i] = self.Nxy[i]/self.Ny[i]
        return res
                    
    def get_ans(self,ans,y,res):
        if y==1 and res==1: # 真陽性
            ans[0] += 1
        elif y==1 and res==-1: # 偽陽性
            ans[1] += 1
        elif y==-1 and res==1: # 偽陰性
            ans[2] += 1
        else: # 真陰性
            ans[3] += 1
            
        return ans

    """
    def save_model(self,ofname,w):
        with open(ofname,'w') as f:            
            py = [str(p).encode('utf-8') for p in self.propy]
            f.write(' '.join(weight)+'\n')
            
            f.write(str(self.feat_dim).encode('utf-8'))
    """

if __name__=='__main__':
    trfname = 'C:/workspace/HadoopPig/HadoopPig/works/input/train_cov' #webspam_wc_normalized_trigram, kddb, covtype.libsvm.binary, splice, train_cov
    tefname = 'C:/workspace/HadoopPig/HadoopPig/works/input/test_cov'

    bf = BF(trfname, 6)
    bf.train()
    bf.test(tefname)