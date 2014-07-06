#coding: utf8
'''
Created on 2013/08/18

@author: nahki
'''

from multiprocessing import *
import numpy as np
import time


def chec_unique((now_ele, pre_bec, res)):
    if np.sum([pre_bec==now_ele])==0:
        res.append(now_ele)
    return res


if __name__=='__main__':
    pre=np.arange(1000000)
    now=np.arange(10000)

    t1=time.time()
    res = []
    pool = Pool(processes=4)
    r = np.array( pool.map(chec_unique, ((v, pre, res) for v in now)) )
    pool.close()
    pool.join()
    t2=time.time()
    
    print r
    print t2-t1 # 2 minutes a so