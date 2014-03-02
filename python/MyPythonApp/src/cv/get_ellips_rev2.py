# coding: utf8
'''
Created on 2013/04/12

@author: nahki
'''

import cv2
import cv2.cv as cv
from PIL import Image
from pylab import *
import numpy as np
from numpy import linalg

im = cv2.imread('4l0mgg.jpg')
#k = int(im.shape[1]/30) # 曲率計算時の片側の幅（計算の都合上偶数の必要がある）
k = 3
x=im.shape[1]; y=im.shape[0]
x_pad = int(x*0.2); y_pad = int(y*0.2)
im2 = im[y_pad:(y-y_pad),x_pad:(x-x_pad),:] 
#im2[0:x_pad,:,:] =0; im2[x-x_pad:x,:,:] =0
#im2[:,0:y_pad,:] =0; im2[:,y-y_pad:y,:] =0

"""
cv2.imshow( "Result", im2 )
cv2.waitKey()  
cv2.destroyAllWindows()  
"""

drawing = np.zeros(im.shape,np.uint8)      # Image to draw the contours
gray_img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
img = cv2.GaussianBlur(gray_img, (9, 9), 0)  
"""
cv2.imshow( "Result", img )
cv2.waitKey()  
cv2.destroyAllWindows()  
"""
(thresh, bin_img) = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)

# stor = cv.CreateMemStorage()
# cv2.CHAIN_APPROX_TC89_L1によりTeh-Chinチェーンの近似アルゴリズムに基づいて近似した線の折れ線の角の座標を取得
contours, hierarchy = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
area = np.array( [cv2.contourArea(np.array(contours[i])) for i in xrange(len(contours))] ) # 輪郭線内の面積の取得
max_cnt = np.where(area==np.max(area))[0]
max_contour = contours[max_cnt]
print "max_contour",max_contour
 
#with open('contours','w') as f:
#    nums = [str(max_contour[i]) for i in xrange(len(max_contour))]
#    f.write((",".join(nums))+"\n") 
 
ellp_point = []
for i in xrange( k,len(max_contour)-k ):
    A = max_contour[i-1] - max_contour[i]
    A = np.ndarray.flatten(A)
    B = max_contour[i+1] - max_contour[i]
    B = np.ndarray.flatten(B)
    distA =linalg.norm(A); distB = linalg.norm(B)
    if 0<= np.dot(A,B)/(distA*distB) <= 1 and np.cross(A,B) >= 0: ellp_point.append(max_contour[i-k:i+k]) 

# 曲率半径の計算
"""
curvature = []
for i in xrange( k, len(max_contour)-k ):
    d_maina = 1.0/(2*k)*(np.sum( (max_contour[-k+i:i-1,:,1] - max_contour[-k+1+i:i,:,1])/
                                (max_contour[-k+i:i-1,:,0] - max_contour[-k+1+i:i,:,0] + 1e-9)) )
    d_pulas = 1.0/(2*k)*(np.sum( (max_contour[i:k+i-1,:,1] - max_contour[i+1:k+i,:,1])/
                                (max_contour[i:k+i-1,:,0] - max_contour[i+1:k+i,:,0] + 1e-9)) )
    d_pm = 1.0/(2*k)*(np.sum( (max_contour[-k/2+i:k/2+i,:,1] - max_contour[-k/2+i+1:k/2+i+1,:,1])/
                                (max_contour[-k/2+i:k/2+i,:,0] - max_contour[-k/2+i+1:k/2+i+1,:,0] + 1e-9)) )
    d2 = d_pulas - d_maina
    d1 = d_pm
    kappa = d2/(1.0+d1**2)**(3/2) + 1e-9
    #print kappa 
    law = 1/kappa
    #print law
    if 1 <= law <= 500 : curvature.append(max_contour[i-k:i+k,:,:])
#print curvature
"""
# エッジを一定の幅で区切って楕円フィッティング
"""
curvature = []
for c in contours:
    if len(c) >= 2*k:
        for i in xrange( k, len(c)-k ):
            drawing = np.zeros(im.shape,np.uint8)
            if sqrt((np.average(c[-k+i:k+i,:,0]) - c[i,:,0])**2) < 3:
                if sqrt((np.average(c[-k+i:k+i,:,1]) - c[i,:,1])**2) < 3:
                    ellp = cv2.fitEllipse(c[-k+i:k+i,:,:])
                    cv2.ellipse(drawing, ellp, (0,0,255), 2)
                    cv2.drawContours(drawing,[c],0,(0,255,0),2)
                    #cv2.imshow( "Result", drawing )
                    #cv2.waitKey()  
                    #cv2.destroyAllWindows()  
                    a = ellp[1][0]; b = ellp[1][1]
                    r = (b**2)/(a+1e-9)
                    if 2 <= r <= 500: curvature.append(max_contour[i-k:i+k,:,:])
print curvature
"""
# エッジに円をフィッティング
curvature = []
for c in contours:
    if len(c) >= 2*k:
        for i in xrange( k, len(c)-k ):
            drawing = np.zeros(im.shape,np.uint8)
            if sqrt((np.average(c[-k+i:k+i,:,0]) - c[i,:,0])**2) < 10:
                if sqrt((np.average(c[-k+i:k+i,:,1]) - c[i,:,1])**2) < 10:
                    L = sqrt( (c[-k+i,:,0] - c[k+i,:,0])**2 + (c[-k+i,:,1] - c[k+i,:,1])**2 )
                    d = sqrt( ((c[-k+i,:,0] + c[k+i,:,0])/2 + c[i,:,0])**2 +
                               ((c[-k+i,:,1] + c[k+i,:,1])/2 + c[i,:,1])**2 )
                    R = (L**2/4 + d**2)/(2*d) # 円の半径
                    
                    # 円の中心を求める
                    a = (c[-k+i,:,1] - c[k+i,:,1])/(c[-k+i,:,0] - c[k+i,:,0] + 1e-9)
                    y0 = c[i,:,1] - R/sqrt(1 + a**2 + 1e-9)
                    x0 = c[i,:,0] + a*(c[i,:,1] - y0)
                    center = (x0, y0)
                    print center
                    ellp = cv2.fitEllipse(c[-k+i:k+i,:,:])
                    cv2.ellipse(drawing, ellp, (0,0,255), 2)
                    cv2.drawContours(drawing,[c],0,(0,255,0),2)
                    cv2.circle(drawing, center, R, (255,0,0), 2)
                    cv2.imshow( "Result", drawing )
                    cv2.waitKey()  
                    cv2.destroyAllWindows()                      
