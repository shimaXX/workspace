# -*- coding: utf-8 -*-
'''
Created on 2013/04/23

@author: n_shimada
'''

import  cv2.cv as cv
import  cv2
import sys
import numpy as np
import imtools
import math
import pickle
import BackProject
from PIL import Image


batch = 5

def main_get_dist(imlist):
    """ fHSVによって取得した画像を距離変換画像に変換し、最大領域を取る """
    area = []
    for imname in imlist:
        im = cv2.imread(imname)
        
        """
        # ヒストグラム平滑化を行う
        r, g, b = cv2.split(im)
        
        eq_r = cv2.equalizeHist(r)
        eq_g = cv2.equalizeHist(g)
        eq_b = cv2.equalizeHist(b)
        im2 = cv2.merge( (eq_r, eq_g, eq_b) )
        
        '''
        cv2.imshow( "Result", im2 )
        cv2.waitKey()  
        cv2.destroyAllWindows() 
        '''
        """
        img = cv2.GaussianBlur(im, (9, 9), 0) # 平滑化をするときはim2に変更

        mask = np.zeros(img.shape, np.uint8) # HSVのmask画像の枠を定義しておく
        dst = np.zeros(img.shape, np.uint8)
        
        # 修正HSVでmaskする
        get_mask_hsv(img, mask, 1, 1);
        dst=im*(mask==255)
        
        # 手の領域のみ取得
        im_area =  get_hand_area(dst)
        ratio = float(im_area)/(im.shape[0]*im.shape[1]) 
        area.append(ratio)

    area = np.array(area)
    flag = 1*(area>=0.3)
    flag = flag.tolist() # 何故かtolist()は別に記述しないとbooleanになる
    print area
    print flag
    num = map(str,flag)
    with open('hsv_flag___.csv','w') as f:
        # 書き込み
        #f.writelines(num)
        f.write(",".join(num)+"\n")


def main_get_hist(imlist):
    hist = []
    """ 修正HSVのHSV毎の色のbin(10刻み)のヒストグラムを取得する """
    for imname in imlist:
        im = cv2.imread(imname)
        img = cv2.GaussianBlur(im, (9, 9), 0)    
        # 修正HSVの色ヒストグラムの取得
        hist.append(get_hist(img))
    np.array(hist)
    np.savetxt('fHSV_hist.txt', hist)

    
def get_hist(im):
    p_src = cv2.split(im)

    # 修正HSVではなく普通のHSVで使うやつ
    """
    H = p_src[0]    # 0から180
    S = p_src[1]
    V = p_src[2] 
    """
    H, S, V = BGR2fHSV(im) # 修正HSVの取得    
    p_src[0]= H; p_src[1]= S; p_src[2]= V # 修正HSVに入れ替える

    return get_hist_fHSV(p_src) # ヒストグラムを返す
  

def main_get_masked_image(imlist):
    """ 肌色部分以外をマスクした画像を取得する """
    result = []    
    for imname in imlist:
        im = cv2.imread(imname)
        drawing = np.zeros(im.shape,np.uint8)
        
        img = cv2.GaussianBlur(im, (9, 9), 0)

        contour = get_contours(im,drawing) # detection edges
        mask = np.zeros(img.shape, np.uint8) # HSVのmask画像の枠を定義しておく
        mask_YCbCr = np.zeros(img.shape, np.uint8) # YCbCrのmask画像の枠を定義しておく
        dst = np.zeros(img.shape, np.uint8)
        dst_YCbCr = np.zeros(img.shape, np.uint8)
        
        #　YCbCrでmaskする
        """
        get_mask_YCbCr(img, mask_YCbCr)
        dst_YCbCr=im*(mask_YCbCr==255)
        '''
        cv2.imshow( "Result_YCbCr", dst_YCbCr )
        cv2.waitKey()  
        cv2.destroyAllWindows()  
        '''
        """
        
        # 修正HSVでmaskする
        #get_mask_hsv(dst_YCbCr, mask, 1, 1);
        get_mask_hsv(img, mask, 1, 1);
        dst=im*(mask==255)
        """
        cv2.imshow( "Result_fHSV", dst )
        cv2.waitKey()  
        cv2.destroyAllWindows() 
        """
    
        # overlay the edge image on detection image
        """
        #dst=dst*(contour==0) + im*(contour>0) # エッジの中は元画像を使用する
        dst=dst*(contour>0) # エッジの外を黒く塗りつぶす
        cv2.imshow( "Result", dst )
        cv2.waitKey()  
        cv2.destroyAllWindows() 
        """

        # complement color surrounding eceed 4
        #complement_color(dst)
        """
        # 肌色面積が全体の面積の30%を超えた場合は手があるとするためのcode
        tmp = ((dst[:,:,0]>0) + (dst[:,:,1]>0) + (dst[:,:,2]>0))
        area = dst.shape[0]*dst.shape[1]
        
        #print float(np.sum(1*(tmp>0)))/area
        
        # 結果を格納
        result.append( 1 if float(np.sum(1*(tmp>0)))/area > 0.30 else -1 )
        """
        
        
