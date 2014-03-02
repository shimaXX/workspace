#!/usr/bin/python
# -*- coding: utf-8 -*-

import imtools
imlist = sorted(imtools.get_imlist('nail_book03'))

import pickle
import sift
import imagesearch

nbr_images = len(imlist)
featlist = [ imlist[i][:-3]+'sift' for i in range(nbr_images)]

# ボキャブラリを読み込む
with open('vocabulary.pkl', 'rb') as f:
  voc = pickle.load(f)

# Iedexerを生成する
indx = imagesearch.Indexer('aaa.db',voc)
indx.create_tables()

# 画像を順番にボキャブラリに射影してデータベースに挿入する
for i in range(nbr_images):
  locs,descr = sift.read_features_from_file(featlist[i])
  indx.add_to_index(imlist[i],descr)
#
# データベースをコミットする
indx.db_commit()