#print curvature

ellp_param = []
box_param = []
itr = 0
keep = 0
max_area = 0
drawing = np.zeros(im.shape,np.uint8)
for c in contours:
#for c in curvature:
#print max_contour
#for c in max_contour:
#    c=max_contour
    # Number of points must be more than or equal to 6 for cv.FitEllipse2
    if  6 <= len(c) <=100000:
        #center, axis, angle = cv2.fitEllipse(c)
        ellp = cv2.fitEllipse(c)
        """
        if min(ellp[1]) > max(im.shape)/10 :continue
        if max(ellp[1]) > max(im.shape)/3 :continue
        if max(ellp[1]) < max(im.shape)/50 :continue
        if ellp[0][1] < im.shape[0]/5 or ellp[0][1] > (im.shape[0] - im.shape[0]/5):continue # y座標
        if ellp[0][0] < im.shape[1]/5 or ellp[0][0] > (im.shape[1] - im.shape[1]/5):continue # x座標
        """
        rect = cv2.minAreaRect(c)             # rect = ((center_x,center_y),(width,height),angle)
        points = cv2.cv.BoxPoints(rect)         # Find four vertices of rectangle from above rect
        points = np.int0(np.around(points))     # Round the values and make it integers
        """
        ellp_param.append(ellp)
        box_param.append(points)
        area = ellp[1][0]*ellp[1][1]
        if area > max_area:
            max_area = area
            keep = itr
        itr += 1
        """
        #c[:,:,0] += x_pad; c[:,:,1] += y_pad
        points[:,0] += x_pad; points[:,1] += y_pad       
        cv2.drawContours(drawing,[c],0,(0,255,0),2)     # draw contours in green color
        cv2.ellipse(drawing, ellp, (0,0,255), 2)        # draw ellipse in red color. last arg(-1) is fill into the ellipse
        cv2.polylines(drawing,[points],True,(255,0,0),2)# draw rectangle in blue color
# Show image. HighGUI use.
"""
x_max = max(box_param[keep][:,0]); x_min = min(box_param[keep][:,0])
y_max = max(box_param[keep][:,1]); y_min = min(box_param[keep][:,1])
span_x = int((x_max - x_min)*0.35); span_y = int((y_max - y_min)*0.35)
# check x range
if box_param[keep][2,0] + span_x <= x: box_param[keep][2,0] += span_x
else: box_param[keep][2,0] = x
if box_param[keep][3,0] + span_x <= x: box_param[keep][3,0] += span_x
else: box_param[keep][3,0] = x
if box_param[keep][0,0] - span_x >= 0: box_param[keep][0,0] -= span_x
else: box_param[keep][0,0] = 0
if box_param[keep][1,0] - span_x >= 0: box_param[keep][1,0] -= span_x
else: box_param[keep][1,0] = 0

# check y range
if box_param[keep][0,1] + span_y <= y: box_param[keep][0,1] += span_y
else: box_param[keep][0,1] = y
if box_param[keep][1,1] + span_x <= y: box_param[keep][1,1] += span_y
else: box_param[keep][1,1] = y
if box_param[keep][2,1] - span_y >= 0: box_param[keep][2,1] -= span_y
else: box_param[keep][2,1] = 0
if box_param[keep][3,1] - span_y >= 0: box_param[keep][3,1] -= span_y
else: box_param[keep][3,1] = 0
 
cv2.fillPoly(drawing,[box_param[keep]],255) # draw rectangle in blue color
mask = np.array( cv2.cvtColor(drawing, cv2.COLOR_BGR2GRAY) )
tmp = np.array(im)
#np.array(tmp)[:,:,0] = np.array(tmp)[:,:,[mask<0]] = 0
tmp[:,:,0] = tmp[:,:,0]*(1*(mask>0))
tmp[:,:,1] = tmp[:,:,1]*(1*(mask>0))
tmp[:,:,2] = tmp[:,:,2]*(1*(mask>0))
"""
cv2.imshow( "Result", drawing )
cv2.waitKey()  
cv2.destroyAllWindows()  
#cv2.imwrite('bw_image.png', bin_img)