def get_hand_area(im):
    im_tmp = im.copy()
    drawing = np.zeros(im.shape)
    drw_mat = np.zeros(im.shape)[:,:,0]
    gray_img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    #mark = cv2.Canny(im, 1, 255)
    (thresh, bin_img) = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(bin_img, cv2.RETR_LIST, cv2.CHAIN_APPROX_TC89_L1)
    #contours = get_hand_contours(im) # using edges
    # 距離変換
    im_dist = cv2.distanceTransform(bin_img, cv.CV_DIST_L2, cv.CV_DIST_MASK_PRECISE)
    """
    cv2.imshow( "Result", im_dist )
    cv2.waitKey(6)
    """  
    
    # 0-255に正規化
    #dst = cv2.normalize(im_dist)

    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(im_dist) # maxLoc=(x,y)
    for c in contours:
        if len(c) < 20: continue # 点が少なすぎる場合ははじく
        cv2.drawContours(drawing,[c],0,(0,255,0),-2)     
        # 最大点を中に含んでいれば
        tmp_im =  np.array(drawing[:,:,1])
        drw_mat = cv.fromarray(tmp_im)
        if maxLoc[0]>=0 and maxLoc[1]>=0 and \
            maxLoc[0]<=im.shape[1] and maxLoc[1]<=im.shape[0]:  
            if cv.GetReal2D(drw_mat, maxLoc[1], maxLoc[0]): # cvGetReal2D( 入力画像, y, x )
                contour_max = c
                break
    
    dst = np.asarray(drw_mat)
    """
    cv2.imshow( "Result", dst )
    cv2.waitKey(5)
    """
    area = np.sum(1*(dst>0))
    return area

