# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../../indicator')
sys.path.append(os.getcwd()+'/../../')
from stop import Stop
from average_true_range import AverageTrueRange
from tick import Tick

class AverageTrueRangeStop(Stop):
    """真の値幅の移動平均(ATR)に基づくストップクラス
    _仕掛値から
    _買いでは、n日間のATRのx倍下に
    _売りでは、n日間のATRのx倍上に
    _ストップを置く
    """
    def __init__(self, params):
        self.span = params['span'] # ATRの期間
        self.ratio = params['ratio'] if 'ratio' in params else 1 # ATRの何倍か
        
    def calculate_indicators(self):
        self.average_true_range = \
            AverageTrueRange(self.stock, self.span).calculate_indicator()
    
    def stop_price_long(self, position, index):
        """仕掛値からn日ATR（前日）のｘ倍下に行ったところにストップ"""
        _range = self._range(index)
        if _range!=_range: return _range
        return Tick.truncate(position.entry_price - _range)
    
    def stop_price_short(self, position, index):
        """仕掛値からn日ATR（前日）のｘ倍上に行ったところにストップ"""
        _range = self._range(index)
        if _range!=_range: return _range
        return Tick.ceil(position.entry_price + _range)
        
    def _range(self, index):
        return self.average_true_range[index -1]*self.ratio