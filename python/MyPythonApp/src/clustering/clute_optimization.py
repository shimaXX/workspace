# coding: utf-8
"""
全ての分布との距離を加味した最適化を行うこと → rev3で実施（数値はそこまで良くならない）
交換が起きた時にindexがズレる件の修正 → rev2で実施（数値はそこまで良くならない）
いろいろ非効率。効率的にリファクタリング。
ベースはrev2とする。
各クラスタの正規性の確認。 → 歪度が0、尖度が3からどれだけずれているかで評価？ 
（http://haku1569.seesaa.net/article/399462666.html）
→これだと距離の尺度が変わってしまうので、標準正規分布に補正して標準正規分布との距離で判断する。
→結局あまり変わらない。。
"""

import numpy as np
from numpy.random import randn
import scipy
import os
import math
import matplotlib
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA 
import copy

from mutual_information import mic

class Cluto:
    def __init__(self):
        self.label_num = None
        self.labels = None
        self.tmp_labels = None
        #self.standard_norm_dist = randn()

    def get_file_data(self,ifname):
        with open(ifname, 'r') as f:
            data = []
            labels = []
            for line in f:
                lis = line.strip().split('\t')
                vec = lis[:len(lis)-1]
                label = lis[-1]
                data.append(vec)
                labels.append(label)
        data = np.array(data, dtype=np.float64)
        decomposer = PCA(1)
        p_vector = decomposer.fit(data)
        total_value = data*p_vector
        return data , labels, total_value

    def get_data(self,np_data):                
        data = np_data[:,1:]
        labels = np_data[:,0]
        
        decomposer = PCA(1)
        p_vector = decomposer.fit(data).components_[0]
        total_value = np.array([ np.sum(d*p_vector) for d in data], dtype=np.float64)
        return data , labels, total_value
    
    def init_clustors(self,index_list,clustor,label,clustor_number):
        new_clustors = []
        new_labels = []
        
        index_list = np.array(index_list, dtype=np.int)
        
        for clustor_idx in xrange(clustor_number):
            idx = np.where(index_list==clustor_idx)
            new_clustors.append(clustor[idx])
            new_labels.append(label[idx].tolist())
        return np.array(new_clustors), new_labels
    
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
        if isinstance(v1,list):
            tmp = np.array( [ v1[i]*v2[i] for i in xrange(len(v1)) ] ,dtype=np.float)
            return sum(tmp)/self.norm_vector(v1)/self.norm_vector(v2)
        else:
            tmp = v1*v2
            print v2
            return tmp/math.sqrt(v1**2)/math.sqrt(v2**2)
    
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
            #if  self.cos_sim(cntr[0],c) > self.cos_sim(cntr[1],c):
            #if self.dist(np.mean(cntr[0]), c) > self.dist(np.mean(cntr[1]),c):
            if len(new_clus[0]) <= len(new_clus[1]):
                new_clus[0].append(c.tolist())
                new_labels[0].append(labels[itr])
            else:
                new_clus[1].append(c.tolist())
                print len(labels)
                print len(clustor)
                print "itr", itr
                new_labels[1].append(labels[itr])
            itr+=1
        new_clus[0]=np.array(new_clus[0])
        new_clus[1]=np.array(new_clus[1])
        return new_clus, new_labels
    
    def dist(self, avg, target):
        return math.sqrt( (avg-target)**2 )
    
    """
    # クラス間での移動
    def trans_data(self, new_clustors, new_labels):
        centers = [ self.centroid(clustor) for clustor in new_clustors ]
        for i in xrange(len(new_clustors)):
            itr = 0
            for i_e in new_clustors[i]:
                max_dist = 0
                opt_clus = 10000
                #cos_sim = []
                for j in xrange(len(new_clustors)): #距離は当該クラス以外のクラスとの総和
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
    """
    
    # クラス間での移動
    def trans_data(self,clustors, labels, trans_size=3):
        clustor_number = len(clustors)
        for clustor_idx in xrange(clustor_number): # original cluster outer loop
            for idx_label, student in enumerate(clustors[clustor_idx]): # original cluster inner loop
                for change_clustor_idx in xrange(clustor_idx+1,clustor_number): # competitor cluster outer loop
                    this_chanp_data_list = []
                    change_chanp_data_list = []
                    
                    target_idx = np.random.randint(0, len(clustors[change_clustor_idx])-1, size=trans_size)
                    
                    tmp_orig = student
                    this_clustor_data = clustors[clustor_idx].copy()
                    this_tmp_data = this_clustor_data.copy().tolist()
                    change_clustor_data = clustors[change_clustor_idx].copy()
                    
                    # mutual information of not transfer data
                    dist_orig = mic(this_clustor_data, change_clustor_data)
                    
                    this_tmp_data.pop(idx_label)
                    min_dist = dist_orig
                    for idx in target_idx: # competitor cluster inner loop(sampled)
                        this_temporary = copy.deepcopy(this_tmp_data)
                        change_tmp_data = change_clustor_data.copy().tolist()
                        tmp_change = change_clustor_data[idx]
                        change_tmp_data.pop(change_clustor_idx)
                        change_tmp_data.append(tmp_orig)
                        this_temporary.append(tmp_change)
                        dist_change = mic(this_temporary, change_tmp_data)
                        
                        if min_dist > dist_change: # 全てのクラスとの距離の和を計算する必要があるかも...
                            """ maxのやつを保存して最後に更新作業を行うように後で書き換えること """
                            this_chanp_data_list = this_temporary
                            change_chanp_data_list = change_tmp_data
                            
                            orig_tmp_label = labels[clustor_idx][idx_label]
                            #print labels[change_clustor_idx]
                            #print "len", len(labels[change_clustor_idx])
                            #print idx
                            change_tmp_label = labels[change_clustor_idx][idx]
                            
                            labels[clustor_idx].pop(idx_label)
                            labels[clustor_idx].append(change_tmp_label)
                            
                            labels[change_clustor_idx].pop(idx)
                            labels[change_clustor_idx].append(orig_tmp_label)
                            clustors[clustor_idx] = np.array(this_chanp_data_list,dtype=np.float64)
                            clustors[change_clustor_idx] = np.array(change_chanp_data_list,dtype=np.float64)
                            
                            break
        return np.array(clustors), labels

    def calculate_cost(self, centers, indiv_data):
        dist = 0
        for j in xrange(len(centers)):
            dist += 1 - self.cos_sim(centers[j], indiv_data)  
    
    def combine_matrix(self,m1,m2):
        res = []
        res.append(m1)
        for m in m2:
            res.append(m)
        return np.array(res)
    
    """     
    def caluc_mutual(self, y,x):
        y=np.log(1+y); x=np.log(1+x)
        res = y-x-np.mean(y-x)
        res_var = np.var(res)
        x_var = np.var(x)
        return 0.5*np.log(1+x_var/res_var, 2)
    """
    
    def black_list_process(self, black_list, clustors, labels):
        n_total_clust = len(labels)
        for n_clust in xrange(n_total_clust): # original outer cluster
            for idx, student in enumerate(labels[n_clust]): # original inner cluster
                if student in black_list.keys():
                    better_clust = self.calculate_min_enegy_cluster(n_clust, n_total_clust, student)
                    if better_clust is None: continue
                    clustors, labels = self.calculate_better_cluster(clustors, labels, idx, n_clust, better_clust, student, black_list[student])
                else:
                    continue
        return clustors, labels

    def calculate_better_cluster(self, clustors, labels, idx_label, clustor_idx, change_clustor_idx, student, black_list_values):
        """
        n_clust -> clustor_idx
        idx -> idx_label
        """
        this_chanp_data_list = []
        change_chanp_data_list = []
                   
        tmp_orig = student
        this_clustor_data = clustors[clustor_idx].copy()
        this_tmp_data = this_clustor_data.copy().tolist()
        change_clustor_data = clustors[change_clustor_idx].copy()
        
        # mutual information of not transfer data
        dist_orig = mic(this_clustor_data, change_clustor_data)
        
        this_tmp_data.pop(idx_label)
        min_dist = dist_orig
        for idx in xrange(len(clustors[change_clustor_idx])): # competitor cluster inner loop(sampled)
            #if clustors[change_clustor_idx][idx] in black_list_values: continue
            this_temporary = copy.deepcopy(this_tmp_data)
            change_tmp_data = change_clustor_data.copy().tolist()
            tmp_change = change_clustor_data[idx]
            change_tmp_data.pop(change_clustor_idx)
            change_tmp_data.append(tmp_orig)
            this_temporary.append(tmp_change)
            dist_change = mic(this_temporary, change_tmp_data)
            
            if min_dist > dist_change: # 全てのクラスとの距離の和を計算する必要があるかも...
                """ maxのやつを保存して最後に更新作業を行うように後で書き換えること """
                this_chanp_data_list = this_temporary
                change_chanp_data_list = change_tmp_data
                
                orig_tmp_label = labels[clustor_idx][idx_label]
                #print labels[change_clustor_idx]
                #print "len", len(labels[change_clustor_idx])
                #print idx
                change_tmp_label = labels[change_clustor_idx][idx]
                
                labels[clustor_idx].pop(idx_label)
                labels[clustor_idx].append(change_tmp_label)
                
                labels[change_clustor_idx].pop(idx)
                labels[change_clustor_idx].append(orig_tmp_label)
                clustors[clustor_idx] = np.array(this_chanp_data_list,dtype=np.float64)
                clustors[change_clustor_idx] = np.array(change_chanp_data_list,dtype=np.float64)
                
                break
        return np.array(clustors), labels
                
    def calculate_min_enegy_cluster(self,n_clust, n_total_clust, student):
        i_set = set(labels[n_clust]).intersection(set(black_list[student])) #s と t共通に含まれる要素を持った新しいsetを作成
        min_set = len(i_set)
        min_clust = None # n_clust
        for n_comp_clustor in xrange(n_clust, n_total_clust):
            i_cmp_set = set(labels[n_comp_clustor]).intersection(set(black_list[student]))
            if len(i_cmp_set) < min_set:
                min_set = len(i_cmp_set)
                min_clust = n_comp_clustor
        return min_clust
        
    
