# coding: utf8
'''
Created on 2013/04/17

@author: n_shimada
'''

import sift
from PIL import Image
from pylab import *
import os

def process_image(imagename,resultname,params="--edge-thresh 10 --peak-thresh 4"):
    """ 画像を処理してファイルに結果を保存する """
    im = Image.open(imagename)  
    r, g, b = im.split() 

    for i in xrange(3):
        if imagename[-3:] != 'pgm': 
            # pgmファイルを作成する
            im = Image.open(imagename).convert('L')
            im.save('tmp_' + str(i) + '.pgm')
            imagename = 'tmp_'+ str(i) +'.pgm'
        cmmd = str("sift "+imagename+" --output="+resultname+'_' + str(i)+'.sift'+ " "+params) # 引数には.siftを付けないようにする
        os.system(cmmd)

    im = Image.merge("RGB", (b, g, r))
    print 'processed', imagename, 'to', resultname

if __name__ == '__main__':
    process_image('4l0le8.jpg', '4l0le8')
    
    