# coding: utf-8

import sys,os
sys.path.append(os.getcwd()+'/../rule')
sys.path.append(os.getcwd()+'/../../lib')
from rule import Rule

class Stop(Rule):
    def get_stop(self,position, index):
        if position.islong():
            return self._with_valid_indicators(
                    self.stop_price_long(position, index))
        elif position.isshort():
            return self._with_valid_indicators(
                    self.stop_price_short(position, index))