# coding: utf-8

from filter import Filter

class FilterRule(Filter):
    def __init__(self, params):
        """set parameters"""
        pass
        
    def calculate_indicators(self):
        """calculate technical indicators"""
        pass
    
    def filter(self,index):
        """ 'no_entry, 'long_only, 'short_only', 'long_and_short'の
        _いずれかを返す
        """
        pass