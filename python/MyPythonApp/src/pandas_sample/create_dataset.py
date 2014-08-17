# coding: utf-8

import pandas as pd
import numpy as np
import os, io
from collections import defaultdict

class DataSetCreator:
    TITLE_COL_NUMBER = 10
    
    def __init__(self,input_filename):
        self.raw = pd.read_csv(input_filename)
    
    def __del__(self):
        pass
    
    def processed_data(self,car_type, ofname, view_thresh=0):
        
        of = open(ofname, 'w')
        self.sqew_data(car_type,view_thresh,of)
    
    def sqew_data(self, car_type,view_thresh,of):
        viewing_cnt_clumn_name = car_type+'_display'
        click_cnt_clumn_name = car_type+'_click'
        raw = self.raw.fillna(0)
        
        # save raw summary
        self.save_summary_data(raw,viewing_cnt_clumn_name,click_cnt_clumn_name)
        
        raw = raw[raw[viewing_cnt_clumn_name]>view_thresh]        
        dataset = raw[np.sum(raw.ix[:,self.TITLE_COL_NUMBER:],axis=1)>0]
        # aggregate unique user
        unique_dtaset = dataset.groupby(['unicst_id',viewing_cnt_clumn_name,click_cnt_clumn_name,'gender','age','region']).sum()
        #test.to_csv(os.getcwd()+'/output/'+car_type+'_test_data_out.csv')
        #print test.head
        
        # save raw summary
        self.save_summary_data(dataset,viewing_cnt_clumn_name,click_cnt_clumn_name, thresh=view_thresh)

        unique_dtaset.to_csv('use_data_'+car_type+'.csv')
        unique_dtaset = pd.read_csv('use_data_'+car_type+'.csv')

        t_data = unique_dtaset.ix[:,self.TITLE_COL_NUMBER:].T        
        t_data.to_csv('test_out_'+car_type)
        with open('test_out_'+car_type, 'r', 10000) as f:
            itr=0
            viewed_dic = defaultdict(list)
            for line in f:
                if itr==0:
                    itr+=1
                    continue
                med_data = line.strip().split(',')
                title = med_data[0].replace(r'.1','').replace(r'.2','').replace(r'.3','').replace(r'.4','')
                if title in viewed_dic:
                    viewed_dic[title] += np.array(med_data[1:],dtype=np.float32)
                else:
                    viewed_dic[title] = np.array(med_data[1:],dtype=np.float32)
        s = 'click_cnt'+','+','.join(viewed_dic.keys())
        of.write(s+'\n')

        clicked = raw[raw[click_cnt_clumn_name]>0]
        self.save_summary_data(clicked,viewing_cnt_clumn_name,click_cnt_clumn_name,click=1)
        
        clicked = dataset[dataset[click_cnt_clumn_name]>0]
        self.save_summary_data(clicked,viewing_cnt_clumn_name,click_cnt_clumn_name,thresh=1,click=1)
        
        click_data = unique_dtaset[click_cnt_clumn_name].values
        click_data[click_data>0]=1
        for i in xrange(len(click_data)):
            print 'index:',i,' saving...'
            s = str(click_data[i])
            for title, ls in viewed_dic.items():
                flag = '1' if ls[i]>0 else '0'
                s += ','+flag
            of.write(s+'\n')
        of.close()

    def save_summary_data(self,raw,viewing_cnt_clumn_name,click_cnt_clumn_name,thresh=None,click=None):
        if thresh is None and click is None:
            ## cross aggregation
            # imp
            grouped = raw.groupby(viewing_cnt_clumn_name)#.unicst_id.unique()
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/imp_usr_count/'+car_type+'_imp.csv')
            
            # click
            grouped = raw.groupby(click_cnt_clumn_name)
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/click_usr_count/'+car_type+'_click.csv')
            
            # gender * age
            grouped = raw.groupby(['gender','age'])
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/gender_age/'+car_type+'_cross.csv')
        elif thresh is not None and click is None:
            ## cross aggregation
            # imp
            grouped = raw.groupby(viewing_cnt_clumn_name)#.unicst_id.unique()
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/imp_usr_count/'+car_type+'_imp_thresh.csv')
            
            # click
            grouped = raw.groupby(click_cnt_clumn_name)
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/click_usr_count/'+car_type+'_click_thresh.csv')
            
            # gender * age
            grouped = raw.groupby(['gender','age'])
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/gender_age/'+car_type+'_cross_thresh.csv')
        elif thresh is None and click is not None: 
            ## cross aggregation
            # imp
            grouped = raw.groupby(viewing_cnt_clumn_name)#.unicst_id.unique()
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/imp_usr_count/'+car_type+'_imp_clicked.csv')
            
            # click
            grouped = raw.groupby(click_cnt_clumn_name)
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/click_usr_count/'+car_type+'_click_clicked.csv')
            
            # gender * age
            grouped = raw.groupby(['gender','age'])
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/gender_age/'+car_type+'_cross_clicked.csv')            
        elif thresh is not None and click is not None: 
            ## cross aggregation
            # imp
            grouped = raw.groupby(viewing_cnt_clumn_name)#.unicst_id.unique()
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/imp_usr_count/'+car_type+'_imp_thresh_clicked.csv')
            
            # click
            grouped = raw.groupby(click_cnt_clumn_name)
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/click_usr_count/'+car_type+'_click_thresh_clicked.csv')
            
            # gender * age
            grouped = raw.groupby(['gender','age'])
            usr_cnt = grouped.agg({'unicst_id': pd.Series.nunique})
            usr_cnt.to_csv(os.getcwd()+'/output/gender_age/'+car_type+'_cross_thresh_clicked.csv')


if __name__=='__main__':
    ifname = os.getcwd()+'/input/pana_toyota_banner_data_plus_uid.csv'
    
    car_type_list = 'vellfire spade aqua'.strip().split(' ')
    
    dsc = DataSetCreator(ifname)
    
    for car_type in car_type_list:
        ofname = os.getcwd()+'/output/'+car_type+'_data.csv'
        dsc.processed_data(car_type,ofname,view_thresh=4) # 1回以上見ている人のデータを取る