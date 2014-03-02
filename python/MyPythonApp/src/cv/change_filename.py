# coding: utf8
'''
Created on 2013/04/24

@author: n_shimada
'''
import glob
import os

txtlist = glob.glob('new_data\\*.jpg')
for x in xrange(len(txtlist)):
    name = 'new_data\\images'+'2'+('0'+str(x))[-2:]
    newname = name + u'.jpg'
    print newname
    os.rename(txtlist[x].decode('utf-8'),newname.decode('utf-8'))