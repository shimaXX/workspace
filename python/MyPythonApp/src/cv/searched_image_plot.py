# -*- coding: utf-8 -*-
import imagesearch
import imtools
imlist = sorted(imtools.get_imlist('nail_book03'))
from svm import *
from svmutil import *
import os
import cv2
import cv2.cv as cv
import sqlite3 as sqlite
import pickle
import numpy as np
import csv
import random
import math
from scipy.stats import norm 
from copy import deepcopy 


execfile('loaddata.py')
path = 'nail_book03'
train_csvfile = 'train_labels04.csv'
test_csvfile = 'test_labels04.csv'
csvfile = 'train_labels.csv'
HSV_fname = 'fHSV_hist.txt'
hsv_flag_fname = 'hsv_flag.csv'

src = imagesearch.Searcher('nail_image500.db',voc)

def main_boost():
    train_ratio = 0.5
    src = Searcher('nail_image500.db')
    # get histogram
    HSV_hist = np.loadtxt(HSV_fname) # fHSVのヒストグラムを読み込む
    
    # normalize HSV hist 
    HSV_max = np.max(HSV_hist, axis = 1)
    HSV_min = np.min(HSV_hist, axis = 1)
    HSV_rang = (HSV_max -HSV_min).reshape((len(HSV_max), 1))
    HSV_hist_norm = [(HSV_hist[i] - HSV_min[i])/HSV_rang[i] for i in xrange(len(HSV_rang))]
    
    samples = np.array( src.get_hist() , dtype = np.float32)

    # normalize BoW(samples) hist
    smp_max = np.max(samples, axis = 1)
    smp_min = np.min(samples, axis = 1)
    smp_rang = (smp_max - smp_min).reshape((len(smp_max), 1))
    smp_norm = [(samples[i] - smp_min[i])/smp_rang[i] for i in xrange(len(smp_rang))]

    samples = np.hstack((smp_norm, HSV_hist_norm))
    #samples = np.hstack((samples, HSV_hist))
    
    # get labels(object)
    responses = np.int8(next(csv.reader(file(csvfile, 'r'), delimiter=',')))
    responses[responses==-1] = 0

    # get HSV area flag()
    hsv_flag = np.int8(next(csv.reader(file(hsv_flag_fname, 'r'), delimiter=',')))
    
    # get sample indexes
    train_idx = random.sample( range(len(samples)), int(len(samples)*train_ratio) )  
    test_idx = range(len(samples)) # initialize test index
    for t in train_idx: test_idx.remove(t) # remove train index. and create test index.
    
    # implement Model
    boost = Boost()
    # create model
    boost.train(samples[train_idx,:], responses[train_idx])
    
    boost.save('test_boost')
    # predict use created model
    print "raw",boost.predict(samples[test_idx])
    print "test_rst",responses[test_idx]
    print "hsv_flag", hsv_flag[test_idx]
    train_rate = np.mean(boost.predict(samples[train_idx]) == responses[train_idx])
    train_res = boost.predict(samples[test_idx])
    test_rate = np.mean(train_res == responses[test_idx])
    
    # テストの結果をhsvによって補正する
    revision = deepcopy(train_res)
    revision[ hsv_flag[test_idx]==1 ] = 1
    res_rate = np.mean(revision == responses[test_idx])
    
    print "revision", revision
    
    print "train",train_rate
    print "test",test_rate
    print "res_rate",res_rate
    

class LetterStatModel(object):
    class_n = 2
    train_ratio = 0.5
    
    def load(self, fn):
        self.model.load(fn)
    def save(self, fn):
        self.model.save(fn)
    
    def unroll_samples(self, samples):
        sample_n, var_n = samples.shape
        new_samples = np.zeros((sample_n * self.class_n, var_n+1), np.float32)
        new_samples[:,:-1] = np.repeat(samples, self.class_n, axis=0)
        new_samples[:,-1] = np.tile(np.arange(self.class_n), sample_n)
        return new_samples
    
    def unroll_responses(self, responses):
        sample_n = len(responses)
        new_responses = np.zeros(sample_n*self.class_n, np.int32)
        resp_idx = np.int32( responses + np.arange(sample_n)*self.class_n )
        new_responses[resp_idx] = 1
        return new_responses

