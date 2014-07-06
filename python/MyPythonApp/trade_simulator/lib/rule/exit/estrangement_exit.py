# coding:utf-8

import sys, os
sys.path.append(os.getcwd()+'/../../indicator')
from exit import Exit
from estrangement import Estrangement

class EstrangementExit(Exit):
    """移動平均乖離率による手仕舞いクラス
    _前日の終値がn日移動平均からx%以内のとき寄り付きで手仕舞う
    """
    
    def __init__(self,params):
        self.span = params['span'] #n日移動平均のn
        self.rate = params['rate'] #n日移動平均からのr%乖離のr
        
    def calculate_indicators(self):
        self.estrangement = \
            Estrangement(self.stock, self.span).calculate_indicator('open')
            
    def check_long(self, trade, index):
        if self.estrangement[index-1] > -self.rate:
            self._exit(trade, index, self.stock.open_prices()[index], 'open')
        else:
            return 'no_exit'

    def check_short(self, trade, index):
        if self.estrangement[index-1] < self.rate:
            self._exit(trade , index, self.stock.open_prices()[index], 'open')
        else:
            return 'no_exit'