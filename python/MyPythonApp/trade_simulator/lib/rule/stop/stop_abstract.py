# coding: utf-8

from stop import Stop

class StopRule(Stop):
    def __init__(self, params):
        """set parameters"""
        pass
        
    def calculate_indicators(self):
        """calculate technical indicators"""
        pass
    
    def stop_price_long(self,position,index):
        """買いポジションに対するストップの計算
        """
        pass
    
    def stop_price_short(self,index):
        """売りポジションに対するストップの計算
        """
        pass