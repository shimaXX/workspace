#!/usr/bin/python
# -*- coding: utf-8 -*-

import pickle
import os

#!/usr/bin/python
# -*- coding: utf-8 -*-

from PIL import Image
from pylab import *
import imtools
import pickle
from scipy.cluster.vq import *
import numpy as np
import scipy as sp
import cv2


with open('panoramio_matchscores.pkl','r') as f:
  nbr_images = pickle.load(f)
  imlist = pickle.load(f)
  matchscores = pickle.load(f)

n = len(imlist)

# 距離行列を計算する
S = matchscores
S = 1 / (S + 1e-6)

# ラプラシアン行列を作成する
rowsum = sum(S,axis=0)
D = diag(1 / sqrt(rowsum))
I = identity(n)
L = I - dot(D,dot(S,D))

# Lの固有ベクトルを計算する
U,sigma,V = linalg.svd(L)

k = 10
# 最初のk個の固有ベクトルを列として並べて
# 特徴量ベクトルを作成する
features = array(V[:k]).T

# k-means
features = whiten(features)
print features
centroids,distortion = kmeans(features,k)
code,distance = vq(features,centroids)

# クラスタを描画する
for c in range(k):
  ind = where(code==c)[0]
  figure()
  for i in xrange(minimum(len(ind),39)):
    im = Image.open(imlist[ind[i]])
    subplot(4,10,i+1)
    gray()
    imshow(array(im))
    axis('equal')
    axis('off')
show()
