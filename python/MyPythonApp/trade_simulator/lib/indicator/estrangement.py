# coding: utf-8

import pandas as pd
import numpy as np

class Estrangement:
    """ calculate Estrangement moveing average and latest value  """
    def __init__(self, stock, window):
        self.stock = stock
        self.window = window
    
    def calculate_indicator(self, label): # self.stock.close_prices()
        prices = np.array(self.stock.get_data(label), dtype=np.float64)
        last = lambda x: x[-1]
        prices_last = pd.rolling_apply(prices, self.window, last)
        moving_average = pd.rolling_mean(prices, self.window)
        result = (prices_last-moving_average)/moving_average*100 # include nan
        return result.tolist()