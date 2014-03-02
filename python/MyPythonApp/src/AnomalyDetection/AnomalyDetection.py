# coding: utf-8
'''
Created on 2012/12/14

@author: n_shimada
'''
from __future__ import with_statement

import math
import numpy as np
import statsmodels as sm
import matplotlib.pyplot as plt
from pandas import *
from scipy import *
from Scientific.Statistics import *
from patsy import *
from statsmodels.tsa import *
from statsmodels.tsa import arima_model


#import math
#import numpy as np
#import statsmodels as sm
##import matplotlib.pyplot as plt
#from pandas import *
##from scipy import *
#from Scientific.Statistics import *
#from statsmodels.tsa import arima_model
#from patsy import *


#ARIMAモデルのパラメータの設定
TERM = 20
ORDER = [1, 1, 0]


def input_data(input_filename):
    output = {}

    with open(input_filename) as f:
        for line in f:
            output['testUser'] = [int(item) for item in line.strip().split()]
    return output


#データの整形
def get_input_data(input_filename):
    
    output = {}
    
    with open(input_filename) as f:
        for line in f:
            cols = line.strip().split()
            uid = cols[0]
            num = int(cols[2])
            if uid not in output:
                output[uid] = []
            output[uid].append(num)
            
    return output


def culcurate_score(seq_data):
    output = {}
    for k,seq_session_verb_cnt in seq_data.items():
        print "seq_session_verb_cnt"
        print seq_session_verb_cnt
        output[k] = change_anomaly_detection(seq_session_verb_cnt, term = TERM, order = ORDER)

    return output


#arimaモデルに投入 
def change_anomaly_detection(x, term=30, smooth_n=7, order=[1,0,0]):
    N = len(x)
    #ここ（outlier_score）でterm分のデータが前方からなくなる（予測データの残差を使用してスコアを算出するため）
    
    print "x"
    print x
    
    outlier_score = get_first_outlier_score(x, N, term)
    
    print "get_first_score"
    
    #ここ（outlier_score_smooth）でsmooth.n分のデータが前方からなくなる（移動平均を取るため）
    print "outlier_score"
    print outlier_score
    print "done_print_outlier_score"
    outlier_score_smooth = score_smoothing(outlier_score, smooth_n)

    N2 = len(outlier_score_smooth)
    change_score = get_second_outlier_score(outlier_score_smooth, N2, term)
    change_score_smooth = score_smoothing(change_score, round(smooth_n/2))

    print "get_second_score"

##############    
    print change_score_smooth
    
    for i in range(N-len(change_score_smooth)):
        change_score_smooth.insert(0,0)
    
    return change_score_smooth

#1段階目の外れ値スコアの取得
def get_first_outlier_score(x , N, term):
    output = [] 
    for i in range(N-term-1):
        train = x[i:(i+term)]
        target = double(x[(i+term+1)])
        results = arima_model.ARIMA(np.array(train, np.float), order=ORDER).fit()
        #results.summary()
        res = results.resid()
        pred = double(results.forecast(1)[0])  #returns 0:forecast, 1:stderr, 2:conf_int        
        
        output.append( outlier_score(train = res, var = (double(pred) - double(target))) )
    print "first_outlier_score"
    print output
    return output

#2段階目の外れ値スコアの取得
def get_second_outlier_score(x , N, term):
    output = []
    for i in range(N-term-1):
        train = x[i:(i+term)]
        target = x[(i+term+1)]
        
        output.append( outlier_score(train = train, var = double(target)) )

    return output

#外れ値スコアの取得時のスコア変換
def outlier_score(train, var):
    m = np.mean(train)
    s = np.std(train)
    
    print "outlier_score"
    
    return -math.log(1/np.sqrt(2*np.pi*s)*np.exp(-((var - m)**2)/(2*s)))

#スムージング
def score_smoothing(x, n=7):
    print "smoothing"
    print x
    window = np.ones(n)/(double(n))
    #return np.s(x, n)
    return np.convolve(x, window, 'valid')