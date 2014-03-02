#!/usr/bin/python
# -*- coding: utf-8 -*-

import imtools
imlist = sorted(imtools.get_imlist('test'))
#imlist = imlist[:100]  # for small memory

import pickle
import vocabulary

nbr_images = len(imlist)
featlist = [ imlist[i][:-3]+'sift' for i in range(nbr_images) ]

voc = vocabulary.Vocabulary('nail')
voc.train(featlist,500,10) # 第2引数がクラスタ数、第3引数が間引く数

# ボキャブラリを保存する
with open('vocabulary.pkl', 'wb') as f:
  pickle.dump(voc,f)
print 'vocabulary is:', voc.name, voc.nbr_words