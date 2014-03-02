# coding: utf8

import numpy as np
import scipy as sp
import math
from scipy import linalg as sln
from scipy.sparse import linalg as sprsln
from svm import *
from svmutil import *

import matplotlib.pyplot as plt
from scipy.cluster.vq import vq, kmeans, kmeans2, whiten
#from sklearn import linear_model as sklm
from pylab import *
import random


imp_num = 3000 #データ発生数
usr_num = 100 # user数
nnk = 5 # knnのご近所さんの数

np.random.seed(55)

def create_data():
    adinfo = np.zeros((imp_num,1048)) #クリエイティブIDは外して1148に減少させる
    mediainfo = np.zeros((imp_num, 1200))
    usrinfo = np.zeros((usr_num,1002))
    deviceinfo = np.zeros((imp_num,7))
    timeinfo = np.zeros((imp_num,1))
    
#     #adID data
#     adid_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*1000) 
#     for i in xrange(imp_num):
#         adinfo[i,int(adid_idx[i])] = 1
    
#     #adnetworkID data    
#     adntw_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*100) 
#     for i in xrange(imp_num):
#         adinfo[i,int(adntw_idx[i])] = 1

    #campaignID data    
    adcmpgn_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*20) 
    for i in xrange(imp_num):
        adinfo[i,int(adcmpgn_idx[i])] = 1
        
    #creative type data    
    adcr_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*3) 
    for i in xrange(imp_num):
        adinfo[i,20+int(adcr_idx[i])] = 1

    #creative category data    
    #adctgry_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*1000)
    adctgry_idx = np.array( [ np.floor(np.random.uniform(0, 1, size=1)[0]*adcmpgn_idx[i]*50)
                              for i in xrange(imp_num) ] ) 
    for i in xrange(imp_num):
        adinfo[i,23+int(adctgry_idx[i])] = 1
        
    #creative size data    
    adcrsz_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*15) 
    for i in xrange(imp_num):
        adinfo[i,1023+int(adcrsz_idx[i])] = 1

    #creative position data    
    adcrps_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*10) 
    for i in xrange(imp_num):
        adinfo[i,1038+int(adcrps_idx[i])] = 1

    ##ここからuser情報
    #interest category data. 4week内で訪問したサイトのカテゴリ頻度
    usr_ctg_idx = np.floor(np.random.uniform(0, 1, size=usr_num)*1000) #ユーザの興味のあるカテゴリ
    usrinfo[:,0:1000] = np.floor( np.array(
                            [
                                np.array([np.random.uniform(0,1,size=1)*500 
                                 if i-20<=usr_ctg_idx[j]<=i+20 else np.random.uniform(0,1,size=1)*10
                                 for i in xrange(1000)]).flatten()
                             for j in xrange(usr_num)]
                        ))
    rec = np.random.uniform(0,1,size=usr_num)*15
    usrinfo[:, 1000:1001] = rec.reshape((usr_num, 1))
    frec = np.random.uniform(0,1,size=usr_num)*7
    usrinfo[:, 1001:1002] = frec.reshape((usr_num, 1))
    
    ##ここからdevice情報
    #device data
    dvc_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*2)
    for i in xrange(imp_num):
        deviceinfo[i,int(dvc_idx[i])] = 1

    #os data
    os_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*5)
    for i in xrange(imp_num):
        deviceinfo[i,2+int(os_idx[i])] = 1

    ##ここから広告提示時間のデータ
    #time data
    timeinfo = np.floor(np.random.uniform(0, 1, size=imp_num)*24)
#     time_idx = np.floor(np.random.uniform(0, 1, size=imp_num)*24)
#     for i in xrange(imp_num):
#         timeinfo[i,int(time_idx[i])] = 1
    
    ##各広告にどのユーザが現れるか
    imp_usr = np.floor(np.random.uniform(0, 1, size=imp_num)*usr_num)
    
    #CV条件
    ct = []
    ct_crt = np.zeros((imp_num, 5))
    for i in xrange(imp_usr.shape[0]):
        if usr_ctg_idx[imp_usr[i]]-20 <= adctgry_idx[i] <= usr_ctg_idx[imp_usr[i]]+20 \
                 and adcrps_idx[i]<6 and usrinfo[imp_usr[i],1001] < 5 and \
                 adcmpgn_idx[i] < 10 and adcrsz_idx[i] < 10:
            ct.append(1)
        #elif np.random.uniform(0, 1, size=1) > 0.95: ct.append(1)
        else: ct.append(0)
        
        ct_crt[i,0] = usr_ctg_idx[imp_usr[i]]
        ct_crt[i,1] = adctgry_idx[i]
        ct_crt[i,2] = timeinfo[i]
        ct_crt[i,3] = adcrps_idx[i]
        ct_crt[i,4] = ct[i]
    ct = np.array(ct)
    
    return adinfo, usrinfo, deviceinfo, timeinfo, imp_usr, ct, ct_crt, usr_ctg_idx

