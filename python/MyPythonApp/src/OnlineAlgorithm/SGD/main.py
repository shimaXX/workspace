# coding: utf-8
'''
Created on 2013/11/11

@author: RN-017
'''

import time

import SGD_Train
import SGDTrainNormalize
import SGDTrainSampling
import SGD_Test


dataf = 'C:/workspace/HadoopPig/HadoopPig/works/input/train_cov' #webspam_wc_normalized_trigram, kddb, covtype.libsvm.binary, splice, train_cov
modelf = 'C:/workspace/python/MyPython/works/output/test_model'
testd_fname = 'C:/workspace/HadoopPig/HadoopPig/works/input/test_cov'
rodelf = 'C:/workspace/python/MyPython/works/output/test_result'

def train():
    # training dataのあるディレクトリを指定
    #sgd = SGD_Train.sgd_bin_train(dataf, 6, 'log') # SGDのロス関数がログであれば'log', ヒンジロスであれば'hinge'
    sgd = SGD_Train.sgd_bin_train(dataf, 6, 'log') # SGDのロス関数がログであれば'log', ヒンジロスであれば'hinge'
    weight = sgd.train(1,0)
    sgd.save_model(modelf,weight)


def train_normalized():
    # training dataのあるディレクトリを指定
    sgd = SGDTrainNormalize.sgd_bin_train(dataf, 6, 'log') # SGDのロス関数がログであれば'log', ヒンジロスであれば'hinge'
    weight = sgd.train(0.5,0)
    sgd.save_model(modelf,weight)

    
def train_sampling():
    # training dataのあるディレクトリを指定
    sgd = SGDTrainSampling.sgd_bin_train(dataf, 6, 'log') # SGDのロス関数がログであれば'log', ヒンジロスであれば'hinge'
    weight = sgd.train(0.5,0)
    sgd.save_model(modelf,weight)
    
    
def test():
    # test
    sgd_t = SGD_Test.SGD_Test(modelf,testd_fname)
    sgd_t.read_model()
    pred, ans = sgd_t.test()
    sgd_t.save_result(rodelf, pred, ans)
    
if __name__=='__main__':
    time1 = time.clock()
    train() # train_normalized() # train_sampling()
    time2 = time.clock()
    print '処理時間は ', time2-time1