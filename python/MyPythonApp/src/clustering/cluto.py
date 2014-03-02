# coding: utf-8
'''
Created on 2013/11/25

@author: RN-017
'''

import numpy as np
import scipy
import os
import math


class Cluto:
    def __init__(self):
        self.label_num = None
        self.labels = None
        self.tmp_labels = None

    def get_data(self,ifname):
        with open(ifname, 'r') as f:
            data = []
            labels = []
            for line in f:
                lis = line.strip().split('\t')
                vec = lis[:len(lis)-1]
                label = lis[len(lis)-1]
                data.append(vec)
                labels.append(label)
        return np.array(data, dtype=np.float), labels 
        
    def cluste(self,clustor, labels, k=3):
        self.label_num = [[] for _ in xrange(k)]
        self.labels = labels

        op_clustor = clustor
        op_labels = labels
        clustor_list = []
        label_list = []

        for itr in xrange(k-1):
                        
            clustors, labels = self.clust_data(op_clustor,op_labels)
            clustors, labels = self.trans_data(clustors, labels)
            
            # 新規に出来たクラスターたをリストに登録
            for i in xrange(len(clustors)):
                clustor_list.append(clustors[i])
                label_list.append(labels[i])
            
            # 目的の分割数まで達したらbreak
            if itr==k-2: break
            
            # 複雑度の高いクラスタを選択する
            select_idx = self.select_clustor(np.array(clustor_list))
            
            # 分割を行うクラスタを登録
            op_clustor = clustor_list[select_idx[0][0]]
            op_labels = label_list[select_idx[0][0]]
            
            # listから選択したクラスタを削除
            clustor_list.pop(select_idx[0][0])
            label_list.pop(select_idx[0][0])
            
        return np.array(clustor_list), label_list           
        
    # クラスタ内のデータを入れて、各クラスタの重心を返す
    def centroid(self,clustor):
        return self.composit(clustor)/len(clustor)
        
    # 各クラスタのベクトルを足しこむ
    def composit(self,clustor):
        com = None
        try:
            clustor.shape[1]
            com = np.sum(clustor,axis=0)
        except:
            com = clustor
        return np.array(com, dtype=np.float)
    
    # 全ベクトルの和のノルムの計算
    # 類似度の計算をしている
    def norm(self,clustors):
        comp = [ self.composit(clustor) for clustor in clustors ]
        return [ math.sqrt( sum(c**2) ) for c in comp]

    def norm_vector(self,vector):
        return math.sqrt( sum(vector**2) )

    # cosin類似度の計算
    def cos_sim(self,v1,v2):
        tmp = np.array( [ v1[i]*v2[i] for i in xrange(len(v1)) ] ,dtype=np.float)
        return sum(tmp)/self.norm_vector(v1)/self.norm_vector(v2)
    
    # 行列とベクトルのcosin類似度の計算
    def matrix_cos_sim(self,mat,vec):
        multmv = np.sum(mat*vec, axis=0)
        norm_m = np.sqrt( np.sum(mat**2,axis=0) )
        norm_v = self.norm_vector(vec)
        return multmv/norm_m/norm_v
    
    # クラスタの選択
    def select_clustor(self,clustors):
        dist_list = self.norm(clustors)
        idx = np.where(dist_list==np.max(dist_list))
        return idx
                
    # データの選択
    def get_sample_labels(self,clustor):
        return np.floor( np.random.uniform(size=2)*( len(clustor)-1 ) )

    # データの分割
    def clust_data(self, clustor, labels):
        samples = self.get_sample_labels(clustor)
        tmp_clus = [[],[]]
        tmp_clus[0].append(clustor[samples[0]].tolist())
        tmp_clus[1].append(clustor[samples[1]].tolist())
        
        tmp_labels = [[],[]]
        tmp_labels[0].append(labels[ int(samples[0]) ])
        tmp_labels[1].append(labels[ int(samples[1]) ])        
        
        new_clustors, new_labels = self.divide_data(tmp_clus, tmp_labels, clustor, labels, samples)
        return np.array(new_clustors), new_labels
    
    # dataの振り分け
    def divide_data(self,new_clus, new_labels, clustor, labels, samples):
        itr = 0
        for c in clustor:
            if itr in samples: itr+=1; continue
            cntr = [ self.centroid(np.array(new_clus[0])), self.centroid(np.array(new_clus[1])) ]
            if  self.cos_sim(cntr[0],c) > self.cos_sim(cntr[1],c):
                new_clus[0].append(c.tolist())
                new_labels[0].append(labels[itr])
            else:
                new_clus[1].append(c.tolist())
                new_labels[1].append(labels[itr])
            itr+=1
        new_clus[0]=np.array(new_clus[0])
        new_clus[1]=np.array(new_clus[1])
        return new_clus, new_labels
    
    # クラス間での移動
    def trans_data(self, new_clustors, new_labels):
        centers = [ self.centroid(clustor) for clustor in new_clustors ]
        for i in xrange(len(new_clustors)):
            itr = 0
            for i_e in new_clustors[i]:
                max_dist = 0
                opt_clus = 10000
                #cos_sim = []
                for j in xrange(len(new_clustors)):
                    #cos_sim.append( self.matrix_cos_sim(new_clustors[i], centers[j]) )                    
                    
                    dist = self.cos_sim(centers[j], i_e)
                    if max_dist < dist:
                        max_dist = dist
                        opt_clus = j

                if opt_clus!=i:
                    ## 新しいクラスに追加
                    # 新しいクラスタにデータを追加
                    tmp = new_clustors[opt_clus].tolist()
                    tmp.append(i_e.tolist())
                    new_clustors[opt_clus] = np.array(tmp)
                    
                    # 新しいクラスタにラベルデータを追加
                    tmp = new_labels[opt_clus]
                    tmp.append(new_labels[i][itr])
                    new_labels[opt_clus] = tmp
                    
                    ## 古いクラスから削除
                    # 古いクラスタからデータを削除
                    tmp = new_clustors[i].tolist()
                    tmp.remove(i_e.tolist())
                    new_clustors[i] = np.array(tmp)

                    tmp = new_labels[i]
                    tmp.pop(itr)
                    new_labels[i] = tmp
                else:
                    itr += 1
                    
        return new_clustors, new_labels
    
    def combine_matrix(self,m1,m2):
        res = []
        res.append(m1)
        for m in m2:
            res.append(m)
    
        return np.array(res)
    
if __name__=='__main__':
    fname = 'c:/workspace/python/MyPython/works/input/testdata.txt'
    ofname = 'c:/workspace/python/MyPython/works/output/test_outp.txt'
    
    # 分割を行う
    cluto = Cluto()

    f_clustor, label = cluto.get_data(fname)
    clustor = np.array(f_clustor, dtype=np.float)
    
    c ,labels = cluto.cluste(clustor, label, k=3)
    
    print c
    print labels