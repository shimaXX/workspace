# coding: utf-8
'''
Created on 2013/11/11

@author: RN-017
'''

import SCW_Train
import SCW_Train_mat
import SCW_Test


dataf = 'D:/workspace/python/MyPythonApp/works/input/rcv1_train.binary' #webspam_wc_normalized_trigram, kddb
#dataf = 'C:/workspace/python/MyPython/works/input/tttest.txt'
modelf = 'D:/workspace/python/MyPythonApp/works/output/scw_test_model'
testd_fname = 'D:/workspace/python/MyPythonApp/works/input/rcv1_train.binary'
rodelf = 'D:/workspace/python/MyPythonApp/works/output/test_result'

def train():
    # training dataのあるディレクトリを指定
    sgd = SCW_Train.scw_bin_train(dataf, 7, 'hinge', 0.9, 1.0) # SGDのロス関数がログであれば'log', ヒンジロスであれば'hinge'
    weight = sgd.train()
    sgd.save_model(modelf,weight)
    
def train_mat():
    # training dataのあるディレクトリを指定
    sgd = SCW_Train_mat.scw_bin_train(dataf, 7, 'hinge', 0.9, 1.0) # SGDのロス関数がログであれば'log', ヒンジロスであれば'hinge'
    weight = sgd.train()
    sgd.save_model(modelf,weight)    
    
def test():
    # test
    sgd_t = SCW_Test.SCW_Test(modelf,testd_fname)
    sgd_t.read_model()
    pred, ans = sgd_t.test()
    sgd_t.save_result(rodelf, pred, ans)
    
if __name__=='__main__':
    test() #train_mat()