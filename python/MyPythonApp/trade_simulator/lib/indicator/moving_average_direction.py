# coding: utf-8

import pandas as pd
import numpy as np

class MovingAverageDirection:
    """compare patest close value and moving average of today
    today is higher than yesterday: up
    yesterday is higher than today: down
    today equal yesterday: flat
    """
    def __init__(self, stock, window):
        self.stock = stock
        self.window = window
        
    def calculate_indicator(self, label):
        prices = np.array(self.stock.get_data(label), dtype=np.float64)
        last = lambda x: x[-1]
        prices_last = pd.rolling_apply(prices, self.window, last)
        
        first = lambda x: x[0]
        prices_first = pd.rolling_apply(prices, self.window, first)
        
        direction = prices_last - prices_first
        direction[direction>0]=100
        direction[direction<0]=-100
        
        res = direction.astype(str)
        res[res=='100.0']='up'
        res[res=='-100.0']='down'
        res[res=='0.0']='flat'

        return res.tolist()