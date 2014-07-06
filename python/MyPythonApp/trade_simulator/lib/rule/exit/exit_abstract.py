# coding:utf-8

from exit import Exit

class ExitRule(Exit):
    def __init__(self, params):
        """set parameters"""
        pass
    
    def calculate_indicators(self):
        """calculate technical indicators"""
        pass
    
    def check_long(self,index):
        """買いポジションの手仕舞いチェック
        _手仕舞いが発生していれば、exit(trade, index, price, entry_time)
        _で手仕舞う
        """
        pass
    
    def check_short(self,index):
        """売りポジションの手仕舞いチェック
        _手仕舞いが発生していれば、exit(trade, index, price, time)
        _で手仕舞う
        """
        pass