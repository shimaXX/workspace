#!/usr/bin/python
# -*- coding: utf-8 -*-

import os 
from PIL import *
from numpy import *
from pylab import *

def get_imlist(path):
  """ pathに指定されたフォルダのすべてのjpgファイル名のリストを返す """
  return [os.path.join(path,f) for f in os.listdir(path) if f.endswith('.jpg')]

def imresize(im,sz): 
  """ Resize an image array using PIL. """
  pil_im = Image.fromarray(uint8(im)) 
  return array(pil_im.resize(sz))

def histeq(im,nbr_bins=256):
  """ Histogram equalization of a grayscale image. """
  # 画像のヒストグラムを得る
  imhist,bins = histogram(im.flatten(),nbr_bins,normed=True)
  cdf = imhist.cumsum() # 累積分布関数
  cdf = 255 * cdf / cdf[-1] # 正規化

  # cdfを線形補間し、新しいピクセル値とする
  im2 = interp(im.flatten(),bins[:-1],cdf) 

  return im2.reshape(im.shape), cdf

def compute_average(imlist):
  """ 画像列の平均を求める """

  # 最初の画像を開き、浮動小数点数の配列に変換する
  averageim = array(Image.open(imlist[0]), 'f')

  for imname in imlist[1:]:
    try:
      averageim += array(Image.open(imname))
    except:
      print imname + '...skipped'
  averageim /= len(imlist)

  # 平均を uint8 に変換する
  return array(averageim, 'uint8')

def plot_2D_boundary(plot_range,points,decisionfcn,labels,values=[0]):
  """ plot_range：(xmin,xmax,ymin,ymax)、points：クラスの点のリスト、
      decisionfcn：評価関数、
      labels：各クラスについてdecisionfcnが返すラベルのリスト、
      values：表示する判別の輪郭のリスト """

  clist = ['b','r','g','k','m','y'] # クラスの描画色

  # グリッドを評価して判別関数の輪郭を描画する
  x = arange(plot_range[0],plot_range[1],.1)
  y = arange(plot_range[2],plot_range[3],.1)
  xx,yy = meshgrid(x,y)
  xxx,yyy = xx.flatten(),yy.flatten() # グリッドのx,y座標のリスト
  zz = array(decisionfcn(xxx,yyy))
  zz = zz.reshape(xx.shape)
  # valuesにそって輪郭を描画する
  contour(xx,yy,zz,values)

  # クラスごとに正しい点には*、間違った点には'o'を描画する
  for i in range(len(points)):
    d = decisionfcn(points[i][:,0],points[i][:,1])
    correct_ndx = labels[i]==d
    incorrect_ndx = labels[i]!=d
    plot(points[i][correct_ndx,0],points[i][correct_ndx,1],'*',color=clist[i])
    plot(points[i][incorrect_ndx,0],points[i][incorrect_ndx,1],'o',color=clist[i])

  axis('equal')
