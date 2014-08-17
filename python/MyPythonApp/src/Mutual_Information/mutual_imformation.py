#coding:utf-8

import codecs
import math
import sys
from collections import defaultdict
import numpy as np
import os, io

# feature_selection.py
class MI:
    N11 = None  # N11[word] -> wordを含むtargetの文書数(wordは番組録画、targetはclick)
    N10 = None  # N10[word] -> wordを含むtarget以外の文書数
    N01 = None  # N01[word] -> wordを含まないtargetの文書数
    N00 = None  # N00[word] -> wordを含まないtarget以外の文書数
    Np = 0.0  # targetの文書数
    Nn = 0.0  # target以外の文書す

    def init_vec(self, size):
        self.N11 = np.zeros(size)  # N11[word] -> wordを含むtargetの文書数(wordは番組録画、targetはclick)
        self.N10 = np.zeros(size)  # N10[word] -> wordを含むtarget以外の文書数
        self.N01 = np.zeros(size)  # N01[word] -> wordを含まないtargetの文書数
        self.N00 = np.zeros(size)  # N00[word] -> wordを含まないtarget以外の文書数        
    
    def mutual_information(self, target, data):
        """カテゴリtargetにおける相互情報量が高い上位k件の単語を返す"""
        
        # N11とN10をカウント
        if data[0] == target:
            self.Np += 1
            self.N11 += np.array(data[1:], dtype=np.int32)
        elif data[0] != target:
            self.Nn += 1
            self.N10 += np.array(data[1:], dtype=np.int32)

    def get_score(self):        
        # N01とN00は簡単に求められる
        self.N01 = self.Np - self.N11
        self.N00 = self.Nn - self.N10
    
        # 総文書数
        N = self.Np + self.Nn
        
        # 各単語の相互情報量を計算
        # 相互情報量の定義の各項を計算
        temp1 = self.N11/N * np.log2((N*self.N11)/((self.N10+self.N11)*(self.N01+self.N11)))
        temp2 = self.N01/N * np.log2((N*self.N01)/((self.N00+self.N01)*(self.N01+self.N11)))
        temp3 = self.N10/N * np.log2((N*self.N10)/((self.N10+self.N11)*(self.N00+self.N10)))
        temp4 = self.N00/N * np.log2((N*self.N00)/((self.N00+self.N01)*(self.N00+self.N10)))
        score = temp1 + temp2 + temp3 + temp4
        
        # 相互情報量の降順にソートして上位k個を返す
        return score

if __name__ == "__main__":
    # 訓練データをロード
    name = 'vellfire spade aqua'.strip().split(' ')
    basepath = os.getcwd()+'/output/'
    target = "1"
    
    for n in name:
        s = n+'_data.csv'
#        s = n+'_raw.csv'
        fname = os.path.join(basepath, s)
        s = n+'_MI_thresh.txt'
#        s = n+'_MI.txt'
        ofname = os.path.join(basepath, s)
        mi = MI()
        itr = 0
#        of = io.open(ofname, 'w')
        with open(fname, "r",10000) as fp:
            for line in fp:
                if itr==0:
                    data = line.strip().split(',')
                    size = len(data[1:])
                    mi.init_vec(size)
                    itr +=1
                    continue
                else:
                    data = line.strip().split(',')
                # 相互情報量を用いて特徴選択
                score = mi.mutual_information(target,data)
            score = mi.get_score()
            print n
            print "[%s]" % target
            score[score!=score]=0
            print score
#            s = [unicode(str(n)) for n in score]
#            sr = ','.join(s)
            np.savetxt(ofname, score)