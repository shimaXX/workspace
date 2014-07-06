#-*- coding: utf-8 -*-
'''
Created on 2012/11/18

@author: nahki
'''
import attributionAnaly

dist,nodes = attributionAnaly.getDistData()

print(dist)

seq = attributionAnaly.getSequence()

accuDist = attributionAnaly.calculateAccumulateDist(dist,seq)

print(accuDist)

sigma = attributionAnaly.calcurateSigma(accuDist)

print(sigma)

sigma = 2.0
attributionAnaly.calcurateWeight(nodes,seq,accuDist,sigma)