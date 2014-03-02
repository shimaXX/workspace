#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import *
from scipy.cluster.vq import *
import sift
import numpy as np
import pickle
#import cv2


class Vocabulary(object):

  def __init__(self,name):
    self.name = name
    self.voc = []
    self.idf = []
    self.trainingdata = []
    self.nbr_words = 0

  def train(self,featurefiles,k=100,subsampling=10):
    """ featurefilesに列挙されたファイルから特徴量を読み込み
      k平均法とk個のビジュアルワードを用いてボキャブラリを
      学習する。subsamplingで教師データを間引いて高速化可能 """

    nbr_images = len(featurefiles)
    # ファイルから特徴量を読み込む
    #points = []
    descr = []
    descr.append(sift.read_features_from_file(featurefiles[0])[1])
    # optional.view feature points.
    #points.append( np.array(sift.read_features_from_file(featurefiles[0])[0][:,0:2]) ) # stock of x,y axis value
    descriptors = descr[0] #stack all features for k-means
    #pointors = points[0]
    for i in arange(1,nbr_images):
      descr.append(sift.read_features_from_file(featurefiles[i])[1])
      #points.append( np.array(sift.read_features_from_file(featurefiles[i])[0][:,0:2]) ) # stock of x,y axis value
      descriptors = vstack((descriptors,descr[i]))
    
    # k平均法：最後の数字で試行数を指定する
    self.voc,distortion = kmeans(descriptors[::subsampling,:],k,1)
    self.nbr_words = self.voc.shape[0]
    
    # 重心を保存しておく
    with open('voc_centroid.pkl','wb') as f:
        pickle.dump(self.voc,f)
    """
    # ワードとx,y座標の辞書作成
    dic = []
    for i in xrange(len(nbr_images)):
        dic[i] = {}
        dic[i][]
    """
    
    # 教師画像を順番にボキャブラリに射影する
    imwords = zeros((nbr_images,self.nbr_words))
    for i in xrange(1): #xrange( nbr_images ):
      # imwords[i] = self.project(descr[i], points[i]) # PLSAを使う場合はこちらを使用する
      imwords[i] = self.project(descr[i])

    nbr_occurences = sum( (imwords > 0)*1 ,axis=0)

    self.idf = log( (1.0*nbr_images) / (1.0*nbr_occurences+1) )
    self.trainingdata = featurefiles

#  def project(self,descriptors, pointors): # 領域を表示させるためにpointorsを書き加えている。通常は不要。
  def project(self,descriptors):
    """ 記述子をボキャブラリに射影して、
        単語のヒストグラムを作成する """
    #drawing = zeros((1000,1000))    
    dic = {}
    # ビジュアルワードのヒストグラム
    imhist = zeros((self.nbr_words))
    words,distance = vq(descriptors,self.voc)
    """
    tmp = list(set(words)) # 重複を排除したwordsを取得
    words = np.array(words)
    index = []
    for t in tmp:
      tmp_d = []
      index.append( np.where( words == t)[0] )
      for i in index:
        tmp_d.append([pointors[i,:]])
      dic[t] = tmp_d
      tmp_d = np.array(dic[t])
      dic[t] = np.sort(tmp_d, axis = 0)
      print dic[t]
      cv2.drawContours(drawing,dic[t],0,(0,255 -t,0),2)
    
    cv2.imshow( "Result", drawing )
    cv2.waitKey()  
    cv2.destroyAllWindows()
    """
    for w in words:
      imhist[w] += 1

    return imhist