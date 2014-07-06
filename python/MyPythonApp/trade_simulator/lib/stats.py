# coding: utf-8

import sys, os
from trade import Trade

class Stats:
    """ 取引結果から各種統計を計算 """
    def __init__(self, trades):
        self.trades = trades
        self._profits()
        self.r_multiples()
        self.percentages()
        
    def sum_profit(self):
        return sum(self.profits)
        
    def average_profit(self):
        if len(self.profits)==0: return 0
        return float(self.sum_profit())/len(self.profits)
    
    def wins(self):
        return sum( [1 for profit in self.profits if profit>0] )
    
    def losses(self):
        return sum( [1 for profit in self.profits if profit<0] )

    def draws(self):
        return sum( [1 for profit in self.profits if profit==0] )
    
    def winning_rate(self):
        if len(self.trades)==0: return 0
        return self.wins()/len(self.trades)
    
    def profit_factor(self):
        if self.losses()==0: return None
        else:
            total_profit = sum([profit for profit in self.profits if profit>0])
            total_loss = sum([profit for profit in self.profits if profit<0])
            return float(total_profit)/total_loss
    
    def sum_r(self):
        if self.r_multiples is not None: return sum(self.r_multiples)
        
    def average_r(self):
        if self.r_multiples is not None and len(self.r_multiples)!=0:
            return float(sum(self.r_multiples))/len(self.r_multiples)
        else: return 0
    
    def sum_percentage(self):
        return sum(self.percentages)
    
    def average_percentage(self):
        if len(self.percentages)==0: return 0
        return float(self.sum_percentage())/len(self.percentages)
       
    def average_length(self):
        lengths = [trade.length for trade in self.trades]
        if len(lengths)==0 or lengths is None: return 0
        return float(sum(lengths))/len(lengths)
       
    def _profits(self):
        self.profits = [ trade.profit() for trade in self.trades]
    
    def r_multiples(self):
        self.r_multiples = [ trade.r_multiple() for trade in self.trades ]
        
    def percentages(self):
        self.percentages = \
            [ trade.percentage_result() for trade in self.trades ]