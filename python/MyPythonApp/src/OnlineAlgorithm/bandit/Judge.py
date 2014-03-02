# coding: utf-8
'''
Created on 2014/01/07

@author: RN-017
'''

import numpy as np

import LinUCBArm
import DataGenerator


class judge:
    def __init__(self,contents_num,event_num):
        self.contents_num = contents_num
        self.event_num = event_num
    
    def get_arms(self,featdim):
        arms = []
        for i in xrange(self.contents_num):
            arms.append(LinUCBArm.Arm(i,0.5,featdim))
        return arms

    def simulate(self,arms):
        # data発生オブジェクト
        dgen = DataGenerator.DataGen(0)

        select_arm = [0,0]
        for _ in xrange(self.event_num):
            features = dgen.generate_line()
            pred = np.zeros(self.contents_num)
            for i in xrange( len(arms) ):
                pred[i] = arms[i].calculate_prediction(features)
            print 'pred=',pred
            idx = np.where(pred==max(pred)) # 確率の高い方の腕を取得
            print "feauturs=",features
            print "arm=",idx[0][0]
            arms[idx[0][0]].update_param(features)
            
            if idx[0][0]==0: select_arm[0] +=1
            else: select_arm[1] +=1
        return arms, select_arm
    
if __name__=='__main__':
    contents_num = 2
    event_num = 10000
    judge = judge(contents_num,event_num)
    
    # data発生オブジェクト
    dgen = DataGenerator.DataGen(0)
    try:
        featdim = len(dgen.generate_line())
    except:    
        featdim = 1
    
    # armの取得
    arms = judge.get_arms(featdim)
    
    # シミュレーション
    arms, select_arm = judge.simulate(arms)

    # 結果の表示
    for i in xrange(len(arms)):
        print 'arm%d = %f' % (i,arms[i].get_r()/select_arm[i]) # arm0=0.1, arm1=0.05になるはず