# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../../indicator')
sys.path.append(os.getcwd()+'/../../')
from filter import Filter
from moving_average_direction import MovingAverageDirection

class MovingAverageDirectionFilter(Filter):
    """移動平均の方向フィルタークラス
    _前日の移動平均が上昇中の時は、買いからのみ入る
    _前日の移動平均が下降中の時は、売りからのみ入る
    _前日の移動平均がヨコバイの時は、仕掛ない
    """
    def __init__(self, params):
        self.span = params['span'] # n日移動平均のn
        
    def calculate_indicators(self):
        self.moving_average_direction = \
            MovingAverageDirection(self.stock, self.span).calculate_indicator('open')
    
    def filter(self, index):
        direction = self.moving_average_direction[index-1]
        if direction=='up': return 'long_only'
        elif direction=='down': return 'short_only'
        elif direction=='flat': return 'no_entry'