# coding: utf-8
#.groupby('hogehoge').user_id.nunique()

import sqlite3 as sqlite
import pandas as pd
import numpy as np
import os


class RecognitionAggregate:
    def __init__(self):
        pass
    
    def read_data(self,filename):
        self.data = pd.read_csv(filename)
        #print self.data.head()
        
    def aggregate(self):
        tv_pre_recog = self.calculate_recog('recog_flag')
        filmil_recog = self.calculate_recog('Q2')
        pre_tv_and_filmil_recog = self.calculate_recog_recognized('Q2')
        pre_not_tv_and_filmil_recog = self.calculate_recog_not_recognized('Q2')        
        
        tv_pre_recog.to_csv('tv_pre_recog.csv')
        filmil_recog.to_csv('filmil_recog.csv')
        pre_tv_and_filmil_recog.to_csv('pre_tv_and_filmil_recog.csv')
        pre_not_tv_and_filmil_recog.to_csv('not_tv_and_filmil_recog.csv')        
        
    def calculate_recog(self,target):
        recog_clear = self.count_recog1(target)
        recog_somewhat = self.count_recog2(target)
        non_recog = self.count_non_recog(target)
        
        denominator = recog_clear+recog_somewhat+non_recog
        r_recog_clear = recog_clear/denominator
        r_recog_clear['somewhat'] = recog_somewhat/denominator
        r_recog_clear.columns = ['clear','somewhat']
        return r_recog_clear

    def calculate_recog_recognized(self,target):
        recog_clear = self.count_recog1_pre_recognized(target)
        recog_somewhat = self.count_recog2_pre_recognized(target)
        non_recog = self.count_non_recog_pre_recognized(target)
        
        denominator = recog_clear+recog_somewhat+non_recog
        r_recog_clear = recog_clear/denominator
        r_recog_clear['somewhat'] = recog_somewhat/denominator
        r_recog_clear.columns = ['clear','somewhat']
        return r_recog_clear

    def calculate_recog_not_recognized(self,target):
        recog_clear = self.count_recog1_not_recognized(target)
        recog_somewhat = self.count_recog2_not_recognized(target)
        non_recog = self.count_non_recog_not_recognized(target)
        
        denominator = recog_clear+recog_somewhat+non_recog
        r_recog_clear = recog_clear/denominator
        r_recog_clear['somewhat'] = recog_somewhat/denominator
        r_recog_clear.columns = ['clear','somewhat']
        return r_recog_clear
    
    # count recognization number      
    def count_non_recog(self,target):
        df_tmp = self.data[['sampleID','CM_No']][self.data[target]==3]
        return df_tmp.groupby('CM_No').count()
    
    def count_recog1(self,target): # clear
        df_tmp = self.data[['sampleID','CM_No']][self.data[target]==1]
        return df_tmp.groupby('CM_No').count()
    
    def count_recog2(self,target): # somewhat
        df_tmp = self.data[['sampleID','CM_No']][self.data[target]==2]
        return df_tmp.groupby('CM_No').count()

    # cross have recognized tv
    def count_non_recog_pre_recognized(self,target):
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==3) & \
                            ((self.data['recog_flag']==1) | (self.data['recog_flag']==2))]
        return df_tmp.groupby('CM_No').count()
    
    def count_recog1_pre_recognized(self,target): # clear
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==1) & \
                            ((self.data['recog_flag']==1) | (self.data['recog_flag']==2))]
        return df_tmp.groupby('CM_No').count()
    
    def count_recog2_pre_recognized(self,target): # somewhat
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==2) & \
                            ((self.data['recog_flag']==1) | (self.data['recog_flag']==2))]
        return df_tmp.groupby('CM_No').count()

    # cross not have recognized tv
    def count_non_recog_not_recognized(self,target):
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==3) & (self.data['recog_flag']==3)]
        return df_tmp.groupby('CM_No').count()
    
    def count_recog1_not_recognized(self,target): # clear
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==1) & (self.data['recog_flag']==3)]
        return df_tmp.groupby('CM_No').count()
    
    def count_recog2_not_recognized(self,target): # somewhat
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==2) & (self.data['recog_flag']==3)]
        return df_tmp.groupby('CM_No').count()


