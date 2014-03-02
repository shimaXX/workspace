#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import Image
from pylab import *

def ncut_graph_matrix(im,sigma_d=1e2,sigma_g=1e-2):
  """ 正規化カット用の行列を作る。パラメータは、ピクセル間の
      距離の重みと、類似度の重み """

  m,n = im.shape[:2]
  N = m*n

  # RGBもしくはグレースケールの特徴量ベクトルを作り
  # 正規化する
  if len(im.shape)==3:
    for i in range(3):
      im[:,:,i] = im[:,:,i] / im[:,:,i].max()
    vim = im.reshape((-1,3))
  else:
    im = im / im.max()
    vim = im.flatten()

  # 距離計算のためのx,y座標
  xx,yy = meshgrid(range(n),range(m))
  x,y = xx.flatten(),yy.flatten()

  # エッジ重み行列を作る
  W = zeros((N,N),'f')
  for i in range(N):
    for j in range(i,N):
      d = (x[i]-x[j])**2 + (y[i]-y[j])**2
      W[i,j] = W[j,i] = exp(-1.0*sum((vim[i]-vim[j])**2)/sigma_g) * \
                        exp(-d/sigma_d)

  return W

from scipy.cluster.vq import *

def cluster(S,k,ndim):
  """ 類似度行列からスペクトラルクラスタリングを行う """

  # 対称性をチェックする
  if sum(abs(S-S.T)) > 1e-10:
    print 'not symmetric'

  # ラプラシアン行列を作成する
  rowsum = sum(abs(S),axis=0)
  D = diag(1 / sqrt(rowsum + 1e-6))
  L = dot(D,dot(S,D))

  # Lの固有ベクトルを計算する
  U,sigma,V = linalg.svd(L)

  # 固有ベクトルの上位ndim個を列として並べて
  # 特徴量ベクトルを作成する
  features = array(V[:ndim]).T

  # k平均法
  features = whiten(features)
  centroids,distortion = kmeans(features,k)
  code,distance = vq(features,centroids)

  return code,V
