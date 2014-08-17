# coding:utf-8

import io
import numpy as np
import pandas as pd

class RewardMaximizer:
    def __init__(self, limit_duration):
        self.limit_duration = limit_duration
    
    def maximize_reward(self,data,sort_col_name):
        sorted_data = self.sort_data(data, sort_col_name)
        return self.calculate_total_raward(sorted_data)
                
    def calculate_total_raward(self, data):
        selected_pairs = self.select_pairs(data)
        return sum(selected_pairs[:,0]), sum(selected_pairs[:,1])
        
    def select_pairs(self,data):
        total_duration = 0
        selected_pairs = []
        for row in data.values:
            if total_duration + row[1]<=self.limit_duration:
                selected_pairs.append(row)
                total_duration += row[1]
        return np.array(selected_pairs)
            
    
    def sort_data(self,data,colname):
        return data.sort(colname,ascending=0)
    
    def calculate_reward_par_duration(self,reward, duration):
        return reward / duration
    
    def read_data(self,filename,colnames,enocode):
        return pd.read_csv(filename, header=None, names=colnames, encoding=encode)
        
        
if __name__=='__main__':
    limit_duration = 100
    rm = RewardMaximizer(limit_duration)

    filename = 'candy_order.csv'
    colnames = 'reward duration'.split(' ')
    encode = 'Shift_JIS'
    data = rm.read_data(filename,colnames,encode)
    
    data['efficient'] = rm.calculate_reward_par_duration(
                                        data[colnames[0]],data[colnames[1]])
    
    sort_col_name = 'efficient'
    total_rewards, total_duration = \
                    rm.maximize_reward(data, sort_col_name)
    
    print 'total reward:', total_rewards
    print 'total duration:', total_duration