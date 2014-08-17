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
        
    def lasso(self,ofname,featdim=7):
        model = LogisticRegression(penalty='l2',class_weight='auto',C=1.0, tol=0.00001)
        y = self.raw.ix[:,0].values
        ls_res = model.fit(self.raw.ix[:,1:featdim], y)
        coef = ls_res.coef_
        #print "coef", ls_res.coef_
        #print "intercept", ls_res.intercept_
        result_label = ls_res.predict(self.raw.ix[:,1:featdim])
        true_positive = str( sum( (result_label==1) * (y==1) ) )
        false_positive = str( sum( (result_label==1) * (y==0) ) )
        true_negative = str( sum( (result_label==0) * (y==0) ) )
        false_negative = str( sum( (result_label==0) * (y==1) ) )
        
        with open(ofname, 'w', 1000) as f:
            s = ','.join( [true_positive,false_negative,false_positive,true_negative] )
            f.write(s)
        #self.save_result(coef, ofname)
        
    def save_result(self,coef,ofname):
        with open(ofname, 'w',1000) as f:
            for c in coef[0]:
                f.write(str(c)+'\n')        
        
if __name__=='__main__':
    methods = ('MI','LR','RF',)
    years = ('2013','2014',)

    datafbase = os.getcwd()+'/../_0725/output/result/' #webspam_wc_normalized_trigram, kddb
    rodelfbase = os.getcwd()+'/../_0725/output/logi_test/'
    
    dimention=20
    
    vng = VariablesNessesarityGetter()
    for year in years:
        for method in methods:
            dataf = datafbase + method+'_'+year+'.csv' #webspam_wc_normalized_trigram, kddb
            testd_fname = dataf
            rodelf = rodelfbase +method+'_'+year+'.csv'
            
            #train_mat(dataf,modelf,dimention=dimention)
            #test(modelf, testd_fname, rodelf,dimention) #train_mat()
    
            #filename = os.getcwd()+'/output/vellfire_data.csv'
            #filename = os.getcwd()+'/output/logi_test/vellfire_data_2013.csv'
            
            # strage raw data
            vng.get_data(dataf)
            
            # lassoの実行
            vng.lasso(rodelf,featdim=dimention)