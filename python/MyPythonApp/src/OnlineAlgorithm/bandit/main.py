# coding: utf-8
'''
Created on 2014/01/09

@author: RN-017
'''
import Judge
import DataGenerator


if __name__=='__main__':
    contents_num = 2
    event_num = 10000
    judge = Judge.judge(contents_num,event_num)
    
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