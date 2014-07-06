# -*- coding: utf-8 -*-
'''
Created on 2013/04/23

@author: n_shimada
'''

import sys
import cv2
import cv2.cv as cv
from PIL import Image
from pylab import *
import numpy as np
from numpy import linalg

#im = cv2.imread('nail_book02\\4l0mgg.jpg')
im = cv2.imread('nail_book02\\4l0nt3.jpg')
#k = int(im.shape[1]/30) # 曲率計算時の片側の幅（計算の都合上偶数の必要がある）
k = 3
x=im.shape[1]; y=im.shape[0]
xy = im.shape
area = x*y

cv.XorS(im, cv.Scalar(255,255,255,0),im)

drawing = np.zeros(im.shape,np.uint8)      # Image to draw the contours
gray_img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
img = cv2.GaussianBlur(gray_img, (9, 9), 0)  

(thresh, bin_img) = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
print "bin_img", bin_img
cnt = sum(1*(bin_img==0)) 

print "cnt=",cnt,"area=",area,"ratio=",float(float(cnt)/area)


#cv2.imshow( "Result", bin_img )
cv2.imshow( "Result", im )
cv2.waitKey()  
cv2.destroyAllWindows()  