class UnderstandingAggregate:
    def __init__(self):
        pass
    
    def read_data(self,filename):
        self.data = pd.read_csv(filename)
        #print self.data.head()
        
    def aggregate(self):
        only_tv_recognized_understanding = self.calculate_understanding_rate_only_tv('tv_recognition')
        only_filmil_recognized_understanding = self.calculate_understanding_rate_only_filmil('Q4')
        tv_and_filmil_recognized_understanding = self.calculate_understanding_rate_tv_and_filimi('Q4')

        only_tv_recognized_understanding.to_csv('only_tv_recognized_understanding_rate.csv')
        only_filmil_recognized_understanding.to_csv('only_filmil_recognized_understanding_rate(Q4).csv')
        tv_and_filmil_recognized_understanding.to_csv('tv_and_filmil_recognized_understanding_rate(Q4).csv')
        
        # Q5 
        only_filmil_recognized_understanding = self.calculate_understanding_rate_only_filmil('Q5') # 好意
        tv_and_filmil_recognized_understanding = self.calculate_understanding_rate_tv_and_filimi('Q5')

        only_filmil_recognized_understanding.to_csv('only_filmil_recognized_favor_rate(Q5).csv')
        tv_and_filmil_recognized_understanding.to_csv('tv_and_filmil_recognized_favor_rate(Q5).csv')

        # Q6
        only_filmil_recognized_understanding = self.calculate_understanding_rate_only_filmil('Q6') # 興味
        tv_and_filmil_recognized_understanding = self.calculate_understanding_rate_tv_and_filimi('Q6')

        only_filmil_recognized_understanding.to_csv('only_filmil_recognized_interest_rate(Q6).csv')
        tv_and_filmil_recognized_understanding.to_csv('tv_and_filmil_recognized_interest_rate(Q6).csv')        
        
        # Q7
        only_filmil_recognized_understanding = self.calculate_understanding_rate_only_filmil('Q7') # 購入意向
        tv_and_filmil_recognized_understanding = self.calculate_understanding_rate_tv_and_filimi('Q7')

        only_filmil_recognized_understanding.to_csv('only_filmil_recognized_purchase _rate(Q7).csv')
        tv_and_filmil_recognized_understanding.to_csv('tv_and_filmil_recognized_purchase _rate(Q7).csv')
        
    def calculate_understanding_rate_only_tv(self,target):
        recog_clear = self.count_only_tv_recognized_understand1(target)
        recog_somewhat = self.count_only_tv_recognized_understand2(target)
        non_recog = self.count_only_tv_recognized_not_understand(target)
        
        denominator = recog_clear+recog_somewhat+non_recog
        r_recog_clear = recog_clear/denominator
        r_recog_clear['somewhat'] = recog_somewhat/denominator
        r_recog_clear.columns = ['clear','somewhat']
        return r_recog_clear

    def calculate_understanding_rate_only_filmil(self,target):
        recog_clear = self.count_recognized_filmil_and_tv_nunderstand1(target)
        recog_somewhat = self.count_recognized_filmil_and_tv_nunderstand2(target)
        non_recog = self.count_recognized_filmil_and_tv_not_nunderstand(target)
        
        denominator = recog_clear+recog_somewhat+non_recog
        r_recog_clear = recog_clear/denominator
        r_recog_clear['somewhat'] = recog_somewhat/denominator
        r_recog_clear.columns = ['clear','somewhat']
        return r_recog_clear

    def calculate_understanding_rate_tv_and_filimi(self,target):
        recog_clear = self.count_recognized_filmil_and_tv_nunderstand1(target)
        recog_somewhat = self.count_recognized_filmil_and_tv_nunderstand2(target)
        non_recog = self.count_recognized_filmil_and_tv_not_nunderstand(target)
        
        denominator = recog_clear+recog_somewhat+non_recog
        r_recog_clear = recog_clear/denominator
        r_recog_clear['somewhat'] = recog_somewhat/denominator
        r_recog_clear.columns = ['clear','somewhat']
        return r_recog_clear
    
    # count have recognized only tv
    def count_only_tv_recognized_not_understand(self,target):
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]>=3)]
        return df_tmp.groupby('CM_No').count()
    
    def count_only_tv_recognized_understand1(self,target): # clear
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==1)]
        return df_tmp.groupby('CM_No').count()
    
    def count_only_tv_recognized_understand2(self,target): # somewhat
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==2)]
        return df_tmp.groupby('CM_No').count()




    # cross have recognized only filmil
    def count_only_filmil_recognized_not_nunderstand(self,target):
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]>=3) & (self.data['recog_flag']==3)]
        return df_tmp.groupby('CM_No').count()
    
    def count_only_filmil_recognized_nunderstand1(self,target): # clear
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==1) & (self.data['recog_flag']==3)]
        return df_tmp.groupby('CM_No').count()
    
    def count_only_filmil_recognized_nunderstand2(self,target): # somewhat
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==2) & (self.data['recog_flag']==3)]
        return df_tmp.groupby('CM_No').count()



    # cross have recognized tv and filmil
    def count_recognized_filmil_and_tv_not_nunderstand(self,target):
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]>=3) & \
                        ((self.data['recog_flag']==1) | (self.data['recog_flag']==2)) & \
                        ((self.data['Q2']==1) | (self.data['Q2']==2))]
        return df_tmp.groupby('CM_No').count()
    
    def count_recognized_filmil_and_tv_nunderstand1(self,target): # clear
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==1) & \
                        ((self.data['recog_flag']==1) | (self.data['recog_flag']==2)) & \
                        ((self.data['Q2']==1) | (self.data['Q2']==2))]
        return df_tmp.groupby('CM_No').count()
    
    def count_recognized_filmil_and_tv_nunderstand2(self,target): # somewhat
        df_tmp = self.data[['sampleID','CM_No']][(self.data[target]==2) & \
                        ((self.data['recog_flag']==1) | (self.data['recog_flag']==2)) & \
                        ((self.data['Q2']==1) | (self.data['Q2']==2))]
        return df_tmp.groupby('CM_No').count()

if __name__=='__main__':
    """ サンプルID    プロフィールID    gender    CM_No    素材名    Q2    Q3    Q4    Q5    Q6    Q7    Q15    viewing_cnt    認知flag """
    filename = os.getcwd()+'/input/filmil_raw_data.csv'
    
    # recognition
    ragg = RecognitionAggregate()
    ragg.read_data(filename)
    ragg.aggregate()
    
    # understanding
    ua = UnderstandingAggregate()
    ua.read_data(filename)
    ua.aggregate()
    