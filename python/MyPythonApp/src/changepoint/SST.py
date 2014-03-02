# -*- coding: utf-8 -*-
'''
Created on 2013/05/30

@author: n_shimada
'''
 
import sys
import numpy as np
import scipy as sp
from scipy.stats import norm
import statsmodels.tsa.arima_model as ar
import matplotlib.pyplot as plt
from numpy.linalg import svd
from scipy.sparse.linalg import eigs,eigsh  # eigsはnonsymmetric, eigshはsymmetric
from scipy.linalg import eig
from copy import deepcopy 
#import PIC
 
class change_finder(object):
    def __init__(self, term=70, window=5, order=(1, 1, 0)):
        self.term = term
        self.window = window
        self.l = term # 履歴行列を作るためにバンドルする時間数
#        self.order = order
#        print("term:", term, "window:", window, "order:", order)
 
    def main(self, X):
        req_length = self.term * 2 + self.window + np.round(self.window / 2) - 2
        if len(X) < req_length:
            sys.exit("ERROR! Data length is not enough.")
 
        #X = (X - np.mean(X)) / np.std(X)
        score = self.outlier(X)
        print("Done.")
 
        print "visualization"
        # visualize score
        self.visualize(score,X)
        plt.show()
        
        #return score
        return
 
    def outlier(self, X):
        count = len(X) - self.term
        trains = [X[t:(t + self.term)] for t in xrange(count)]
        
        sst_cnt = count - self.term
        score = []
        for t in xrange(self.l,sst_cnt):
            print "t=", t
            # 特異値分解
            score.append(self.get_H(trains, t))
        tmp = [0]*self.term*2
        score = tmp + score
        return score
        
    def get_H(self, X,t):
        k=5 # krylov空間のサイズ
        if k%2==1: r = int(k/2) +1
        else: r = int(k/2)
        td = t+self.term-self.l # テスト行列の先頭の位置
        H1 = np.array(X[t-self.l:t]) # 履歴行列
        law = np.dot(H1, H1.T)
        H2 = np.array(X[td:td+self.l]) # テスト行列
        U, s, V = svd(np.dot(H2,H2.T), full_matrices=True) # テスト行列の左特異ベクトルを取得
        index = np.where(s==np.max(s))
        mu = U[:,index].reshape((self.l,1))  # 最大左特異値ベクトル
        mu = self.normalize(mu)
        
        arnold = self.arnoldi(mu, law, k) # arnoldi法の基底行列
        np.savetxt('arnold.txt',arnold)
        """
        #mu = self.normalize(mu)
        vals, Q = eigs(H1 ,k=k, v0 = mu, which='LM') # k次元部分空間の正規直行基底Qを算出
        np.savetxt('Q_val.txt',Q.real)
        Q = Q.real # 実数部のみ取り出し
        """
        
        #alph, beta, q = self.lanczos(law, mu, k)
        #q = q.reshape((q.shape[1], q.shape[0]))
        """
        T = np.zeros((k,k))
        for i in xrange(k):
            for j in xrange(k):
                if i==j: T[i,j] = alph[i]
                elif i==j+1: T[i,j] = beta[i]
                elif i+1==j: T[i,j] = beta[j]
        """
        #print "alph",alph
        #print "beta",beta
        q=arnold
        T = np.dot(q.T, np.dot(law,q))
        np.savetxt('T_val.txt',T)
        
        """        
        U2, s2, V2 = svd(H1, full_matrices=True)
        cng_score = 1 - np.sum((np.dot(mu.T, U2[:,:r]))**2)
        """
        
        #T_eig_val, T_eig_vec = eig( T )
        T_eig_val, vec = eig( T )
        #vec = T_eig_vec /np.sum(T_eig_vec**2,axis=0)**0.5
        """       
        np.savetxt('T_eig_val.txt',T_eig_vec)
        cng_score = 1 - np.sum(T_eig_vec[0,:r]**2) # 変化度
        """
        np.savetxt('T_eig_val.txt',vec)
        cng_score = 1 - np.sum(vec[0,:r]**2) # 変化度
        return cng_score

    def normalize(self, v):
        return v/np.sum(v**2)**0.5

    def visualize(self,y1,y2):
        #plt.plot(x, y , color=clr)
        # 一画面を 2 行 1列の領域に分割し、1番めの領域に描画する
        x = np.arange(len(y1))
        plt.subplot(2,1,1)
        plt.title('y=score')
        plt.xlabel('t [step]')
        plt.ylabel('Out 1 [-]')
        plt.plot(x,y1,color = 'r')
        
        # 一画面を 2 行 1列の領域に分割し、2番めの領域に描画する
        x = np.arange(len(y2))
        plt.subplot(2,1,2)
        plt.xlabel('t [step]    ')
        plt.ylabel('Out 2 [-]')
        plt.plot(x,y2,color = 'b')


    def lanczos(self, law, mu, k):
        r = mu; beta0=1; q0=0
        alph = []; beta=[]; q=[]
        for s in xrange(k):
            if s==0:
                q.append(r/beta0)
                alph.append( np.dot(np.dot(np.array(q[s]).T, law), np.array(q[s])) )
                r = np.dot(law,np.array(q[s])) - alph[s-1]*np.array(q[s]) - beta0*q0
            else:
                q.append( r/beta[s-1] )
                alph.append( np.dot(np.dot(np.array(q[s]).T, law), np.array(q[s])) )
                r = np.dot(law,np.array(q[s])) - alph[s-1]*np.array(q[s]) - beta[s-1]*np.array(q[s-1])
            beta.append( np.dot(r.T,r)**0.5 )
        return alph, beta, np.array(q)
            
    def arnoldi(self, mu, law, k):
        h = np.zeros((k+1,k))
        v = np.zeros((len(law),k+1))
        v[:,0] = mu[:,0]
        for j in xrange(1,k+1):
            j_t = j-1
            for i in xrange(j): h[i,j_t] = np.dot( np.dot(law,v[:,j_t]), v[:,i] );print "j=",j; print h[i,j_t]
            v_hat = np.dot(law, v[:,j_t]) - np.array([h[i,j_t]*v[:,i] for i in xrange(j)]).sum()
            h[j_t+1,j_t] = np.sum(v_hat**2)**0.5
            v[:,j_t+1] = v_hat/h[j_t+1,j_t]
        return v[:,:k]

if __name__ == '__main__':
    cf = change_finder(term=100, window=10, order=(1, 10, 0)) #window is generally 5 to 10
    x = np.loadtxt('tunami01.txt')
    cf.main(x)