def get_hand_contours(img):
    # Split out each channel
    blue = cv2.split(img)[0]
    green = cv2.split(img)[1]
    red = cv2.split(img)[2]
    
    # Run canny edge detection on each channel
    blue_edges = cv2.Canny(blue, 1, 255)
    green_edges = cv2.Canny(green, 1, 255)
    red_edges = cv2.Canny(red, 1, 255)
    
    # Join edges back into image
    edges = blue_edges | green_edges | red_edges
    #edge = cv2.Canny(gray_img, 1, thresh)
    contours,hierarchy = cv2.findContours(edges.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    return contours

         
def get_contours(im,drawing):
    """ エッジを取得する """
    #img = cv2.GaussianBlur(im, (5, 5), 0)
    img = cv2.GaussianBlur(im, (3, 3), 0) 
    #(thresh, bin_img) = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY|cv2.THRESH_OTSU)
    
    # Split out each channel
    blue = cv2.split(img)[0]
    green = cv2.split(img)[1]
    red = cv2.split(img)[2]
    
    # Run canny edge detection on each channel
    blue_edges = cv2.Canny(blue, 1, 255)
    green_edges = cv2.Canny(green, 1, 255)
    red_edges = cv2.Canny(red, 1, 255)
    
    # Join edges back into image
    edges = blue_edges | green_edges | red_edges
    #edge = cv2.Canny(gray_img, 1, thresh)
    contours,hierarchy = cv2.findContours(edges.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    #area = np.array( [cv2.contourArea(np.array(contours[i])) for i in xrange(len(contours))] ) # 輪郭線内の面積の取得
    #max_cnt = np.where(area==np.max(area))[0]
    #max_contour = contours[max_cnt]

    # 凸包計算 
    hull = [cv2.convexHull(c) for c in contours]
    #hull = cv2.convexHull(max_contour)
    
    """
    # エッジの記述
    for c in contours:
        cv2.drawContours(drawing,[c],0,(128,128,128),-2)
    """
    # forは hull から値を取り出している
    for h in hull:
        cv2.fillConvexPoly(drawing, h, (128,128,128)) 
    
    """
    cv2.imshow( "Result", drawing )
    cv2.waitKey()  
    cv2.destroyAllWindows()
    """    
    return drawing

def get_mask_hsv(im, mask, erosions=1, dilations=1):
    """ default values
    minH = 100;    maxH = 115
    minS = 80;    maxS = 255
    minV = 120;    maxV = 255
    """
    minH = 50;    maxH = 180 # 色相、red。修正HSVの場合はGreen系？ def=180
    minS = 50;    maxS = 150 # 彩度、yellow 150
    minV = 50;    maxV = 150 # 輝度 def=150

    tmp = cv2.cvtColor(im, cv.CV_RGB2HSV) # RGB → HSV
    
    p_src = cv2.split(tmp) # 元画像RGBのimを。HVSの場合はtmpとする。修正HSVとする場合はimでよい。
    p_dst = cv2.split(tmp) # マスク用に変更する画像

    # 修正HSVではなく普通のHSVで使うやつ
    """
    H = p_src[0]    # 0から180
    S = p_src[1]
    V = p_src[2] 
    """
    H, S, V = BGR2fHSV(im) # 修正HSVの取得    
    
    p_dst[0]= H; p_dst[1]= S; p_dst[2]= V
    
    hist = get_hist_fHSV(p_dst)
    
    p_dst[0] = 255*(minH <= H)*(H <= maxH)*(minS <= S)*(S <= maxS)*(minV <= V)*(V <= maxV)
    p_dst[1] = 255*(minH <= H)*(H <= maxH)*(minS <= S)*(S <= maxS)*(minV <= V)*(V <= maxV)
    p_dst[2] = 255*(minH <= H)*(H <= maxH)*(minS <= S)*(S <= maxS)*(minV <= V)*(V <= maxV)
    
    mask[:,:,0] = p_dst[0]; mask[:,:,1] = p_dst[1]; mask[:,:,2] = p_dst[2];

    # 細かいノイズを取り除く
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    cv2.dilate( np.uint8(mask), element )
    cv2.erode(np.uint8(mask), element)

def get_hist_fHSV(fHSV_im):
    hist = [[],[],[]] # histの初期化

    # 量子化の枠を作る
    itr =0
    for p in fHSV_im:
        hist[itr] = [np.sum( 1*(p>=10*i)*(p<10*(i+1)) ) for i in xrange(1,26)]        
        hist[itr].insert( 0, np.sum(1*(p<10)) )
        #hist[itr] = np.float32( hist[itr] )/max(hist[itr])
        itr += 1
    return np.array(hist).flatten() # listを開いたやつを返す
    

def get_mask_YCbCr(im, mask_YCbCr):
    minH = 80;    maxH = 220 
    minS = 65;    maxS = 220 
    minV = 65;    maxV = 220 

    tmp = cv2.cvtColor(im, cv.CV_BGR2YCrCb) # RGB → YCrCb
    
    p_src = cv2.split(tmp) # 元画像RGBのimを。HVSの場合はtmpとする。修正HSVとする場合はimでよい。
    p_dst = cv2.split(tmp) # マスク用に変更する画像

    # 修正HSVではなく普通のHSVで使うやつ
    H = p_src[0]    # 0から180 
    S = p_src[1]
    V = p_src[2] 

    p_dst[0] = 255*(minH <= H)*(H <= maxH)*(minS <= S)*(S <= maxS)*(minV <= V)*(V <= maxV)
    p_dst[1] = 255*(minH <= H)*(H <= maxH)*(minS <= S)*(S <= maxS)*(minV <= V)*(V <= maxV)
    p_dst[2] = 255*(minH <= H)*(H <= maxH)*(minS <= S)*(S <= maxS)*(minV <= V)*(V <= maxV)
    
    mask_YCbCr[:,:,0] = p_dst[0]; mask_YCbCr[:,:,1] = p_dst[1]; mask_YCbCr[:,:,2] = p_dst[2];

    # 細かいノイズを取り除く
    element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    cv2.dilate( np.uint8(mask_YCbCr), element )
    cv2.erode(np.uint8(mask_YCbCr), element)

    
def BGR2fHSV(im):
    """ 修正HSVの値を取得する """
    p_src = cv2.split(im) # 元画像RGBのimを。HVSの場合はtmpとする。修正HSVとする場合はimでよい。
    # 修正HVSを作成する
    r = np.float32(p_src[0]); g = np.float32(p_src[1]); b = np.float32(p_src[2])
    
    # calculate
    Qc = np.sqrt( (r-g)*(r-g)+(r-b)*(g-b) )
    H = np.arccos( ((r-g)+(r-b))/(2.0*Qc + 1e-9) )
    H=(2*math.pi-H)*(b>g)
    H=(H*255.0)/(2.0*math.pi);
    I = (r+g+b)/3 # 修正HSVのI
      
    return H, Qc, I


def complement_color(im):
    width = im.shape[1]; height = im.shape[0]
    
    for y in xrange(batch,height-batch):
        nbk_flg = 0 # check the first collared cell
        bk_cnt = 0 # count number of blank between the specified span
        for x in xrange(batch,width-batch):
            # complement surround
            if np.sum(im[y,x,0])==0 and np.sum(1*im[y-batch:y+batch,x-batch:x+batch,0]>0) >=10:
                im[y,x,:] = np.average(im[y-batch:y+batch,x-batch:x+batch,:]*(im[y-batch:y+batch,x-batch:x+batch,:]>0))
            
            # complement line
            if np.sum(im[y,x-1,0])>40 and np.sum(im[y,x,0])==0: nbk_flg=1
            if nbk_flg ==1 and np.sum(im[y,x,0])==0: bk_cnt += 1
            elif np.sum(im[y,x,0])>40 and 0< bk_cnt <= batch*100:
                print  "bk_cnt",bk_cnt
                print "pre_im[y,x-bk_cnt:x-1,:]",im[y,x-bk_cnt:x-1,:]
                im[y,x-bk_cnt:x-1,:] = (im[y,x-(bk_cnt+1),:] + im[y,x,:])/2
                print "pro_im[y,x-bk_cnt:x-1,:]",im[y,x-bk_cnt:x-1,:]
                
                bk_cnt = 0
                nbk_flg = 0
            elif np.sum(im[y,x,0])>40 and bk_cnt > batch*100: bk_cnt = 0; nbk_flg = 0
    
    #cv2.pointPolygonTest(contour, )   CvPoint2D32f pt, int measure_dist );
    """
    cv2.imshow( "Result", im )
    cv2.waitKey()  
    cv2.destroyAllWindows()   
    """

if __name__ == '__main__':
    imlist = imtools.get_imlist('nail_book03')
    print len(imlist)
    #main_get_hist(imlist) # 判別条件 "=IF(AND(A8=1,A2<-0.3),-1,IF(AND(A8=1,A2>-0.3),1,A8))"
    main_get_dist(imlist)