# ユークリッド距離による類似画像を返す
def euclid():
    nbr_results = 6
    for n_im in xrange(len(imlist)):
        print "n_im=",n_im
        res = [w[1] for w in src.query(imlist[n_im])[:nbr_results]]
        imagesearch.plot_results(src,res)

def svm_class(labels,HSV_fname):
    for im in imlist:
        print "imlist", im
    result,m = src.classify_via_svm(labels, imlist, HSV_fname) # 対象はDB内で調整している（where filename not like '%images1%'）
    with open('nail_labels.csv','w') as f:
        f.write((",".join([str(result)]))+"\n")
    return result, m

class Boost(LetterStatModel):
    def __init__(self):
        self.model = cv2.Boost()
        self.class_n = 2
    
    def train(self, samples, responses):
        sample_n, var_n = samples.shape
        new_samples = self.unroll_samples(samples) # if data have  multi class
        new_responses = self.unroll_responses(responses) # if data have  multi class
        var_types = np.array([cv2.CV_VAR_NUMERICAL] * var_n + [cv2.CV_VAR_CATEGORICAL, cv2.CV_VAR_CATEGORICAL], np.uint8)
        #CvBoostParams(CvBoost::REAL, 100, 0.95, 5, false, 0 )
        params = dict(max_depth=5) #, use_surrogates=False)
        self.model.train(new_samples, cv2.CV_ROW_SAMPLE, new_responses, varType = var_types, params=params)
    
    def predict(self, samples):
        new_samples = self.unroll_samples(samples)
        pred = np.array( [self.model.predict(s, returnSum = True) for s in new_samples] )
        pred = pred.reshape(-1, self.class_n).argmax(1)
        return pred

class boosting_svm(object):
    def __init__(self,ITR_BOOST=200, BOOST_TRAIN_RATE=0.5):
        self.itr_boost = ITR_BOOST
        self.boost_train_rate = BOOST_TRAIN_RATE
        
    def create_models(self):
        # initialize
        itr =0
        err = []
        epsilon = []
        self.alpha = []
        prs_err = 0
        self.fname = []
        
        # get labels
        labels = np.int8(next(csv.reader(file(csvfile, 'r'), delimiter=',')))
        # get hist
        hist = src.get_hist() # 対象はDB内で調整している（where filename like '%images1%'）
        sample_n = labels.shape[0] # get number of sample
        
        # number of training data
        num_train = int(sample_n/3*2)
        ind = np.arange(sample_n)
        ind_list =ind.tolist() 
        
        # trainigに使用するdata set
        random.shuffle(ind_list)
        train_ind = ind_list[:num_train]
        pred_ind = ind_list[num_train:]
        
        train_smp_hist = np.array(hist)[train_ind].tolist()
        train_smp_labels = np.array(labels)[train_ind].tolist()
        
        # create weight
        D = np.ones(num_train, dtype = np.float32) # get initial weight
        D_t = D/num_train
        self.D = []
        self.D.append(D_t)
    
        # number of using traing
        train_smp_n = int(num_train*self.boost_train_rate)
        
        # 汎化誤差計算用 test data set
        self.pred_hist = np.array(hist)[pred_ind].tolist()
        self.pred_labels = np.array(labels)[num_train:].tolist()
        self.pred_num = sample_n - num_train
        
        print sample_n
        for itr in xrange(self.itr_boost): # continuation condition
            print itr
            
            ## select training set and test set
            # get training set index
            w_val = norm.rvs(loc = self.D[itr], scale=0.1, size = num_train)
            raw_val = deepcopy(w_val)
            w_val.sort() # 昇順に直す
            w_val = w_val[::-1] # 降順で取得
            sorted_index = [np.where(raw_val==v)[0][0] for v in w_val]
            train_index = sorted_index[:train_smp_n]
            #test_index = [i for i in ind if i not in train_index]
            
            # get training set add test set
            train_hist = np.array(train_smp_hist)[train_index].tolist()
            #test_hist = deepcopy(train_smp_hist)
            train_labels = np.array(train_smp_labels)[train_index].tolist()
            #test_labels = deepcopy(train_smp_labels)
            
            # do svm
            # create svm model
            problem = svm_problem(train_labels,train_hist)
            param = svm_parameter('-s 0 -t 2') # デフォルト0 -- C-SVC、2 -- 動径基底関数カーネル: K(u,v) = exp(-&gamma |u-v|2)。 -b　1でpredictionで確率表示
            m = svm_train(problem, param) # training
            p_labels, p_acc, p_vals = svm_predict(train_smp_labels, train_smp_hist, m) # result training
    
            # save the svm model
            lab = ('0000'+str(itr))[-4:]
            fname = 'boost_svm' + lab + '.model'
            svm_save_model(fname, m)
            self.fname.append(fname)
            
            # do training
            tmp = np.array(p_labels) - np.array(train_smp_labels)
            
            # calculate number of error
            err_lab = np.float32(1.0)*(tmp!=0)
            num_err = np.sum( err_lab )
            prs_err = num_err/train_smp_n
            err.append(prs_err)
            # calculate epsilon
            epsilon = np.sum( err_lab*self.D[itr] ) 
            self.alpha.append(0.5*math.log((1-epsilon)/epsilon))
                    
            # calculate D
            tmp = self.D[itr]*np.exp(-self.alpha[itr]*np.float32(train_smp_labels)*p_labels)
            Z_t = np.sum(tmp)
            self.D.append(tmp/Z_t)

    def test(self):
        hyp = []
        for f in self.fname:
            print "fname",f
            m = svm_load_model(f)
            p_labels, p_acc, p_vals = svm_predict(self.pred_labels, self.pred_hist, m) # labelが未知の場合は適当の与えておく
            hyp.append(p_labels)  
        alpha = np.array(self.alpha).reshape((self.itr_boost, 1))
        # show
        tmp =  np.sum(alpha*np.array(hyp), axis=0) 
        H = np.sign(tmp) # 多数決の結果
        print "pred_labels",self.pred_labels
        res = np.array(self.pred_labels) - np.array(H) 
        err = np.sum(1*(res!=0), dtype= np.float32)
        print err
        print err/len(H)
        print "H",H
        
        return H


