#!/usr/bin/python
# -*- coding: utf-8 -*-

from pylab import *
from numpy import *
from pygraph.classes.digraph import digraph
from pygraph.algorithms.minmax import maximum_flow

import bayes

def build_bayes_graph(im,labels,sigma=1e2,kappa=2):
  """ 4近傍ピクセルからグラフを構成する。
    labelsにより前景か背景かを指定する
     (1:前景、-1:背景、0:それ以外）
    単純ベイズ分類器によりモデル化する """

  m,n = im.shape[:2]

  # RGBベクトル（1行に1ピクセル）にする
  vim = im.reshape((-1,3))

  # 前景と背景のRGB
  foreground = im[labels==1].reshape((-1,3))
  background = im[labels==-1].reshape((-1,3))
  train_data = [foreground,background]

  # 単純ベイズ分類器を学習させる
  bc = bayes.BayesClassifier()
  bc.train(train_data)

  # 全ピクセルの確率を取得する
  bc_lables,prob = bc.classify(vim)
  prob_fg = prob[0]
  prob_bg = prob[1]

  # m*n+2個のノードグラフを生成する
  gr = digraph()
  gr.add_nodes(range(m*n+2))

  source = m*n # 最後から2つ目のノードがソース
  sink = m*n+1 # 最後のノードがシンク

  # 正規化
  for i in range(vim.shape[0]):
    tmp = linalg.norm(vim[i])
    if tmp == 0: tmp =1e-6 
    vim[i] = vim[i] / tmp

  # 全ノードを順番にあたり、エッジを追加する
  for i in range(m*n):
    # ソースからのエッジを追加する
    gr.add_edge((source,i), wt=(prob_fg[i]/(prob_fg[i]+prob_bg[i])))

    # シンクへのエッジを追加する
    gr.add_edge((i,sink), wt=(prob_bg[i]/(prob_fg[i]+prob_bg[i])))

    # 近傍ピクセルへのエッジを追加する
    if i%n != 0: # 左に存在すれば
      edge_wt = kappa*exp(-1.0*sum((vim[i]-vim[i-1])**2)/sigma)
      gr.add_edge((i,i-1), wt=edge_wt)
    if (i+1)%n != 0: # 右に存在すれば
      edge_wt = kappa*exp(-1.0*sum((vim[i]-vim[i+1])**2)/sigma)
      gr.add_edge((i,i+1), wt=edge_wt)
    if i//n != 0: # 上に存在すれば
      edge_wt = kappa*exp(-1.0*sum((vim[i]-vim[i-n])**2)/sigma)
      gr.add_edge((i,i-n), wt=edge_wt)
    if i//n != m-1: # 下に存在すれば
      edge_wt = kappa*exp(-1.0*sum((vim[i]-vim[i+n])**2)/sigma)
      gr.add_edge((i,i+n), wt=edge_wt)

  return gr

def show_labeling(im,labels):
  """ 前景と背景の領域といっしょに画像を描画する。
    labels = 1 なら前景、-1 なら背景、0 はその他を表す """

  imshow(im)
  contour(labels,[-0.5,0.5])
  contourf(labels,[-1,-0.5],colors='b',alpha=0.25)
  contourf(labels,[0.5,1],colors='r',alpha=0.25)
  axis('off')

def cut_graph(gr,imsize):
  """ グラフgrの最大フローを求め、
    領域分割結果の2値ラベルを返す """

  m,n = imsize
  source = m*n # 最後から2つ目がソース
  sink = m*n+1 # 最後がシンク

  # グラフをカットする
  flows,cuts = maximum_flow(gr,source,sink)

  # グラフをラベル画像に変換する
  res = zeros(m*n)
  for pos,label in cuts.items()[:-2]: # ソースとシンクを除く
    res[pos] = label

  return res.reshape((m,n))
