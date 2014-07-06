# coding: utf8
'''
Created on 2013/05/07

@author: n_shimada
'''
""" reference
http://www.janeriksolem.net/
"""

import cv2
import cv2.cv as cv
import numpy as np
import imtools

class hough_circle(object):
    def __init__(self, imlist):
        self.imlist = imlist
        
    def main(self):
        self.get_circles()

    def get_circles(self):
        for imname in self.imlist:
            im_orig = cv2.imread(imname) # get image data
            im_gray = cv2.cvtColor(im_orig, cv2.COLOR_RGB2GRAY)
            img = cv2.GaussianBlur(im_gray, (9, 9), 0)
            
            # hough変換による円の描画
            #circles = cv2.HoughCircles(img, cv.CV_HOUGH_GRADIENT, 2, 10, np.array([]))
            circles = cv2.HoughCircles(img, cv.CV_HOUGH_GRADIENT, 2, 100, np.array([]), 40, 90, 10, 250)[0]
            if len(circles)>0:
                for x, y, radius in circles:
                    cv2.circle(img, (x,y), radius, (0,255,0), 2)
                    #cvCircle (src_img, cvPoint (cvRound (p[0]), cvRound (p[1])), cvRound (p[2]), CV_RGB (255, 0, 0), 3, 8, 0);
            cv2.imshow( "Result", img )
            cv2.waitKey()  
            cv2.destroyAllWindows()
        return 0

class hough_lines(object):
    def __init__(self, imlist):
        self.imlist = imlist
        
    def main(self):
        self.get_lines()
    
    def get_lines(self):
        for imname in self.imlist:
            im_orig = cv2.imread(imname) # get image data
            im_gray = cv2.cvtColor(im_orig, cv2.COLOR_RGB2GRAY)
            img = cv2.GaussianBlur(im_gray, (9, 9), 0)
            
            # edgeの取得
            edges = cv2.Canny(img, 1, 255)
            
            # 線分検出
            if len(edges)>0:
                plines = cv2.HoughLinesP(edges, 5, np.pi/180, 10, np.array([]), 1)[0]
            else: continue
            if len(plines)>0:
                for l in plines:
                    # red for line segments
                    cv2.line(img, (l[0],l[1]), (l[2],l[3]), (0,0,255), 2)
            cv2.imshow( "Result", img )
            cv2.waitKey()  
            cv2.destroyAllWindows()
        return 0
    
if __name__ == '__main__':
    imlist = imtools.get_imlist('nail_book03')
    
    lines = hough_lines(imlist)
    lines.main()
    
    """
    circle = hough_circle(imlist)
    circle.main()
    """