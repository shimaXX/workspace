# coding: utf-8

import sys, os
sys.path.append(os.getcwd()+'/../rule')
sys.path.append(os.getcwd()+'/../../lib')
from rule import Rule

class Filter(Rule):
    def get_filter(self, index):
        return self._with_valid_indicators(self.filter(index))