def draw(data, label):
    # 訓練データを描画
    N = len(data)
    
    color = ['r', 'b', 'g', 'c', 'm', 'y', 'k', 'w']  # K < 8と想定
    for n in xrange(N):
        scatter(data[n,0], data[n,1], c=color[label[n]], marker='o')
    
#    # クラスタの平均を描画
#    for k in xrange(K):
#        scatter(mean[k, 0], mean[k, 1], s=120, c='y', marker='s')
    
    xlim(-2.5, 2.5)
    ylim(-2.5, 2.5)
    show()

def get_data():
    data =np.loadtxt('c:/workspace/python/Mypython/works/input/testdata.txt', delimiter='\t')
#    with open('C:/workspace/python/Mypython/works/input/testdata.txt' ,'r') as f:
    cv = data[:, len(data[0,:])-1]
    info = data[:, :len(data[0,:])-1]

    return cv, info

def get_testdata():
    data =np.loadtxt('c:/workspace/python/Mypython/works/input/testset.txt', delimiter='\t')
#    with open('C:/workspace/python/Mypython/works/input/testdata.txt' ,'r') as f:
    cv = data[:, len(data[0,:])-1]
    info = data[:, :len(data[0,:])-1]

    return cv, info
    
class SMOTE(object):
    def __init__(self, N):
        self.N = N
        self.T = 0
    
    def oversampling(self, smp, cv):
        mino_idx = np.where(cv==1)[0]
        mino_smp = smp[mino_idx,:]
        
        # kNNの実施
        mino_nn = []
        
        for idx in mino_idx:
            near_dist = np.array([])
            near_idx = np.zeros(nnk)
            for i in xrange(len(smp)):
                if idx != i:
                    dist = self.dist(smp[idx,:], smp[i,:])
                    
                    if len(near_dist)<nnk: # 想定ご近所さん数まで到達していなければ問答無用でlistに追加
                        tmp = near_dist.tolist()
                        tmp.append(dist)
                        near_dist = np.array(tmp)
                    elif sum(near_dist[near_dist > dist])>0:
                        near_dist[near_dist==near_dist.max()] = dist
                        near_idx[near_dist==near_dist.max()] = i
            mino_nn.append(near_idx)
        return self.create_synth( smp, mino_smp, np.array(mino_nn, dtype=np.int) )

    def dist(self, smp_1, smp_2):
        return np.sqrt( np.sum((smp_1 - smp_2)**2) )
                    
    def create_synth(self, smp, mino_smp, mino_nn):
        self.T = len(mino_smp)
        if self.N < 100:
            self.T = int(self.N*0.01*len(mino_smp))
            self.N = 100
        self.N = int(self.N*0.01)
        
        rs = np.floor( np.random.uniform(size=self.T)*len(mino_smp) )
        
        synth = []
        for n in xrange(self.N):
            for i in rs:
                nn = int(np.random.uniform(size=1)[0]*nnk)
                dif = smp[mino_nn[i,nn],:] - mino_smp[i,:]
                gap = np.random.uniform(size=len(mino_smp[0]))
                tmp = mino_smp[i,:] + np.floor(gap*dif)
                tmp[tmp<0]=0
                synth.append(tmp)
        return synth    

def undersampling(imp_info, cv, m):
    # minority data
    minodata = imp_info[np.where(cv==1)[0]]
    
    # majority data
    majodata = imp_info[np.where(cv==0)[0]]

    # kmeans2でクラスタリング
    whitened = whiten(imp_info) # 正規化（各軸の分散を一致させる）
#    whitened = majodata
    centroid, label = kmeans2(whitened, k=3) # kmeans2
    C1 = []; C2 = []; C3 = []; # クラスタ保存用
    C1_cv = []; C2_cv = []; C3_cv = [] 
    for i in xrange(len(imp_info)):
        if label[i] == 0:
            C1 += [whitened[i]]
            C1_cv.append(cv[i])
        elif label[i] == 1:
            C2 += [whitened[i]]
            C2_cv.append(cv[i])
        elif label[i] == 2:
            C3 += [whitened[i]]
            C3_cv.append(cv[i])
    
    # numpy形式の方が扱いやすいため変換
    C1 = np.array(C1); C2 = np.array(C2); C3 = np.array(C3) 
    C1_cv = np.array(C1_cv); C2_cv = np.array(C2_cv); C3_cv = np.array(C3_cv);
    
    # 各クラスの少数派データの数
    C1_Nmajo = sum(1*(C1_cv==0)); C2_Nmajo = sum(1*(C2_cv==0)); C3_Nmajo = sum(1*(C3_cv==0)) 
    
    # 各クラスの多数派データの数
    C1_Nmino = sum(1*(C1_cv==1)); C2_Nmino = sum(1*(C2_cv==1)); C3_Nmino = sum(1*(C3_cv==1))
    t_Nmino = C1_Nmino + C2_Nmino + C3_Nmino

    # 分母に0が出る可能性があるので1をプラスしておく
    C1_MAperMI = float(C1_Nmajo)/(C1_Nmino+1); C2_MAperMI = float(C2_Nmajo)/(C2_Nmino+1); C3_MAperMI = float(C3_Nmajo)/(C3_Nmino+1);
    
    t_MAperMI = C1_MAperMI + C2_MAperMI + C3_MAperMI
    
    under_C1_Nmajo = int(m*t_Nmino*C1_MAperMI/t_MAperMI)
    under_C2_Nmajo = int(m*t_Nmino*C2_MAperMI/t_MAperMI)
    under_C3_Nmajo = int(m*t_Nmino*C3_MAperMI/t_MAperMI)
    t_under_Nmajo = under_C1_Nmajo + under_C2_Nmajo + under_C3_Nmajo