class Searcher(object):
    def __init__(self,db):
        """ データベース名とボキャブラリを用いて初期化する """
        self.con = sqlite.connect(db)
    
    def __del__(self):
        self.con.close()

    def get_imhistogram(self,imname):
        """ 画像のワードヒストグラムを返す """
        im_id = self.con.execute(
            "select rowid from imlist where filename='%s'" % imname).fetchone()
        s = self.con.execute(
            "select histogram from imhistograms where rowid='%d'" % im_id).fetchone()
        
        # pickleを使って文字列をNumPy配列に変換する
        return pickle.loads(str(s[0]))

    def get_hist(self):
        """ svmのtrainingを行う """
        # 名前を取得する
        cand_name = self.con.execute(
            #"select filename from imlist where filename not like '%images1%' and filename not like '%images2%'").fetchall()
            "select filename from imlist").fetchall()
        hist = []
        for cn in cand_name: 
            cand_h = self.get_imhistogram(cn)
            hist.append(cand_h.tolist())
        return hist


if __name__ == '__main__':
    """
    ''' svmによるboosting '''
    boost = boosting_svm(10,0.5)
    boost.create_models()
    H = boost.test()
    """
    
    
    ''' random forest '''
    main_boost() # boosting.using rtrees.
    #boosting_svm()

    
    """
    ### training svm
    labels = np.int8(next(csv.reader(file(train_csvfile, 'r'), delimiter=',')))
    result,m = svm_class(labels, HSV_fname)
    svm_save_model('test.model', m)
    
    
    pred_lab = np.int8(next(csv.reader(file(test_csvfile, 'r'), delimiter=',')))
    print pred_lab.shape
    hist = src.get_pred_hist() # 対象はDB内で調整している（where filename like '%images1%'）
    m = svm_load_model('test.model')
    p_labels, p_acc, p_vals = svm_predict(pred_lab, hist, m) # labelが未知の場合は適当の与えておく
    print p_labels
    """
    
    """
    samples = np.array( src.get_hist() , dtype = np.float32)
    boost = Boost()
    boost.load('test_boost')
    boost.predict(samples)
    """