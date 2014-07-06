# coding: utf-8
'''
Created on 2013/11/12

@author: RN-017
'''
import math
import numpy as np

class SCW_Test(object):
    def __init__(self, model_fname, testdata_fname):
        self.modelfile = model_fname
        self.testdata_fname = testdata_fname 
        self.type = None
        self.ans = np.zeros(4)
    
    def test(self):
        """
        Do test by trained model
        """
        # trained modelの情報取得
        self.type, w, feat_dim = self.read_model()
        bitmask = feat_dim - 1
        w = np.array(w,dtype=np.float64)
        
        with open(self.testdata_fname,'r') as testf:
            predict = []
            ans = np.zeros(4)     
            for line in testf:
                
                y = line.strip().split(' ')[0]
                data = line.strip().split(' ')[1:]

                y = -1 if int(y)<=0 else 1  # posi=1, nega=-1にといういつする
                #y = -1 if int(y)<=1 else 1  # posi=1, nega=-1にといういつする

                m = 0.0
                for kv in data: # 推定量の算出
                    k, v = kv.strip().split(':')
                    m += self.calc_iter_result(w,int(k),float(v),bitmask)
                res = self.calc_result(m)
                ans = self.get_table(y, res)
                predict.append(res)
        print predict
        return predict, ans
    
    def read_model(self):
        w=None; type=None; feat_dim=None
        with open(self.modelfile,'r') as modelf:
            cnt = 0
            for line in modelf:
                if cnt==0:
                    type = line.strip().split(' ')
                elif cnt==1:
                    w = line.strip().split(' ')
                elif cnt==2:
                    feat_dim = line.strip().split(' ')
                cnt += 1
        return type[0], w, int(feat_dim[0]) 
   
    def calc_iter_result(self,w,k,x,bitmask):
        if self.type=='log':
            return w[k&bitmask]*x
        elif self.type=='hinge':
            return w[k&bitmask]*x
            #return w[k-1]*x
            
    def calc_result(self, m):
        if self.type=='log':
            if m<-700: m=-700
            return 1/(1+math.exp(-m))
        elif self.type=='hinge':
            return 1 if m>=0.0 else -1 
        
    def get_table(self,y,res):
        """
                 正確性、再現性などのチェックのために4分割表を作成
        """        
        # log-lossの場合は0.5を閾値とする
        if self.type=='log':
            res = 1 if res>0.5 else -1
         
        if y==1 and res==1:
            self.ans[0] += 1 
        elif y==1 and res==-1:
            self.ans[1] += 1
        elif y==-1 and res==1:
            self.ans[2] += 1
        elif y==-1 and res==-1:
            self.ans[3] += 1
        return self.ans
    
    def save_result(self,ofname,predict, ans):
#        print predict
        with open(ofname,'w') as f:
            pred = [str(x).encode('utf-8') for x in predict]
            f.write(','.join(pred)+'\n\n')
            
            a = [str(x).encode('utf-8') for x in ans]
            f.write(','.join(a))