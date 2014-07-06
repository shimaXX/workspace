# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../../indicator')
from entry import Entry
from estrangement import Estrangement

class EstrangementEntry(Entry):
    """前日の終値がn日移動平均からx%離れたら寄り付きで仕掛ける"""
    def __init__(self,params):
        self.span = params['span'] #n日移動平均のn
        self.rate = params['rate'] #n日移動平均からのr%乖離のr
        
    def calculate_indicators(self):
        self.estrangement = \
            Estrangement(self.stock, self.span).calculate_indicator('open')
            
    def check_long(self, index):
        if self.estrangement[index-1] < -self.rate:
            return self.enter_long(index, self.stock.open_prices()[index], 'open')

    def check_short(self, index):
        if self.estrangement[index-1] > self.rate:
            return self.enter_short(index, self.stock.open_prices()[index], 'open')