# coding: utf8

import numpy as np
import scipy as sp
import math
from scipy import linalg as sln
from scipy.sparse import linalg as sprsln
from svm import *
from svmutil import *
#from sklearn import linear_model as sklm


imp_num = 2000 #データ発生数
usr_num = 100 # user数
 
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
        print usr_ctg_idx[imp_usr[i]], imp_usr[i], adctgry_idx[i]
        if usr_ctg_idx[imp_usr[i]]-20 <= adctgry_idx[i] <= usr_ctg_idx[imp_usr[i]]+20 \
                 and adcrps_idx[i]<6 and usrinfo[imp_usr[i],1001] < 5 and \
                 adcmpgn_idx[i] < 10 and adcrsz_idx[i] < 10:
            ct.append(1)
        #elif np.random.uniform(0, 1, size=1) > 0.95: ct.append(1)
        else: ct.append(0)
        print ct[i]
        
        ct_crt[i,0] = usr_ctg_idx[imp_usr[i]]
        ct_crt[i,1] = adctgry_idx[i]
        ct_crt[i,2] = timeinfo[i]
        ct_crt[i,3] = adcrps_idx[i]
        ct_crt[i,4] = ct[i]
    ct = np.array(ct)
    
    return adinfo, usrinfo, deviceinfo, timeinfo, imp_usr, ct, ct_crt, usr_ctg_idx
    
if __name__=='__main__':
    ad, usr, dvc, time, imp_usr, cv, cv_crt, usr_ctg = create_data()

    imp_info = np.array(
                [ np.hstack( (ad[i,:], usr[imp_usr[i],:], dvc[i,:], time[i]) )
                  for i in xrange(len(imp_usr)) ]
                )

    # ad行列の圧縮
    U, S, Vh = sln.svd(imp_info)
    imp_info = np.dot(imp_info, Vh[:, :1000])    

#     # user情報の圧縮    
#     U, S, Vh = sln.svd(usr[:, :-2])
#     usr_inte = np.dot(usr[:,:-2], Vh[:, :1000])
#     usr_info = np.column_stack((usr_inte, usr[:, -2:]))
        
#     imp_info = np.array(
#                 [ np.hstack( (ad_info[i,:], usr_info[imp_usr[i],:], dvc[i,:], time[i]) )
#                   for i in xrange(len(imp_usr)) ]
#                 )
    
    #svm回帰の実施
    problem = svm_problem(cv.tolist(),imp_info.tolist())
    param = svm_parameter('-s 0 -t 0 -b 1 -w1 100') #-w1 100 
    m = svm_train(problem, param)
    p_labels, p_acc, p_vals = svm_predict(cv.tolist(), imp_info.tolist(), m) # result training , '-b 1' 
    print p_labels
    print p_acc
    print p_vals
    
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/p_lavels.csv',p_labels,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/ad.csv',ad,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/usr.csv',usr,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/usr_ctg.csv',usr_ctg,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/dev.csv',dvc,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/time.csv',time,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/imp_usr.csv',imp_usr,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/imp_info.csv',imp_info,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/cv.csv',cv,delimiter=',')
    np.savetxt('C:/workspace/python/MyPython/works/output/microad/ctr/cv_crt.csv',cv_crt,delimiter=',')