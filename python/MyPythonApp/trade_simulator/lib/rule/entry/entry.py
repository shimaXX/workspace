# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../rule')
sys.path.append(os.getcwd()+'/../../lib')
from rule import Rule
from trade import Trade

class Entry(Rule):
    def check_long_entry(self,index):
        return self._with_valid_indicators(self.check_long(index))
    
    def check_short_entry(self,index):
        return self._with_valid_indicators(self.check_short(index))
        
    def _enter(self, index, price, long_short, entry_time):
        try:
            dt = self.stock.dates()[index]
        except:
            dt = None
        
        params = {'stock_code':self.stock.code,
                  'trade_type':long_short,
                  'entry_date':dt,
                  'entry_price':price,
                  'entry_time':entry_time}
        return Trade(params)
    
    def enter_long(self,index,price,entry_time):
        return self._enter(index, price, 'long', entry_time)
    
    def enter_short(self,index,price,entry_time):
        return self._enter(index, price, 'short', entry_time)