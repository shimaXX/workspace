# coding:utf-8

from entry import Entry

class EntryRule(Entry):
    def __init__(self, params):
        """set parameters"""
        pass
    
    def calculate_indicators(self):
        """calculate technical indicators"""
        pass
    
    def check_long(self,index):
        """買い仕掛けのチェック
        _仕掛け発生なら、enter_long(index, price, entry_time)
        _で仕掛ける
        """
        pass
    
    def check_short(self,index):
        """売り仕掛けのチェック
        _仕掛け発生なら、enter_short(index, price, entry_time)
        _で仕掛ける
        """
        pass