#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import *

class BayesClassifier(object):

  def __init__(self):
    """ 初期化する """

    self.labels = [] # クラスのラベル
    self.mean = [] # クラスの平均
    self.var = [] # クラスの分散
    self.n = 0 # クラスの数

  def train(self,data,labels=None):
    """ data（n*dimの配列のリスト）を用いて学習する。
        labelsはオプションで、デフォルトは 0...n-1 """

    if labels==None:
      labels = range(len(data))
    self.labels = labels
    self.n = len(labels)

    for c in data:
      self.mean.append(mean(c,axis=0))
      self.var.append(var(c,axis=0))

  def classify(self,points):
    """ 各クラスの確率を計算して最も確率の高いラベルを
        返すことでpointsを分類する。"""

    # 各クラスの確率を計算する
    est_prob = array([gauss(m,v,points) for m,v in zip(self.mean,self.var)])

    # 最も確率の高いインデクス番号を求め、クラスのラベルを返す
    ndx = est_prob.argmax(axis=0)
    est_labels = array([self.labels[n] for n in ndx])

    return est_labels, est_prob

def gauss(m,v,x):
  """ 独立した平均m分散vの点を、xの行として持つ
      d次元のガウス分布を評価する """

  if len(x.shape)==1:
    n,d = 1,x.shape[0]
  else:
    n,d = x.shape

  # 共分散行列を求め、xから平均を引く
  S = diag(1/v)
  x = x-m
  # 確率の積
  y = exp(-0.5*diag(dot(x,dot(S,x.T))))

  # 正規化して返す
  return y * (2*pi)**(-d/2.0) / ( sqrt(prod(v)) + 1e-6)
