#-*- coding: utf8 -*-
'''
Created on 2012/10/25

@author: n_shimada
'''


from __future__ import with_statement
import math

#FileDir = 'C:/HadoopPig/workspace/HadoopPig/works/output/EvaVerbCount/Part-r-00000'
DistFileDir = 'C:/HadoopPig/workspace/HadoopPig/works/output/Mining/Ci-LaboTranseVerb0123/part-r-00000'
SeqFileDir = 'C:/HadoopPig/workspace/HadoopPig/works/output/Mining/Ci-LaboSessionBuy0123/part-r-00000'

#それぞれのアクティビティの距離を求める関数
#アクティビティの距離はbuy発生時のパスだけでなく、平時のパスも含めた距離を算出する
#本来的なverb間の距離を測るためである（cartとbuyの距離は本来遠いetc）
def getDistData():
    distData = {}
    verbs = []
    summation = {}

    with open(DistFileDir) as f:
        for line in f:
            cols = line.strip().split()
            lastVerb = cols[0]
            postVerb = cols[1]
            num = int(cols[2])
        
            if lastVerb not in verbs:
                verbs.append(str(lastVerb))
        
            if postVerb not in verbs:
                verbs.append(str(postVerb))
            
            if lastVerb not in summation:
                summation[lastVerb] = 0 
        
            if lastVerb not in distData:
                distData[lastVerb] = {}
                      
            distData[lastVerb][postVerb] = num

            summation[lastVerb] += num

    for lVerb in verbs:
        if lVerb in distData and lVerb in summation:        
            for pVerb in verbs:
                if pVerb in distData[lVerb]:
                    distData[lVerb][pVerb] = distLog(distData[lVerb][pVerb], summation[lVerb])
                    
    return distData,verbs

#単純に割合で隣接ノードとの距離を算出する関数
def distProportion(x,y):
    dist = 1.0-(float)(x)/y
    return dist
    
#底が7のlogに割合を入力することにより隣接ノードとの距離を算出する関数
def distLog(x,y):
    dist = -1*math.log((float)(x)/y,7)
    return dist
    
#buyに至った経路を取得
def getSequence():
    seq = []
    with open(SeqFileDir) as f:
        for line in f:
            cols = line.strip('{()}\n').split(',')
            cols = reverseList(cols)
            if(len(cols) <= 1): continue  
            seq.append(cols)
    return seq

#Listの中身を反転させる関数
def reverseList(l):
    cols = []
    for i in range(len(l)):
        cols.insert(0,l[i]) 
        if(l[i] == "buy"): break
    return cols

#buyからの累積距離を計算
def calculateAccumulateDist(distData, seq):
    accuDist = []
    for row in seq:
        lis = []
        dist = 0
        
        for i in range(len(row)-1):
            if(row[i+1] not in distData or row[i] not in distData[row[i+1]]):
                dist += 1
                lis.append(dist)
            elif(row[i+1] in distData and row[i] in distData[row[i+1]]):
                dist += distData[row[i+1]][row[i]]
                lis.append(dist)
        accuDist.append(lis)
    
    return accuDist

#標準偏差の計算
def calcurateSigma(accuDist):
    squareSumDist = 0.0
    cnt = 0
    for row in accuDist:
        #末端までの距離の偏差平方和の算出
        squareSumDist += pow(row[len(row) -1],2)
        cnt += 1
    
    #標準偏差の算出
    sigma = (squareSumDist/cnt)**0.5    
    return sigma

def calcurateWeight(verbs,seq,accuDist,sigma):
    weight = {}
    totalWeight = {}
    sumWeight = {}
    finalWeight = {}
    idx=0
    for row in accuDist:
        weight[idx]={}
        totalWeight[idx]=0
        
        for i in range(len(row)):
            if seq[idx][i+1] not in weight[idx]:
                w = gaussian(row[i],sigma)
                weight[idx][seq[idx][i+1]] = w
                totalWeight[idx] += w
            else:
                w = gaussian(row[i],sigma)
                weight[idx][seq[idx][i+1]] += w
                totalWeight[idx] += w
            
        for k,v in weight[idx].items():
            #当該パスにおける総weightで割ることで、CVに対する貢献度をトータルで1にする
            weight[idx][k] = (float)(v)/totalWeight[idx]
            if k not in sumWeight:
                sumWeight[k] = weight[idx][k]
            else: sumWeight[k] += weight[idx][k]
        idx += 1
        
    for k,v in sumWeight.items():
        finalWeight[k] = (float)(v)/(len(weight))

    outfp = open('C:/Users/n_shimada/Desktop/ContributionRateForCi-Labo.txt','w')
    for rname in verbs:
        nums = [str(finalWeight.get(rname, 0))]
        outfp.write(rname +","+ (",".join(nums))+"\n")

    outfp.close()

#ガウス分布を用いたweightの計算
def gaussian(dist,sigma=2.0):
    return math.e**(-(dist**2)/(2*(sigma**2)))