# coding: utf-8
'''
Created on 2013/11/28

@author: RN-017
'''

import numpy as np

class CalculateHammingWright(object):
    def calculate_jaccard(self,vector1,vector2):
        ''' ハミング重み計算後、jaccard係数の算出を行う '''
        print vector2
        print "sum:",sum( np.array(vector1)==np.array(vector2) )
        print "len:",len(vector1)
        print "res:",float( sum( np.array(vector1)==np.array(vector2) ) )/len(vector1)
        return float( sum( np.array(vector1)==np.array(vector2) ) ) \
                                                    /len(vector1) # len(vector1)はk次元と一致