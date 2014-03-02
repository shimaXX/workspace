# coding: utf8
'''
Created on 2013/04/10

@author: n_shimada
'''
import os
from os import path
import sys
sys.path.append('C:/workPyth/Mypython/cv')
import sift
from PIL import Image
import numpy as np
from pylab import *

#c_path = str(os.getcwd())
c_path = "C:/workPyth/MyPython/cv/"
imname = os.path.join(c_path, "4l0le8.jpg")
print imname
im1 = np.array(Image.open(imname).convert('L'))
try:
    sift.process_image(imname,"4l0le8.sift")
except Exception, e:
    import sys
    import traceback
    sys.stderr.write(traceback.format_exc())

l1, d1 = sift.read_features_from_file("4l0le8.sift")

figure()
gray()
sift.plot_features(im1, l1, circle = True)
show()