if __name__=='__main__':
    #fname = 'c:/workspace/python/MyPython/works/input/testdata.txt'
    ofname = os.getcwd()+'/test_outp.csv'
    
    # 分割を行う
    cluto = Cluto()

    np.random.seed(55) # will fix seed for random 
    
    subject_number = 5
    student_number = 183
    impartial_class_number = 40
    black_list = {1:[3,4,5,120,130,12,11,10], 2:[10,7]}

    data = np.array([[i]+[np.random.randint(1,100) for _ in xrange(subject_number) ] for i in xrange(student_number)]
                    ,dtype=np.float64)
    f_clustor, label, total_value = cluto.get_data(data)
    print total_value
    
    for i in xrange(1,len(data[0,:])):
        data[:,i] = np.float64( data[:,i]-np.mean(data[:,i]) )/np.std(data[:,i])

    clustor = np.array(total_value, dtype=np.float)
    
    #c ,labels = cluto.cluste(clustor, label, k=5)
    
    f_clustor_number = float(student_number)/impartial_class_number
    clustor_number = int(f_clustor_number)+1 if f_clustor_number!=0 else f_clustor_number 
    i_avg_student_number = int(float(student_number)/clustor_number)
    
    index_list = [i for i in xrange(clustor_number-1) for _ in xrange(i_avg_student_number)]
    index_list += [clustor_number-1]*(student_number-i_avg_student_number*(clustor_number-1))

    clustors, labels = cluto.init_clustors(index_list, clustor, label, clustor_number)
    
    for _ in xrange(3):
        transed_clustors, transed_labels = cluto.trans_data(clustors, labels,trans_size=3)
        print transed_labels
        
        final_clustors, final_labels = cluto.black_list_process(black_list, clustors, labels)
        print final_labels    
    
        print labels
        print np.sum(final_clustors[0])
        print np.sum(final_clustors[1])
        print np.sum(final_clustors[2])
        print np.sum(final_clustors[3])
        print np.sum(final_clustors[4])