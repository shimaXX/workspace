# coding: utf-8

from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
import os, io


class VariablesNessesarityGetter:
    def __init__(self):
        pass
    
    def __del__(self):
        pass

    def get_data(self,filename):
        self.raw = pd.read_csv(filename)
        
    def lasso(self,ofname):
        model = LogisticRegression(penalty='l1',class_weight='auto',C=1.0, tol=0.00001)
        ls_res = model.fit(self.raw.ix[:,1:],self.raw.ix[:,0])
        coef = ls_res.coef_
        print "coef", ls_res.coef_
        print "intercept", ls_res.intercept_
        self.save_result(coef, ofname)
        
    def save_result(self,coef,ofname):
        with open(ofname, 'w',1000) as f:
            for c in coef[0]:
                f.write(str(c)+'\n')
        
        
if __name__=='__main__':
    #ofname = os.getcwd()+'/output/coef/lasso_coef_vellfire.csv'
    ofname = os.getcwd()+'/output/coef/lasso_coef_vellfire_2013.csv'
    
    vng = VariablesNessesarityGetter()
    
    #filename = os.getcwd()+'/output/vellfire_data.csv'
    filename = os.getcwd()+'/output/vellfire_data_2013.csv'
    
    # strage raw data
    vng.get_data(filename)
    
    # lassoの実行
    vng.lasso(ofname)