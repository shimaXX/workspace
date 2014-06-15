# coding: utf-8

import numpy as np
import pandas as pd
import sys, os
sys.path.append(os.getcwd()+'/../')

from data_to_stock import DataToStock

class AverageTrueRange:
    """true price range is moving average of price range. show below.
    price range =
        (higher value that close price of yesterday and today)
            - (lower value that close price of yesterday and today)
    """
    def __init__(self, stock, window):
        self.stock = stock
        self.window = window
        
    def calculate_indicator(self):
        yesterday_value = lambda x: x[0]
        today_value = lambda x: x[1]
        previous_close = pd.rolling_apply(
                            np.array(self.stock.close_prices(),dtype=np.float64),
                            2, yesterday_value)
        current_high = pd.rolling_apply(
                            np.array(self.stock.high_prices(),dtype=np.float64),
                            2, today_value)
        current_low = pd.rolling_apply(
                            np.array(self.stock.low_prices(),dtype=np.float64),
                            2, today_value)
        true_high = map( (lambda x,y: max(x,y)), previous_close, current_high )
        true_low = map( (lambda x,y: min(x,y)), previous_close, current_low )
        true_ranges = np.array(true_high,dtype=np.float64) \
                        - np.array(true_low,dtype=np.float64)
        
        return pd.rolling_mean(true_ranges, self.window).tolist()
    
    
if __name__=='__main__':
    data_dir = os.getcwd()+'/../../data'
    dbname = 'daily_stock_data.db'
    dts = DataToStock(data_dir, dbname, '2005-01-01', '2013-01-01') #'2005-01-01', '2013-01-01'
    stck = dts.generate_stock(1301)
    
    atr = AverageTrueRange(stck, 25)
    print atr.calculate_indicator()