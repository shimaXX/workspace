# -*- coding: utf-8 -*-

'''
Created on 2013/05/01

@author: n_shimada
'''
"""
using
https://projects.developer.nokia.com/opencv/browser/opencv/opencv-2.3.1/samples/python2/camshift.py?rev=ffd62ba23055b3d4b8ba068d5554e2760f0f0eea
"""
import numpy as np
import cv2

class App(object):
    def __init__(self, imlist):
        self.imlist = imlist
        cv2.namedWindow('camshift')
        #cv2.setMouseCallback('camshift', self.onmouse)

        self.selection = None
        self.drag_start = None
        self.tracking_state = 1
        self.show_backproj = False
    """
    def onmouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y]) # BUG
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.tracking_state = 0
        if self.drag_start: 
            if flags & cv2.EVENT_FLAG_LBUTTON:
                h, w = self.frame.shape[:2]
                xo, yo = self.drag_start
                x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y]))
                x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y]))
                self.selection = None
                if x1-x0 > 0 and y1-y0 > 0:
                    self.selection = (x0, y0, x1, y1)
            else:
                self.drag_start = None
                if self.selection is not None:
                    self.tracking_state = 1
    """
    
    def show_hist(self):
        bin_count = self.hist.shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count*bin_w, 3), np.uint8)
        for i in xrange(bin_count):
            h = int(self.hist[i])
            cv2.rectangle(img, (i*bin_w+2, 255), ((i+1)*bin_w-2, 255-h), (int(180.0*i/bin_count), 255, 255), -1)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('hist', img)

    def run(self):
        for imname in self.imlist:
            #ret, self.frame = self.cam.read()
            #vis = self.frame.copy()
            im = cv2.imread(imname)
            vis = im.copy()
            hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array((0, 60, 32)), np.array((180, 255, 255)))
            y = im.shape[0]; x = im.shape[1]
            y_cnt =int(0.5*y); x_cnt =int(0.5*x)
            range_y = int(y*0.1); range_x = int(x*0.1)
            x0 =x_cnt-range_x; y0 = y_cnt-range_y
            x1 =x_cnt+range_x; y1 = y_cnt+range_y

            #hsv_roi = hsv[y0:y1, x0:x1]
            #mask_roi = mask[y0:y1, x0:x1]
            self.track_window = (x0, y0, x1-x0, y1-y0)
            hsv_roi = hsv[y0:y1, x0:x1]
            mask_roi = mask[y0:y1, x0:x1]
            hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
            self.hist = hist.reshape(-1)
            self.show_hist()
       
            vis_roi = vis[y0:y1, x0:x1]
            cv2.bitwise_not(vis_roi, vis_roi) # 色の反転
            vis[mask == 0] = 0

            prob = cv2.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
            prob &= mask
            term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
            #track_box, self.track_window = cv2.CamShift(prob, self.track_window, term_crit)
           
            if self.show_backproj:
                vis[:] = prob[...,np.newaxis]
            """
            try: cv2.ellipse(vis, track_box, (0, 0, 255), 2)
            except: print track_box
            """
               
            cv2.imshow('camshift', vis)

            ch = cv2.waitKey(5)
            #cv2.destroyAllWindows()
            if ch == 27:
                break
            if ch == ord('b'):
                self.show_backproj = not self.show_backproj


if __name__ == '__main__':
    import sys
    import imtools
    imlist = imtools.get_imlist('nail_book03')
    App(imlist).run()