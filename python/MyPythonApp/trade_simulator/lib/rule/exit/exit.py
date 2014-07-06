# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../rule')
sys.path.append(os.getcwd()+'/../../lib')
from rule import Rule
import trade

class Exit(Rule):
    def check_exit(self,trade, index):
        if trade.islong():
            return self._with_valid_indicators(self.check_long(trade, index))
        elif trade.isshort():
            return self._with_valid_indicators(self.check_short(trade, index))
            
    def _exit(self, trade, index, price, time):
        try:
            dt =self.stock.dates()[index]
        except:
            dt = None
        
        params = {'exit_date':dt,
                  'exit_price':price,
                  'exit_time':time}
        trade.exit(params)