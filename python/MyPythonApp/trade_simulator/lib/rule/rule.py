# coding: utf-8

class Rule:
    """ 各ルールの親クラス """    
    stock = None
    def calculate_indicatiors(self):
        pass
    
    def _with_valid_indicators(self,value):
        """ if value include raise then except. """
        try:
            return value
        except Exception, e:
            return None