#    draw(majodata, label)
    
    # 各グループで多数派と少数派が同数になるようにデータを削除
    C1 = C1[np.where(C1_cv==0),:][0]
    random.shuffle(C1)
    C1 = np.array(C1)
    C1 = C1[:under_C1_Nmajo,:]
    C2 = C2[np.where(C2_cv==0),:][0]
    random.shuffle(C2)
    C2 = np.array(C2)
    C2 = C2[:under_C2_Nmajo,:]
    C3 = C3[np.where(C3_cv==0),:][0]
    random.shuffle(C3)
    C3 = np.array(C3)
    C3 = C3[:under_C3_Nmajo,:]
    
#     cv1_0 = np.zeros(len(C1)); cv1_1 = np.ones(len(minodata))
#     cv2_0 = np.zeros(len(C2)); cv2_1 = np.ones(len(minodata))
#     cv3_0 = np.zeros(len(C3)); cv3_1 = np.ones(len(minodata))

    cv_0 = np.zeros(t_under_Nmajo); cv_1 = np.ones(len(minodata))
#     cv1 = np.hstack((cv1_0, cv1_1))
#     cv2 = np.hstack((cv2_0, cv2_1))
#     cv3 = np.hstack((cv3_0, cv3_1))
    cv_d = np.hstack((cv_0, cv_1))
    
#     C1 = np.vstack((C1, minodata))
#     C2 = np.vstack((C2, minodata))
#     C3 = np.vstack((C3, minodata))    
    print C1.shape, C2.shape, C3.shape, minodata.shape

    info = np.vstack((C1, C2, C3, minodata))
    
    return cv_d, info


def random_sampl(imp_info, cv):
    m=0.3
    # 単純にminorityをランダムサンプリングした場合
    # minority data
    minodata = imp_info[np.where(cv==1)[0]]
    cv_mino = cv[cv==1]
    
    # majority data
    majodata = imp_info[np.where(cv==0)[0]]
    cv_majo = cv[cv==0]

    # minority dataのランダムサンプリング
    majo_rnd = np.floor( np.random.uniform(size=len(majodata)*m)*len(majodata) )
    majo_rnd = np.array(majo_rnd, dtype=np.int)
    majo = majodata[majo_rnd, :]
    cv_majo = cv_majo[majo_rnd]
    
    info = np.vstack((majo, minodata))
    cv = np.hstack((cv_majo, cv_mino))
    
    return info, cv

if __name__=='__main__':
    ad, usr, dvc, time, imp_usr, cv, cv_crt, usr_ctg = create_data()

    imp_info = np.array(
                [ np.hstack( (ad[i,:], usr[imp_usr[i],:], dvc[i,:], time[i]) )
                  for i in xrange(len(imp_usr)) ]
                )

    # positive dataのover-sampling
    
    smote = SMOTE(200)
    synth = smote.oversampling(imp_info, cv) # psの増幅分

    # 増幅分のマージ
    imp_info = np.vstack((imp_info, synth))
    cv = np.hstack( (cv, np.ones(len(synth))) )
    

    # ad行列の圧縮
    U, S, Vh = sln.svd(imp_info)
#    imp_info = np.dot(imp_info, Vh[:, :1000])
    imp_info = np.dot(imp_info, Vh[:, :700])    

    """
    # under-sampling
    cv_d, info = undersampling(imp_info, cv, 1.8);
    """

    """
    # test setの取得
#    test_cv, test_info = get_testdata()
    """

    """
    # 多数派をrandom sampling
    info, cv_d = random_sampl(imp_info, cv)
    """
    
    #svm回帰の実施
#    problem = svm_problem(cv.tolist(),imp_info.tolist())
#    param = svm_parameter('-s 0 -t 0 -b 1 -w1 100') #-w1 100
    problem = svm_problem(cv.tolist(),imp_info.tolist())
#    problem = svm_problem(cv.tolist(), imp_info.tolist())
    param = svm_parameter('-s 0 -t 0 -b 1 -w1 100') #-w1 100 
    m = svm_train(problem, param)
    p_labels, p_acc, p_vals = svm_predict(cv.tolist(), imp_info.tolist(), m) # result training , '-b 1' 
    print p_labels
    print p_acc
    print p_vals
    print sum(1*(cv==1))
    p_labels = np.array(p_labels)
    print sum(1*(p_labels==1))
    print "positive accuracy(Number)", sum(p_labels[np.where(cv==1)])
